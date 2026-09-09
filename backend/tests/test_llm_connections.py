import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from app import config


def test_gemma_generation():
    print("\n--Testing Gemma 4 E4B (generation model)--")
    llm = Ollama(
        model=config.OLLAMA_GEMMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        request_timeout=config.OLLAMA_REQUEST_TIMEOUT,
        keep_alive=config.OLLAMA_KEEP_ALIVE
    )
    start = time.time()
    response = llm.complete("In a sentence, can you explain what CBT is?")
    elapsed = time.time() - start
    print(f"Response: {response}")
    print(f"Time taken: {elapsed:.2f}s")


def test_nomic_embedding():
    print("\n--Testing nomic-embed-text (embedding model)--")
    embed_model = OllamaEmbedding(
        model_name=config.OLLAMA_EMBED_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        keep_alive=config.OLLAMA_KEEP_ALIVE
    )
    start = time.time()
    vector = embed_model.get_text_embedding("In a sentence, can you explain what CBT is?")
    elapsed = time.time() - start
    print(f"Vector length: {len(vector)}")
    print(f"Time taken: {elapsed:.2f}s")


def test_llama_guard_classification():
    print("\n--Testing Llama Guard 3 (classification model)--")
    guard = Ollama(
        model=config.OLLAMA_LLAMAGUARD_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        request_timeout=config.OLLAMA_REQUEST_TIMEOUT,
        keep_alive=config.OLLAMA_KEEP_ALIVE
    )
    start = time.time()
    response = guard.complete("In a sentence, can you explain what CBT is?")
    elapsed = time.time() - start
    print(f"Response: {response}")
    print(f"Time taken: {elapsed:.2f}s")


if __name__ == "__main__":
    test_gemma_generation()
    test_nomic_embedding()
    test_llama_guard_classification()