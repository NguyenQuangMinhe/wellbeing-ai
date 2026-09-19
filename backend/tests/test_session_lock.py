import pytest
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