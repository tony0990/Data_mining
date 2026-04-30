"""
converts each repo into a bag-of-items (language + topics)
formatted for Apriori/FP-Growth input
"""

import pandas as pd


def build_transactions(df):
    print("Building transaction dataset...")

    transactions = []

    for _, row in df.iterrows():
        items = []

        # Add language — skip 'unknown' as it carries no signal
        if row["language"] and row["language"] != "unknown":
            items.append(f"lang:{row['language']}")

        # Add topics
        items.extend([f"topic:{t}" for t in row["topics_list"]])

        # Apriori/FP-Growth need at least 2 items to form any rule
        if len(items) >= 2:
            transactions.append(items)

    skipped = len(df) - len(transactions)
    print(f"  Skipped (< 2 items)     : {skipped}")
    print(f"  Valid transactions      : {len(transactions)}")

    transactions_df = pd.DataFrame({
        "transaction": ["|".join(t) for t in transactions]
    })

    return transactions_df