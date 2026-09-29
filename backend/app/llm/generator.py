from app.llm.ollama_clients import generation_llm

def generate_response(prompt: str) -> str:
    # generating response using the Gemma 4 E4B model (non-streaming)
    response = generation_llm.complete(prompt)
    return str(response)