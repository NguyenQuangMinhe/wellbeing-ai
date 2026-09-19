import pytest
from app.storage import history_store
from app.llm.prompt_builder import build_prompt, MAX_HISTORY_TURNS


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", test_db)
    history_store.init_db()
    yield


def test_prompt_includes_new_message_with_no_history():
    prompt = build_prompt("session1", "hello")
    assert "User: hello" in prompt
    assert prompt.strip().endswith("Assistant:")


def test_prompt_includes_prior_exchanges():
    history_store.add_entry("session1", "hi", "hello there", "normal", "low")
    prompt = build_prompt("session1", "how are you")
    assert "User: hi" in prompt
    assert "Assistant: hello there" in prompt
    assert "User: how are you" in prompt


def test_prompt_only_includes_current_session():
    history_store.add_entry("session1", "hi", "hello", "normal", "low")
    history_store.add_entry("session2", "secret", "response", "normal", "low")
    prompt = build_prompt("session1", "new message")
    assert "secret" not in prompt


def test_prompt_truncates_to_max_turns():
    for i in range(10):
        history_store.add_entry("session1", f"message {i}", f"reply {i}", "normal", "low")
    prompt = build_prompt("session1", "latest")
    assert "message 0" not in prompt  # oldest should be truncated out
    assert "message 9" in prompt      # most recent should remain