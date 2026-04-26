"""
builds nodes and weighted edges between repos that share topics,
ready for PageRank/HITS
"""

import pandas as pd


def build_graph(df):
    print("Building graph data...")

    # Build nodes
    nodes = df[["full_name", "stars", "language"]].rename(columns={"full_name": "id"}).to_dict("records")

    # Build inverted index: topic -> list of repo indices
    # This is O(n * avg_topics) instead of O(n^2)
    topic_to_repos = {}
    for idx, row in df.iterrows():
        for topic in row["topics_list"]:
            topic_to_repos.setdefault(topic, []).append(idx)

    # Build edges from inverted index
    edge_weights = {}
    for topic, indices in topic_to_repos.items():
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                u = df.at[indices[i], "full_name"]
                v = df.at[indices[j], "full_name"]
                key = (u, v) if u < v else (v, u)
                edge_weights[key] = edge_weights.get(key, 0) + 1

    edges = [
        {"source": u, "target": v, "weight": w}
        for (u, v), w in edge_weights.items()
    ]

    nodes_df = pd.DataFrame(nodes)
    edges_df = pd.DataFrame(edges) if edges else pd.DataFrame(columns=["source", "target", "weight"])

    print(f"  Nodes : {len(nodes_df)}")
    print(f"  Edges : {len(edges_df)}")

    return nodes_df, edges_df