from app.llm.ollama_clients import embedding_model
import pytest

# Test to check if the embedding dimension is correct
@pytest.mark.live
def test_embedding_dimension():
    vector = embedding_model.get_text_embedding("test sentence for dimension check")
    assert len(vector) == 768