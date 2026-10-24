# Relevance scoring method for retrieval tuning. 
# Each query in query_set.json has a hand-judged set of relevant_section_ids matching the section_id values used by ingest.py for chuck IDs
# For each given retieval call retuning the top-k chunk ids, the following is computed:

# Precision@k: |retrieved ∩ relevant| / k
# Recall@k:    |retrieved ∩ relevant| / |relevant|
# MRR:         1 / rank of first relevant chunk in the retrieved list (0 if none)

def precision_at_k(retrieved_ids, relevant_ids, k):
    retrieved_k = retrieved_ids[:k]
    hits = len(set(retrieved_k) & set(relevant_ids))
    return hits / k

def recall_at_k(retrieved_ids, relevant_ids, k):
    retrieved_k = retrieved_ids[:k]
    hits = len(set(retrieved_k) & set(relevant_ids))
    return hits / len(relevant_ids) if relevant_ids else 0.0

def mrr(retrieved_ids, relevant_ids):
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant_ids:
            return 1 / rank
    return 0.0

