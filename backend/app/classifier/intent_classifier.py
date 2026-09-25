from app.llm.ollama_clients import llama_guard

# define classify_intent function, input parameter = variable 'message' of type str, return dictionary
def classify_intent(message: str) -> dict:

    # note: This function is to be called in control_plane.py after crisis_keywords.py performs first safety check
    # if crisis_keywords.py returns a match, session risk-state set to high.
    # otherwise, the following function distinguishes between low/moderate risk states, based on Llamaguards safe/unsafe verdict

    #message sent to Llamaguard and response stored, .complete() with no streaming for guardrail check
    response = llama_guard.complete(message)   

    #convert Llamaguard response (natural language) to lowercase
    response_text = str(response).strip().lower()


    #check for "safe"/"unsafe" response in LG response
    if "unsafe" in response_text:
        risk_level = "moderate"
    else:
        risk_level = "low"


    return {
        "risk_level": risk_level,
        "Llamaguard_response": response_text
    }