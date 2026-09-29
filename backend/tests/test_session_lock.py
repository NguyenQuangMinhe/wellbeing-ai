import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import history_store


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", test_db)
    history_store.init_db()
    yield


def test_session_unlocked_by_default():
    assert history_store.is_session_locked("session1") == False


def test_lock_session():
    history_store.set_session_locked("session1", True)
    assert history_store.is_session_locked("session1") == True


def test_unlock_session():
    history_store.set_session_locked("session1", True)
    history_store.set_session_locked("session1", False)
    assert history_store.is_session_locked("session1") == False


def test_lock_is_session_scoped():
    history_store.set_session_locked("session1", True)
    assert history_store.is_session_locked("session2") == False


def test_delete_history_also_clears_lock():
    history_store.add_entry("session1", "hi", "hello", "normal", "low")
    history_store.set_session_locked("session1", True)
    history_store.delete_history("session1")
    assert history_store.is_session_locked("session1") == False


client = TestClient(app)

def test_full_lifecycle_unlocked_to_high_risk_to_locked_to_terminated():
    session_id = "integration-test-session"

    # 1. Unlocked initially
    assert history_store.is_session_locked(session_id) == False

    # 2. Trigger high risk (crisis)
    response = client.post("/api/message", json={
        "session_id": session_id,
        "message": "I want to end my life",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "crisis"
    assert data["risk_level"] == "high"
    assert data["end_session"] == True

    # 3. Now locked, server-side, independent of any frontend state
    assert history_store.is_session_locked(session_id) == True

    # 4. A completely unrelated follow-up message must still be terminated
    response2 = client.post("/api/message", json={
        "session_id": session_id,
        "message": "just kidding, how's the weather today",
    })
    data2 = response2.json()
    assert data2["type"] == "crisis"
    assert data2["end_session"] == True

    # 5. Both exchanges recorded in history
    history = history_store.get_history(session_id)
    assert len(history) == 2
    assert history[0]["response_type"] == "crisis"
    assert history[1]["response_type"] == "crisis"


def test_boundary_does_not_lock_session():
    session_id = "boundary-test-session"

    response = client.post("/api/message", json={
        "session_id": session_id,
        "message": "what medication should I take",
    })
    data = response.json()
    assert data["type"] == "boundary"
    assert data["end_session"] == False
    assert history_store.is_session_locked(session_id) == False

    # A normal follow-up should proceed normally, not be terminated
    response2 = client.post("/api/message", json={
        "session_id": session_id,
        "message": "hello",
    })
    assert response2.json()["type"] == "normal"


def test_different_sessions_isolated():
    client.post("/api/message", json={"session_id": "locked-one", "message": "I want to end my life"})

    response = client.post("/api/message", json={"session_id": "unrelated-session", "message": "hello"})
    data = response.json()
    assert data["type"] == "normal"
    assert history_store.is_session_locked("unrelated-session") == False