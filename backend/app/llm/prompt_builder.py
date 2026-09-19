from app.storage.history_store import get_history

MAX_HISTORY_TURNS = 6
# TODO: system prompt
SYSTEM_PROMPT = ("")


# Uses current session's history + new message.
# SRS: single-user, no cross-session context leakage

def build_prompt(session_id: str, new_message: str) -> str:
    history = get_history(session_id)
    recent = history[-MAX_HISTORY_TURNS:]

    conversation_lines = []
    for entry in recent:
        conversation_lines.append(f"User: {entry['user_message']}")
        conversation_lines.append(f"Assistant: {entry['system_message']}")

    conversation_lines.append(f"User: {new_message}")

    conversation_text = "\n".join(conversation_lines)

    return f"{SYSTEM_PROMPT}\n\n{conversation_text}\nAssistant:"