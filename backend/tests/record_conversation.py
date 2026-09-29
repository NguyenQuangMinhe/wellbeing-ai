import sys
import uuid

import httpx

from app.storage.history_store import get_history

BASE_URL = "http://localhost:8000"

# httpx defaults to a 5-second timeout. Because the system makes several model calls per prompt
# and to account for recorded slower cold-start execution times, timeout is expended to 120.
TIMEOUT = 120


def send(session_id: str, message: str) -> dict:
    response = httpx.post(
        f"{BASE_URL}/api/message",
        json={"session_id": session_id, "message": message},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    print(f"  type={data['type']} risk_level={data['risk_level']} end_session={data['end_session']}")
    print(f"Assistant: {data['message']}\n")
    return data


def run_interactive_conversation():
    session_id = f"e2e-live-{uuid.uuid4()}"
    print(f"Session: {session_id}")
    print("Type your message and press Enter. Type 'quit' to finish at any time.\n")

    while True:
        try:
            message = input("User: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not message:
            continue
        if message.lower() in ("exit"):
            break

        data = send(session_id, message)

        if data["end_session"]:
            print("[end_session is true - the input would be disabled in the frontend]\n")

    print(f"history rows stored: {len(get_history(session_id))}")


if __name__ == "__main__":
    run_interactive_conversation()