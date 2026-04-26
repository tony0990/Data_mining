"""
deduplicates, fills nulls, normalizes language and topics,
drops zero-topic repos, and builds the combined text column for BERT
"""

import pandas as pd
from utils import normalize_text, normalize_readme, split_topics


def clean_dataset(df):
    print("Cleaning dataset...")
    before = len(df)

    # 1. Remove duplicates
    df = df.drop_duplicates(subset=["full_name"])
    print(f"  Duplicates removed   : {before - len(df)}")

    # 2. Fill missing values
    df["language"]    = df["language"].fillna("unknown")
    df["description"] = df["description"].fillna("")
    df["readme"]      = df["readme"].fillna("")

    # 3. Normalize language
    df["language"] = df["language"].apply(normalize_text)

    # 4. Parse topics into a list
    df["topics_list"] = df["topics_str"].apply(split_topics)

    # 5. Drop repos with no topics — useless for graph edges and Apriori
    before_topics = len(df)
    df = df[df["topics_list"].map(len) > 0]
    print(f"  Dropped (no topics)  : {before_topics - len(df)}")

    # 6. Build clean text column for BERT (description + readme, markdown stripped)
    df["readme_clean"] = df["readme"].apply(normalize_readme)
    df["text"] = (
        df["description"].str.strip()
        + " "
        + df["readme_clean"].str.strip()
    ).str.strip()

    # 7. Reset index so build_graph iloc slicing works correctly
    df = df.reset_index(drop=True)

    # 8. Validation summary
    empty_text  = (df["text"].str.strip() == "").sum()
    empty_desc  = (df["description"].str.strip() == "").sum()
    empty_readme = (df["readme_clean"].str.strip() == "").sum()
    print(f"  Empty description: {empty_desc}")
    print(f"  Empty readme: {empty_readme}")
    print(f"  Empty text (both): {empty_text}")
    print(f"  After cleaning: {len(df)} rows")

    return df