import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.llm.ollama_clients import generation_llm, embedding_model, llama_guard


def test_gemma_generation():
    print("\n--Testing Gemma 4 E4B (generation model)--")
    start = time.time()
    response = generation_llm.complete("In a sentence, can you explain what CBT is?")
    elapsed = time.time() - start
    print(f"Response: {response}")
    print(f"Time taken: {elapsed:.2f}s")


def test_nomic_embedding():
    print("\n--Testing nomic-embed-text (embedding model)--")
    start = time.time()
    vector = embedding_model.get_text_embedding("In a sentence, can you explain what CBT is?")
    elapsed = time.time() - start
    print(f"Vector length: {len(vector)}")
    print(f"Time taken: {elapsed:.2f}s")


def test_llama_guard_classification():
    print("\n--Testing Llama Guard 3 (classification model)--")
    start = time.time()
    response = llama_guard.complete("In a sentence, can you explain what CBT is?")
    elapsed = time.time() - start
    print(f"Response: {response}")
    print(f"Time taken: {elapsed:.2f}s")



if __name__ == "__main__":
    test_gemma_generation()
    test_nomic_embedding()
    test_llama_guard_classification()