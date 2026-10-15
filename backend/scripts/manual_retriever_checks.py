import uuid

from app.rag.retriever import (
    retrieve_top_k,
    load_system_prompt,
    get_recent_history,
    format_history_for_assembled_prompt,
    assemble_prompt,
    MODERATE_RISK_INSTRUCTION,
)
from app.storage.history_store import init_db, add_entry


def check_retrieval():
    test_query = "What should happen if the AI detects a crisis?"
    results = retrieve_top_k(test_query)
    print(f"Query: {test_query!r}\n")
    for i, chunk in enumerate(results):
        print(f"{i+1}. {chunk['id']} [{chunk['metadata']['stage']}] - {chunk['metadata']['title']}")


def check_system_prompt():
    print("\n-Checking load_system_prompt()-\n")
    prompt = load_system_prompt()
    print(f"Prompt length: {len(prompt)} characters")
    print(f"First 80 char: {prompt[:80]!r}")
    print(f"Last 80 char: {prompt[-80:]!r}")


def check_history_and_assembly():
    init_db()
    test_session_id = f"test-session-{uuid.uuid4()}"
    add_entry(test_session_id, "I've been feeling anxious", "That sounds difficult. What's been on your mind?", "normal", "low")
    add_entry(test_session_id, "Mostly work stuff", "Work stress can build up. What's felt hardest about it?", "normal", "low")

    history = get_recent_history(test_session_id)
    print(f"Retrieved {len(history)} entries\n")
    print(format_history_for_assembled_prompt(history))

    full_prompt = assemble_prompt(test_session_id, "I'm stressed about an upcoming deadline", "low")
    print(f"\nSystem prompt present: {load_system_prompt()[:50] in full_prompt}")
    print(f"History present: {'I' in full_prompt}")
    print(f"Current user message present: {'stressed about an upcoming deadline' in full_prompt}")


if __name__ == "__main__":
    check_retrieval()
    check_system_prompt()
    check_history_and_assembly()