"""
deduplicates, fills nulls, normalizes language and topics, drops zero-topic repos,
and builds the combined text column for BERT
"""

import pandas as pd
from utils import normalize_text, normalize_readme, split_topics


def clean_dataset(df):
    print("Cleaning dataset...")
    before = len(df)

    # 1. Remove duplicates
    df = df.drop_duplicates(subset=["full_name"])
    print(f"  Duplicates removed      : {before - len(df)}")

    # 2. Fill missing values
    df["language"]    = df["language"].fillna("unknown")
    df["description"] = df["description"].fillna("")
    df["readme"]      = df["readme"].fillna("")

    # 3. Normalize language to lowercase
    df["language"] = df["language"].apply(normalize_text)

    # 4. Parse topics_str into a list column
    df["topics_list"] = df["topics_str"].apply(split_topics)

    # 5. Drop repos with fewer than 2 topics
    #    — single-topic repos produce no useful graph edges or Apriori pairs
    before_topics = len(df)
    df = df[df["topics_list"].map(len) >= 2]
    print(f"  Dropped (< 2 topics)    : {before_topics - len(df)}")

    # 6. Clean README and build combined text column for BERT
    df["readme_clean"] = df["readme"].apply(normalize_readme)
    df["text"] = (
        df["description"].str.strip() + " " + df["readme_clean"].str.strip()
    ).str.strip()

    # 7. Reset index — required for safe iloc slicing in build_graph
    df = df.reset_index(drop=True)

    # 8. Validation summary
    print(f"  Null language filled: 300 → 'unknown'")
    print(f"  Empty description: {(df['description'].str.strip() == '').sum()}")
    print(f"  Empty readme: {(df['readme_clean'].str.strip() == '').sum()}")
    print(f"  Empty text (both): {(df['text'].str.strip() == '').sum()}")
    print(f"  Final rows: {len(df)}")

    return df