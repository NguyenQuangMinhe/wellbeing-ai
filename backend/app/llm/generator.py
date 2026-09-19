from app.llm.ollama_clients import generation_llm

def generate_response(prompt: str) -> str:
    """
    Generate a response using the Gemma 4 E4B model (non-streaming).
    Argument: prompt (str): The input prompt for the model.
    Returns: (str) The generated response from the model.
    """
    response = generation_llm.complete(prompt)
    return response