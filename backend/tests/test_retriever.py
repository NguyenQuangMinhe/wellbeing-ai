from unittest.mock import patch, MagicMock
from app.rag.retriever import load_system_prompt, retrieve_top_k, assemble_prompt, DEFAULT_K, get_recent_history, format_history_for_assembled_prompt
from app.storage.history_store import add_entry
import uuid
import pytest


# Strictly a mock test, no true Ollama or ChromaDB calls required

@patch("app.rag.retriever.get_collection")
@patch("app.rag.retriever.embedding_model")
def test_retrieve_top_k_mocked(mock_embedding_model, mock_get_collection):
    
    mock_embedding_model.get_text_embedding.return_value = [0.1, 0.2, 0.3]

    # Fake ChromaDB collection returning a fixed result shaped like an authentic collection.query() response
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "ids": [["KB-01.1", "KB-02.1"]],
        "documents": [["Fake chunk text one", "Fake chunk text two"]],
        "metadatas": [[
            {"stage": "Explore", "title": "Fake title one"},
            {"stage": "Start", "title": "Fake title two"},
        ]],
    }
    mock_get_collection.return_value = mock_collection

    results = retrieve_top_k("any query text", k=2)

    # Confirm retrieve_top_k() correctly transformed the fake Chroma response into the expected list of dicts shape
    assert len(results) == 2
    assert results[0]["id"] == "KB-01.1"
    assert results[0]["text"] == "Fake chunk text one"
    assert results[0]["metadata"]["stage"] == "Explore"

    # Confirm the embedding model was actually called with the query text
    mock_embedding_model.get_text_embedding.assert_called_once_with("any query text")

    # Confirm the collection was queried with k=2, not DEFAULT_K
    mock_collection.query.assert_called_once()
    _, call_kwargs = mock_collection.query.call_args
    assert call_kwargs["n_results"] == 2


@patch("app.rag.retriever.get_collection")
@patch("app.rag.retriever.embedding_model")
def test_retrieve_top_k_uses_default_k(mock_embedding_model, mock_get_collection):
    # Confirms DEFAULT_K (3) is used when k isn't explicitly passed
    mock_embedding_model.get_text_embedding.return_value = [0.1, 0.2, 0.3]

    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
    }
    mock_get_collection.return_value = mock_collection

    retrieve_top_k("any query text")

    _, call_kwargs = mock_collection.query.call_args
    assert call_kwargs["n_results"] == DEFAULT_K


# live test: the one real, end-to-end check, no mocking

@pytest.mark.live
def test_retrieve_top_k_live_end_to_end():
    # The sole deliberately live test calling Ollama and ChromaDB collection. 
    # Implemented to confirm mocked assumptions are accurate

    results = retrieve_top_k("What should happen if the AI detects a crisis?")

    assert len(results) == DEFAULT_K
    # KB-03.2 is the known previously-verified relevant chunk for this exact query 
    result_ids = [chunk["id"] for chunk in results]
    assert "KB-03.2" in result_ids


@pytest.mark.live
def test_assemble_prompt_medium_risk_includes_instruction():
    #
    session_id = f"test-{uuid.uuid4()}"
    prompt = assemble_prompt(session_id, "test message", "medium")
    assert "classified as moderate risk" in prompt


@pytest.mark.live
def test_assemble_prompt_low_risk_excludes_instruction():
    session_id = f"test-{uuid.uuid4()}"
    prompt = assemble_prompt(session_id, "test message", "low")
    assert "classified as moderate risk" not in prompt

def test_load_system_prompt_returns_nonempty_content():
    prompt = load_system_prompt()
    assert len(prompt) > 0
    assert "BEGIN SYSTEM PROMPT" not in prompt
    assert "END SYSTEM PROMPT" not in prompt


def test_get_recent_history_returns_stored_entries():
    session_id = f"test-{uuid.uuid4()}"
    add_entry(session_id, "message one", "response one", "normal", "low")
    add_entry(session_id, "message two", "response two", "normal", "low")

    history = get_recent_history(session_id)

    assert len(history) == 2
    assert history[0]["user_message"] == "message one"
    assert history[1]["user_message"] == "message two"


def test_format_history_for_assembled_prompt_produces_readable_transcript():
    session_id = f"test-{uuid.uuid4()}"
    add_entry(session_id, "I've been feeling anxious", "That sounds difficult.", "normal", "low")

    history = get_recent_history(session_id)
    formatted = format_history_for_assembled_prompt(history)

    assert "I've been feeling anxious" in formatted
    assert "That sounds difficult." in formatted

@pytest.mark.live
def test_assemble_prompt_contains_all_four_ingredients():
    session_id = f"test-{uuid.uuid4()}"
    add_entry(session_id, "earlier message", "earlier response", "normal", "low")

    user_message = "I'm stressed about an upcoming deadline"
    prompt = assemble_prompt(session_id, user_message, "low")

    system_prompt_text = load_system_prompt()
    retrieved = retrieve_top_k(user_message)

    assert system_prompt_text[:50] in prompt
    assert retrieved[0]["id"] in prompt
    assert "earlier message" in prompt
    assert user_message in prompt

