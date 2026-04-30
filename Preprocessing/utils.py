import re
import pandas as pd
import json


def load_data(path):
    return pd.read_csv(path, encoding="utf-8")


def save_csv(df, path):
    df.to_csv(path, index=False, encoding="utf-8")


def save_json(df, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2, ensure_ascii=False)


def normalize_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()


def normalize_readme(text):
    if not text:
        return ""
    text = str(text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)
    # Remove markdown images/links
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[.*?\]\(.*?\)", " ", text)
    # Remove special characters
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Collapse spaces
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def split_topics(topics_str):
    if pd.isna(topics_str) or str(topics_str).strip() == "":
        return []
    return [t.strip().lower() for t in str(topics_str).split("|") if t.strip()]