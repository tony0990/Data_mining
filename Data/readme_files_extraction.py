

import os
import time
import json
import base64
import requests
import pandas as pd
from glob import glob

GITHUB_TOKEN = "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"

DATA_DIR     = "data"              
README_LIMIT = 2000               
SLEEP_TIME   = 0.5                 
# ─────────────────────────────────────────────

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}



def load_latest_csv(data_dir: str) -> tuple[pd.DataFrame, str]:
    
    pattern = os.path.join(data_dir, "github_repos.csv")
    files   = [f for f in glob(pattern) if "with_readme" not in f]

    if not files:
        raise FileNotFoundError(
            f"No CSV file found in '{data_dir}/'. "
            "Please run github_data_collection.py first."
        )

    latest = max(files, key=os.path.getmtime)
    print(f"  Loading: {latest}")
    df = pd.read_csv(latest, encoding="utf-8")
    return df, latest



def fetch_readme(full_name: str) -> str:
    
    try:
        url      = f"https://api.github.com/repos/{full_name}/readme"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            content = response.json().get("content", "")
            decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
            return decoded[:README_LIMIT].strip()

        elif response.status_code == 403:
            # Rate limit hit — wait and retry once
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait_secs  = max(reset_time - int(time.time()), 10)
            print(f"\n  Rate limit hit. Waiting {wait_secs}s...", flush=True)
            time.sleep(wait_secs)
            # Retry once after waiting
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                content = response.json().get("content", "")
                decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                return decoded[:README_LIMIT].strip()

    except Exception as e:
        print(f"\n  Warning: could not fetch README for {full_name} — {e}")

    return ""



def fetch_all_readmes(df: pd.DataFrame) -> pd.DataFrame:
   
    total = len(df)

    # Add empty readme column if it doesn't exist yet
    if "readme" not in df.columns:
        df["readme"] = ""

    # Only fetch for rows where readme is empty
    missing_mask  = df["readme"].isna() | (df["readme"].str.strip() == "")
    missing_count = missing_mask.sum()

    print(f"\n  Total repos      : {total}")
    print(f"  READMEs to fetch : {missing_count}")

    if missing_count == 0:
        print("  All READMEs already present — nothing to fetch.")
        return df

    print(f"\n  Fetching... (estimated time: {missing_count * SLEEP_TIME / 60:.1f} mins)\n")

    fetched = 0
    failed  = 0

    for idx, row in df[missing_mask].iterrows():
        full_name = row.get("full_name", "")
        if not full_name:
            continue

        readme = fetch_readme(full_name)
        df.at[idx, "readme"] = readme

        if readme:
            fetched += 1
        else:
            failed += 1

        time.sleep(SLEEP_TIME)

        # Progress update every 50 repos
        done = fetched + failed
        if done % 50 == 0 or done == missing_count:
            print(f"  Progress: {done}/{missing_count} — fetched: {fetched}, not found: {failed}")

    return df



def save_results(df: pd.DataFrame, data_dir: str) -> None:
    
    os.makedirs(data_dir, exist_ok=True)
    

    # CSV
    csv_path = os.path.join(data_dir, f"github_repos_with_readme.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n  CSV saved → {csv_path}")

    # JSON — convert topics_str back to list for JSON
    records = df.copy()
    records["topics"] = records["topics_str"].apply(
        lambda x: x.split("|") if isinstance(x, str) and x else []
    )
    json_path = os.path.join(data_dir, f"github_repos_with_readme.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records.to_dict(orient="records"), f, indent=2, ensure_ascii=False)
    print(f"  JSON saved → {json_path}")



def print_summary(df: pd.DataFrame) -> None:

    readme_count    = (df["readme"].str.len() > 0).sum()
    readme_avg_len  = df[df["readme"].str.len() > 0]["readme"].str.len().mean()

    print("\n" + "=" * 52)
    print("FINAL DATASET SUMMARY")
    print("=" * 52)
    print(f"  Total repositories   : {len(df)}")
    print(f"  READMEs collected    : {readme_count} / {len(df)}")
    print(f"  Avg README length    : {readme_avg_len:,.0f} chars")
    print(f"  Columns              : {', '.join(df.columns.tolist())}")
    print("=" * 52)



if __name__ == "__main__":
    print("=" * 52)
    print("GitHub README Extractor")
   
    print("=" * 52)

    if GITHUB_TOKEN == "YOUR_TOKEN_HERE":
        print("\nERROR: No GitHub token set!")
        print("Open the script and set GITHUB_TOKEN = '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'")
        exit(1)

    
    print(f"\nStep 1: Loading existing dataset from '{DATA_DIR}/' ...")
    df, source_file = load_latest_csv(DATA_DIR)
    print(f"  {len(df)} repos loaded.")

   
    print(f"\nStep 2: Fetching READMEs from GitHub API ...")
    df = fetch_all_readmes(df)

    
    print(f"\nStep 3: Saving enriched dataset ...")
    save_results(df, DATA_DIR)

    print_summary(df)

    print("\nDone! Use 'github_repos_with_readme_....csv' for all analysis tasks.")