import uuid
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.storage import history_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", test_db)
    history_store.init_db()
    yield


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_read_history_empty_session():
    session_id = str(uuid.uuid4())
    response = client.get(f"/api/history/{session_id}")
    assert response.status_code == 200
    assert response.json() == []


def test_get_session_status_unlocked_by_default():
    session_id = str(uuid.uuid4())
    response = client.get(f"/api/session/{session_id}/status")
    assert response.status_code == 200
    assert response.json() == {"locked": False}


def test_clear_history_nonexistent_session():
    session_id = str(uuid.uuid4())
    response = client.delete(f"/api/history/{session_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted": 0}


def test_post_message_unhandled_exception_returns_error_response():
    # Simulate an unhandled exception in the message handling logic and verify that the API returns a structured error response
    with patch("app.main.handle_message") as mock_handle:
        mock_handle.side_effect = RuntimeError("simulated unexpected failure")
        response = client.post(
            "/api/message",
            json={"session_id": "test-session", "message": "hello"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "error"
    assert data["message"] != ""