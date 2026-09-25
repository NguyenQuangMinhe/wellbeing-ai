from app.llm.ollama_clients import llama_guard

# Safety check on generated response using Llamaguard. Final safety check before return to frontend.
# Uses came instance of Llamaguard as intent_classifier.py; both functions import from ollama_clients.py.
def check_output(generated_response: str) -> dict:

    response = llama_guard.complete(generated_response)
    response_text = str(response).strip().lower()

    if "unsafe" in response_text:
        verdict = "unsafe" 
    else:
        verdict = "safe"

    return {
        "verdict": verdict,
        "Llamaguard_response": response_text,
    }