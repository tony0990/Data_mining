"""
the single entry point that runs the full pipeline in order:
load → clean → transactions → graph → save all outputs
"""

from pathlib import Path
from utils import load_data, save_csv, save_json
from clean_data import clean_dataset
from build_transactions import build_transactions
from build_graph import build_graph

INPUT_PATH = Path(__file__).parent.parent / "Data" / "data" / "github_repos_with_readme.csv"
OUTPUT_DIR = Path(__file__).parent / "output"


def main():
    print("=" * 52)
    print("PREPROCESSING PIPELINE")
    print("=" * 52)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load
    print(f"\nLoading: {INPUT_PATH}")
    df = load_data(INPUT_PATH)
    print(f"  Rows before cleaning: {len(df)}")

    # 2. Clean
    df_clean = clean_dataset(df)
    print(f"  Rows after cleaning: {len(df_clean)}")
    save_csv(df_clean, OUTPUT_DIR / "cleaned_data.csv")
    save_json(df_clean, OUTPUT_DIR / "cleaned_data.json")
    print()

    # 3. Transactions → Apriori / FP-Growth
    transactions = build_transactions(df_clean)
    save_csv(transactions, OUTPUT_DIR / "transactions.csv")
    save_json(transactions, OUTPUT_DIR / "transactions.json")
    print()

    # 4. Graph → PageRank / HITS
    nodes, edges = build_graph(df_clean)
    save_csv(nodes, OUTPUT_DIR / "graph_nodes.csv")
    save_json(nodes, OUTPUT_DIR / "graph_nodes.json")
    save_csv(edges, OUTPUT_DIR / "graph_edges.csv")
    save_json(edges, OUTPUT_DIR / "graph_edges.json")

    print("\n" + "=" * 52)
    print("Outputs saved to:", OUTPUT_DIR)
    print("  cleaned_data.csv/json → BERT classification")
    print("  transactions.csv/json → Apriori / FP-Growth")
    print("  graph_nodes.csv/json → PageRank / HITS")
    print("  graph_edges.csv/json → PageRank / HITS")
    print("=" * 52)
    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    main()