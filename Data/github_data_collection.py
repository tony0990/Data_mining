
#GitHub Repository Data Collection Script


import os
import time
import json
import requests
import pandas as pd



# CONFIGURATION

GITHUB_TOKEN = "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"


SEARCH_QUERIES = [
   
   
    "machine-learning",
    "deep-learning",
    "reinforcement-learning",
    "generative-ai",
    "natural-language-processing",
    "computer-vision",
    "data-science",
    "neural-network",
    "llm",
    "pytorch",
    "tensorflow",

   
    "web-development",
    "rest-api",
    "graphql",
    "microservices",
    "docker",
    "cloud-computing",
    "serverless",
    "authentication",
    "database",
    "fastapi",

    
    "mobile-app",
    "react",
    "flutter",
    "android",
    "ios",

    
    "devops",
    "ci-cd",
    "cybersecurity",
    "testing",
    "open-source",
    "automation",
    "monitoring",

   
    "blockchain",
    "game-development",
    "iot",
    "robotics",
    "data-visualization",
    "mlops",
    "data-engineering",
    "scraping",
    "augmented-reality",
    "embedded-systems",
    "cryptocurrency",
    "linux",
]

REPOS_PER_QUERY = 100       
MIN_STARS       = 50       
OUTPUT_DIR      = "data"   



HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

BASE_URL = "https://api.github.com/search/repositories"


def fetch_repositories(query: str, per_page: int = 50, max_repos: int = 50) -> list[dict]:
   
    #Fetch repositories from the GitHub 
    
    repos = []
    page = 1
    params = {
        "q":        f"topic:{query} stars:>={MIN_STARS}",
        "sort":     "stars",
        "order":    "desc",
        "per_page": min(per_page, 100),
        "page":     page,
    }

    print(f"  Searching: {query} ...", end="", flush=True)

    while len(repos) < max_repos:
        params["page"] = page
        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code == 403:
            # Rate limit hit 
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait_secs  = max(reset_time - int(time.time()), 10)
            print(f"\n  Rate limit reached. Waiting {wait_secs}s...", flush=True)
            time.sleep(wait_secs)
            continue

        if response.status_code != 200:
            print(f"\n  ERROR {response.status_code}: {response.json().get('message', '')}")
            break

        data  = response.json()
        items = data.get("items", [])
        if not items:
            break

        repos.extend(items)
        page += 1

        
        time.sleep(1)

        if len(repos) >= max_repos or len(items) < params["per_page"]:
            break

    print(f" {min(len(repos), max_repos)} repos collected.")
    return repos[:max_repos]


def extract_fields(repo: dict, topic_label: str) -> dict:
    
    #Extract and flatten the relevant fields
    
    return {
        "name":         repo.get("name", ""),
        "full_name":    repo.get("full_name", ""),
        "description":  (repo.get("description") or "").strip(),
        "language":     repo.get("language", "Unknown"),
        "stars":        repo.get("stargazers_count", 0),
        "forks":        repo.get("forks_count", 0),
        "watchers":     repo.get("watchers_count", 0),
        "topics":       repo.get("topics", []),           
        "topics_str":   "|".join(repo.get("topics", [])), # separated for CSV
        "search_query": topic_label,                      # which query found this repo
        
    }


def collect_all(queries: list[str], repos_per_query: int) -> list[dict]:
    
    all_repos  = []
    seen_names = set()

    for query in queries:
        raw_repos = fetch_repositories(query, per_page=repos_per_query, max_repos=repos_per_query)
        for repo in raw_repos:
            full_name = repo.get("full_name", "")
            if full_name not in seen_names:           
                seen_names.add(full_name)
                all_repos.append(extract_fields(repo, query))

    return all_repos



def save_results(records: list[dict], output_dir: str) -> None:
    
    os.makedirs(output_dir, exist_ok=True)

    # Saving as JSON 
    json_path = os.path.join(output_dir, f"github_repos.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"\n  JSON saved → {json_path}")

    # Saving as CSV 
    df = pd.DataFrame(records)
 
   
    df_csv = df.drop(columns=["topics"], errors="ignore")
    csv_path = os.path.join(output_dir, f"github_repos.csv")
    df_csv.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"  CSV saved  → {csv_path}")

    return df


def print_summary(df: pd.DataFrame) -> None:
    #Summary of the collected data.
    print("\n" + "=" * 50)
    print("DATASET SUMMARY")
    print("=" * 50)
    print(f"  Total repositories : {len(df)}")
    print(f"  Unique languages   : {df['language'].nunique()}")
    print(f"  Stars  — min: {df['stars'].min():,}  max: {df['stars'].max():,}  mean: {df['stars'].mean():,.0f}")
    print(f"  Forks  — min: {df['forks'].min():,}  max: {df['forks'].max():,}  mean: {df['forks'].mean():,.0f}")
    print(f"\n  Top 10 languages:")
    for lang, count in df["language"].value_counts().head(10).items():
        print(f"    {lang:<20} {count}")
    print(f"\n  Repos per search query:")
    for query, count in df["search_query"].value_counts().items():
        print(f"    {query:<30} {count}")
    print("=" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("GitHub Repository Data Collector")

    print("=" * 50)

    if GITHUB_TOKEN == "YOUR_TOKEN_HERE":
        print("\nWARNING: No GitHub token set!")
        print("Unauthenticated requests are limited to 10 req/min.")
        print("Set GITHUB_TOKEN environment variable or edit the script.\n")

    print(f"\nCollecting up to {REPOS_PER_QUERY} repos for each of {len(SEARCH_QUERIES)} queries...\n")
    records = collect_all(SEARCH_QUERIES, REPOS_PER_QUERY)

    print(f"\nTotal unique repos collected: {len(records)}")
    df = save_results(records, OUTPUT_DIR)
    print_summary(df)

    print("\nDone!")