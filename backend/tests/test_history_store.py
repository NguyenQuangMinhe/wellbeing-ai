import pytest
from app.storage import history_store


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", test_db)
    history_store.init_db()
    yield


# --- add_entry / get_history ---

def test_add_and_get_entry():
    history_store.add_entry("session1", "hello", "hi there", "normal", "low")
    entries = history_store.get_history("session1")
    assert len(entries) == 1
    assert entries[0]["user_message"] == "hello"
    assert entries[0]["system_message"] == "hi there"
    assert entries[0]["response_type"] == "normal"
    assert entries[0]["risk_level"] == "low"


def test_entries_scoped_to_session():
    history_store.add_entry("session1", "hi", "hello", "normal", "low")
    history_store.add_entry("session2", "hey", "hi", "normal", "low")
    assert len(history_store.get_history("session1")) == 1
    assert len(history_store.get_history("session2")) == 1


def test_multiple_entries_ordered_oldest_first():
    history_store.add_entry("session1", "first", "reply one", "normal", "low")
    history_store.add_entry("session1", "second", "reply two", "normal", "low")
    entries = history_store.get_history("session1")
    assert len(entries) == 2
    assert entries[0]["user_message"] == "first"
    assert entries[1]["user_message"] == "second"


def test_crisis_entry_stored_with_correct_type():
    history_store.add_entry("session1", "I want to end my life", "crisis resources...", "crisis", "high")
    entries = history_store.get_history("session1")
    assert entries[0]["response_type"] == "crisis"
    assert entries[0]["risk_level"] == "high"


# --- delete_history ---

def test_delete_history():
    history_store.add_entry("session1", "hello", "hi", "normal", "low")
    deleted = history_store.delete_history("session1")
    assert deleted == 1
    assert history_store.get_history("session1") == []


def test_delete_nonexistent_session_returns_zero():
    assert history_store.delete_history("nonexistent") == 0


def test_delete_history_only_affects_target_session():
    history_store.add_entry("session1", "hi", "hello", "normal", "low")
    history_store.add_entry("session2", "hey", "hi", "normal", "low")
    history_store.delete_history("session1")
    assert history_store.get_history("session1") == []
    assert len(history_store.get_history("session2")) == 1


# --- session lock ---

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