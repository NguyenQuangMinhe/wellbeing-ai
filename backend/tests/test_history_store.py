import os
import pytest
from app.storage import history_store


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", test_db)
    history_store.init_db()
    yield


def test_add_and_get_entry():
    history_store.add_entry("session1", "user", "hello", "low")
    entries = history_store.get_history("session1")
    assert len(entries) == 1
    assert entries[0]["message"] == "hello"
    assert entries[0]["risk_level"] == "low"


def test_entries_scoped_to_session():
    history_store.add_entry("session1", "user", "hi", "low")
    history_store.add_entry("session2", "user", "hey", "low")
    assert len(history_store.get_history("session1")) == 1
    assert len(history_store.get_history("session2")) == 1


def test_delete_history():
    history_store.add_entry("session1", "user", "hello", "low")
    deleted = history_store.delete_history("session1")
    assert deleted == 1
    assert history_store.get_history("session1") == []


def test_delete_nonexistent_session_returns_zero():
    assert history_store.delete_history("nonexistent") == 0