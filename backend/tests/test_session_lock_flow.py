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


client = TestClient(app)


def test_full_lifecycle_unlocked_to_high_risk_to_locked_to_terminated():
    session_id = "integration-test-session"

    # 1. Unlocked — session has no prior state
    assert history_store.is_session_locked(session_id) == False

    # 2. Send a high-risk (crisis) message
    response = client.post("/api/message", json={
        "session_id": session_id,
        "message": "I want to end my life",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "crisis"
    assert data["end_session"] == True

    # 3. Session should now be locked, server-side
    assert history_store.is_session_locked(session_id) == True

    # 4. Subsequent, completely unrelated message should still be terminated
    response2 = client.post("/api/message", json={
        "session_id": session_id,
        "message": "hello, how are you today",
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["type"] == "crisis"
    assert data2["end_session"] == True

    # 5. Both exchanges should be recorded in history
    history = history_store.get_history(session_id)
    assert len(history) == 2
    assert history[0]["response_type"] == "crisis"
    assert history[1]["response_type"] == "crisis"  # locked-session response, also recorded


def test_different_session_unaffected_by_another_sessions_lock():
    client.post("/api/message", json={"session_id": "locked-session", "message": "I want to end my life"})

    response = client.post("/api/message", json={"session_id": "other-session", "message": "hello"})
    data = response.json()
    assert data["type"] != "crisis"
    assert history_store.is_session_locked("other-session") == False