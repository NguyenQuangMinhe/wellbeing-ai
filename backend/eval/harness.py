import csv
import datetime
import json
from pathlib import Path
from app.rag.retriever import retrieve_top_k
from eval.scoring import precision_at_k, recall_at_k, mrr

"""
Retrieval tuning harness (task 1102).

Runs the fixed, committed query set (eval/query_set.json) against
retrieve_top_k() at each k value in K_VALUES, scoring results with the
precision@k / recall@k / MRR functions in scoring.py. Chunk size and
overlap are not swept here as the project knowledge base is chunked by
markdown section header (ingest.py), not by a configurable sliding
window, so k is currently the only tunable retrieval parameter.

Writes one row per k value to eval/results/sweep.csv, in a format
intended to be re-run as-is in Week 2 against the expanded knowledge
base for a direct before/after comparison against this file's values.

Usage (run as a module from backend/, not as a bare script, so that
both `app.*` and `eval.*` imports resolve):

    python -m eval.harness
"""

K_VALUES = [1, 3, 5, 10]

def run_sweep(query_set_path="eval/query_set.json", output_path="eval/results/sweep.csv", k_values=K_VALUES):
    with open(query_set_path, encoding="utf-8") as f:
        queries = json.load(f)

    rows = []
    for k in k_values:
        p_scores, r_scores, mrr_scores = [], [], []
        for q in queries:
            retrieved = retrieve_top_k(q["query"], k=k)
            retrieved_ids = [chunk["id"] for chunk in retrieved]
            p_scores.append(precision_at_k(retrieved_ids, q["relevant_section_ids"], k))
            r_scores.append(recall_at_k(retrieved_ids, q["relevant_section_ids"], k))
            mrr_scores.append(mrr(retrieved_ids, q["relevant_section_ids"]))

        rows.append({
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "k": k,
            "precision_at_k": round(sum(p_scores) / len(p_scores), 4),
            "recall_at_k": round(sum(r_scores) / len(r_scores), 4),
            "mrr": round(sum(mrr_scores) / len(mrr_scores), 4),
        })

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return rows

if __name__ == "__main__":
    results = run_sweep()
    for r in results:
        print(r)
