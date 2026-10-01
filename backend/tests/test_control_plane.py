import uuid
from unittest.mock import patch

import pytest

from app.control_plane import handle_message, GUARDRAIL_FALLBACK_MESSAGE
from app.models.schemas import ChatRequest
from app.storage.history_store import init_db, get_history, is_session_locked

UNSAFE_MARKER = "UNSAFE-MARKER-TEXT-12345"


@pytest.mark.asyncio
async def test_unsafe_text_never_appears_in_response_or_history():
    # Forces the model's generated resposne to return an unsafe guardrail verdict
    # Confirms generated response not returned to user or used to populated stored session histopry
    init_db()
    session_id = f"test-{uuid.uuid4()}"
    request = ChatRequest(
        session_id=session_id,
        message="I've been feeling stressed about an upcoming deadline",
    )

    with patch("app.control_plane.generate_response") as mock_generate, \
         patch("app.control_plane.check_output") as mock_check:
        mock_generate.return_value = UNSAFE_MARKER
        mock_check.return_value = {"verdict": "unsafe", "Llamaguard_response": "unsafe\ns1"}
        response = await handle_message(request)

    print(f"\ntype: {response.type}")
    print(f"risk_level: {response.risk_level}")
    print(f"end_session: {response.end_session}")
    print(f"message: {response.message}")

    assert response.message == GUARDRAIL_FALLBACK_MESSAGE
    assert UNSAFE_MARKER not in response.message

    history = get_history(session_id)
    print(f"stored history entry: {history[0]['system_message']}")

    assert len(history) == 1
    assert UNSAFE_MARKER not in history[0]["system_message"]


@pytest.mark.asyncio
async def test_crisis_writes_history_and_locks_session():
    # tests for crisis message accurately recorded in session history
    # tests for crisis message setting session lock
    # tests follow up prompts in same-session do not reach the LLM
    init_db()
    session_id = f"test-{uuid.uuid4()}"

    crisis_response = await handle_message(
        ChatRequest(session_id=session_id, message="I might hurt myself")
    )

    print(f"\ncrisis type: {crisis_response.type}")
    print(f"crisis risk_level: {crisis_response.risk_level}")
    print(f"crisis end_session: {crisis_response.end_session}")
    print(f"session locked after crisis: {is_session_locked(session_id)}")

    history = get_history(session_id)
    print(f"history rows after crisis: {len(history)}")
    print(f"history row: response_type={history[0]['response_type']}, "
          f"risk_level={history[0]['risk_level']}")

    assert crisis_response.type == "crisis"
    assert crisis_response.risk_level == "high"
    assert crisis_response.end_session is True
    assert is_session_locked(session_id) is True

    assert len(history) == 1
    assert history[0]["response_type"] == "crisis"
    assert history[0]["risk_level"] == "high"

    with patch("app.control_plane.generate_response") as mock_generate:
        follow_up = await handle_message(
            ChatRequest(session_id=session_id, message="Actually, I'm fine now")
        )
        mock_generate.assert_not_called()

    print(f"follow-up type: {follow_up.type}")
    print(f"follow-up end_session: {follow_up.end_session}")

    assert follow_up.type == "crisis"
    assert follow_up.risk_level == "high"
    assert follow_up.end_session is True

@pytest.mark.asyncio
async def test_locked_session_follow_up_is_recorded_in_history():
    
    # test every conversation outcome written to history including a locked-session termination. 
    init_db()
    session_id = f"test-{uuid.uuid4()}"

    await handle_message(ChatRequest(session_id=session_id, message="I might hurt myself"))
    await handle_message(ChatRequest(session_id=session_id, message="Actually, I'm fine now"))

    assert len(get_history(session_id)) == 2