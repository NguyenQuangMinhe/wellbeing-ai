from pathlib import Path
from app.rag.ingest import embedding_model, get_collection

# k=3 chosen as default
# knowledgebase holds 18 chunks total so a smaller assigned k avoids forming assembly prompt with marginally relevant material.
DEFAULT_K = 3

def retrieve_top_k(query_text: str, k: int = DEFAULT_K) -> list[dict]:
    #embeds user message and retrieves the k most similar chunks from ChromaDB
    #return list of dicts each containing chunk id, text, and metadata

    collection = get_collection()
    query_embedding = embedding_model.get_text_embedding(query_text)

    results = collection.query(query_embeddings=[query_embedding], n_results=k)

    chunks = []
    for chunk_id, text, metadata in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0]
    ):
        chunks.append({
            "id": chunk_id,
            "text": text,
            "metadata": metadata,
        })

    return chunks

if __name__ == "__main__":
    test_query = "What should happen if the AI detects a crisis?"
    results = retrieve_top_k(test_query)

    print(f"Query: {test_query!r}\n")
    for i, chunk in enumerate(results):
        print(f"{i+1}. {chunk['id']} [{chunk['metadata']['stage']}] — {chunk['metadata']['title']}")