from pathlib import Path
from app.rag.ingest import embedding_model, get_collection
from app.storage.history_store import get_history

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



SYSTEM_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "system_prompt.md"

def load_system_prompt() -> str:
    #read system prompt file and extract text between BEGIN and END SYSTEM PROMPT
    
    text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    code_fence = "```text"
    fence_start = text.index(code_fence) + len(code_fence)

    start_marker = "BEGIN SYSTEM PROMPT"
    end_marker = "END SYSTEM PROMPT"

    start = text.index(start_marker, fence_start) + len(start_marker)
    end = text.index(end_marker, start)

    return text[start:end].strip()



MAX_HISTORY_TURNS = 10 #max number of session history turns included in assembled prompt. Fixed cap, subject to change.

def get_recent_history(session_id: str) -> list[dict]:
    #10-turns of session history, ordered oldest-to-newest
    full_history = get_history(session_id)
    return full_history[-MAX_HISTORY_TURNS:]

def format_history_for_assembled_prompt(history: list[dict]) -> str:
    #conversion of session history turns into text transcript
    #alternating between 'User:' and 'Assistant:' lines 
    lines = []
    for entry in history:
        lines.append(f"User: {entry['user_message']}")
        lines.append(f"Assistant: {entry['system_message']}")
    return "\n".join(lines)






if __name__ == "__main__":
    test_query = "What should happen if the AI detects a crisis?"
    results = retrieve_top_k(test_query)

    print(f"Query: {test_query!r}\n")
    for i, chunk in enumerate(results):
        print(f"{i+1}. {chunk['id']} [{chunk['metadata']['stage']}] — {chunk['metadata']['title']}")

    print("\n-Testing load_system_prompt()-\n")
    prompt = load_system_prompt()
    print(f"Prompt length: {len(prompt)} characters")
    print(f"First 80 char: {prompt[:80]!r}")
    print(f"Last 80 char: {prompt[-80:]!r}")

    from app.storage.history_store import add_entry, init_db

    init_db()
    test_session_id = "test-session-403"
    add_entry(test_session_id, "I've been feeling anxious", "That sounds difficult. What's been on your mind?", "normal", "low")
    add_entry(test_session_id, "Mostly work stuff", "Work stress can build up. What's felt hardest about it?", "normal", "low")

    history = get_recent_history(test_session_id)
    print(f"Retrieved {len(history)} entries\n")
    print(format_history_for_assembled_prompt(history))