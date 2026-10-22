# TODO: review
import json
import pytest

from app.storage import history_store
from fastapi.testclient import TestClient
from app.main import app
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
def test_feedback_table_created():
    with history_store.get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert "feedback" in tables


def test_feedback_schema_columns():
    with history_store.get_connection() as conn:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(feedback)").fetchall()
        }

    assert {
        "session_id",
        "flagged_message",
        "category",
        "comment",
        "created_at",
    }.issubset(columns)


def test_feedback_write():
    categories = ["Unhelpful", "Inaccurate"]

    history_store.add_feedback(
        session_id="session-001",
        message_id="message-001",
        flagged_message="Message text",
        category=categories,
        comment="This response is incorrect.",
    )

    with history_store.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM feedback WHERE session_id = ?",
            ("session-001",),
        ).fetchone()

    assert row is not None
    assert row["flagged_message"] == "Message text"
    assert json.loads(row["category"]) == categories
    assert row["comment"] == "This response is incorrect."


def test_feedback_empty_comment():
    history_store.add_feedback(
        session_id="session-002",
        message_id="message-001",
        flagged_message="Message text",
        category=json.dumps(["Unhelpful"]),
        comment="",
    )

    with history_store.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM feedback WHERE session_id = ?",
            ("session-002",),
        ).fetchone()

    assert row is not None
    assert row["comment"] == ""

    def test_delete_history_clears_feedback():
        session_id = "session-003"

        history_store.add_entry(
            session_id=session_id,
            user_message="Hello",
            system_message="Hi there",
            response_type="normal",
            risk_level="low",
        )

        history_store.add_feedback(
            session_id=session_id,
            message_id="message-001",
            flagged_message="response-789",
            category='["Unhelpful"]',
            comment="",
        )

        history_store.delete_history(session_id)

        with history_store.get_connection() as conn:
            history_count = conn.execute(
                "SELECT COUNT(*) FROM history WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

            feedback_count = conn.execute(
                "SELECT COUNT(*) FROM feedback WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

        assert history_count == 0
        assert feedback_count == 0


def test_delete_history_preserves_other_sessions():
    history_store.add_feedback(
        session_id="550e8400-e29b-41d4-a716-446655440002",
        message_id="message-001",
        flagged_message="response-A",
        category='["Unhelpful"]',
        comment=""
    )
    history_store.add_feedback(
        session_id="550e8400-e29b-41d4-a716-446655440003",
        message_id="message-001",
        flagged_message="response-B",
        category='["Inaccurate"]',
        comment=""
    )

    history_store.delete_history("550e8400-e29b-41d4-a716-446655440002")

    with history_store.get_connection() as conn:
        remaining = conn.execute(
            "SELECT session_id FROM feedback"
        ).fetchall()

    assert [row["session_id"] for row in remaining] == ["550e8400-e29b-41d4-a716-446655440003"]

def test_post_feedback_returns_success(client):
    session_id = "550e8400-e29b-41d4-a716-446655440002"
    response = client.post(
        "/api/feedback/" + session_id,
        json={
            "message_id": "response-123",
            "message_text": "Message text",
            "category": ["Unhelpful", "Inaccurate"],
            "additional": "The answer was incorrect.",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    with history_store.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM feedback WHERE session_id = ?",
            (session_id,),
        ).fetchone()

    assert row is not None
    assert row["flagged_message"] == "Message text"
    assert json.loads(row["category"]) == ["Unhelpful", "Inaccurate"]
    assert row["comment"] == "The answer was incorrect."


def test_post_feedback_accepts_empty_comment(client):
    session_id = "550e8400-e29b-41d4-a716-446655440002"
    response = client.post(
        "/api/feedback/" + session_id,
        json={
            "message_id": "response-456",
            "message_text": "Message text",
            "category": ["Unhelpful"],
            "additional": "",
        },
    )

    assert response.status_code == 200, response.text

    with history_store.get_connection() as conn:
        row = conn.execute(
            "SELECT comment FROM feedback WHERE session_id = ?",
            (session_id,),
        ).fetchone()

    assert row is not None
    assert row["comment"] == ""


def test_post_feedback_accepts_omitted_comment(client):
    session_id = "550e8400-e29b-41d4-a716-446655440002"
    response = client.post(
        "/api/feedback/" + session_id,
        json={
            "message_id": "response-789",
            "message_text": "Message text",
            "category": ["Inaccurate"],
        },
    )

    assert response.status_code == 200

    with history_store.get_connection() as conn:
        row = conn.execute(
            "SELECT comment FROM feedback WHERE session_id = ?",
            (session_id,),
        ).fetchone()

    assert row is not None
    assert row["comment"] in ("", None)


def test_post_feedback_rejects_missing_required_fields(client):
    session_id = "550e8400-e29b-41d4-a716-446655440002"
    response = client.post(
        "/api/feedback/" + session_id,
        json={
            "session_id": session_id,
        },
    )

    assert response.status_code == 422

def test_delete_history_clears_feedback():
    session_id = "550e8400-e29b-41d4-a716-446655440002"

    history_store.add_entry(
        session_id=session_id,
        user_message="Hello",
        system_message="Hi there",
        response_type="normal",
        risk_level="low",
    )

    history_store.add_feedback(
        session_id=session_id,
        message_id="message-001",
        flagged_message="response-789",
        category='["Unhelpful"]',
        comment="",
    )

    history_store.delete_history(session_id)

    with history_store.get_connection() as conn:
        history_count = conn.execute(
            "SELECT COUNT(*) FROM history WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]

        feedback_count = conn.execute(
            "SELECT COUNT(*) FROM feedback WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]

    assert history_count == 0
    assert feedback_count == 0


def test_delete_history_preserves_other_sessions():
    history_store.add_feedback(
        session_id="session-A",
        message_id="message-001",
        flagged_message="response-A",
        category='["Unhelpful"]',
        comment=""
    )
    history_store.add_feedback(
        session_id="session-B",
        message_id="message-001",
        flagged_message="response-B",
        category='["Inaccurate"]',
        comment=""
    )

    history_store.delete_history("session-A")

    with history_store.get_connection() as conn:
        remaining = conn.execute(
            "SELECT session_id FROM feedback"
        ).fetchall()

    assert [row["session_id"] for row in remaining] == ["session-B"]