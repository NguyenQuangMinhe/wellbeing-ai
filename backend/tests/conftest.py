import pytest
from app.storage import history_store

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    
    # redirects history_store's database to a throwaway file for duration of each test in /tests
    # Applied project-wide, no tests will write to real backend/data/history.db
    
    test_db = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", test_db)
    history_store.init_db()
    yield