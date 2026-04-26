"""
shared helper functions for loading/saving CSVs and normalizing
text/topics/readme content used across all other modules
"""

import re
import pandas as pd
import json


def load_data(path):
    return pd.read_csv(path, encoding="utf-8")


def save_csv(df, path):
    df.to_csv(path, index=False, encoding="utf-8")


def save_json(df, path):
    df.to_json(path, orient="records", indent=2, force_ascii=False)


def normalize_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()


def normalize_readme(text):
    """Clean raw README content for BERT: strip markdown, collapse whitespace."""
    if pd.isna(text) or str(text).strip() == "":
        return ""
    text = str(text)
    # Remove markdown headers, code blocks, URLs, badges
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)          # images
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)            # links
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.DOTALL)  # inline/block code
    text = re.sub(r"#+\s*", "", text)                     # headers
    text = re.sub(r"\s+", " ", text)                      # collapse whitespace
    return text.strip()


def split_topics(topics_str):
    if pd.isna(topics_str) or str(topics_str).strip() == "":
        return []
    return [t.strip().lower() for t in str(topics_str).split("|") if t.strip()]