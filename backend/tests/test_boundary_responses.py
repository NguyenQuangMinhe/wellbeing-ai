from app.classifier.boundary_responses import (
    detect_boundary,
    detect_replacement_of_care,
    detect_unreliable_answer_request,
    get_boundary_response,
    BOUNDARY_RESPONSE_MESSAGE,
    REPLACEMENT_OF_CARE_RESPONSE_MESSAGE,
    UNRELIABLE_ANSWER_RESPONSE_MESSAGE,
)


# --- replacement of care (AC 10.4) ---

def test_replacement_of_care_be_my_therapist():
    assert detect_replacement_of_care("Can you be my therapist?") is True

def test_replacement_of_care_only_rely_on_you():
    assert detect_replacement_of_care("I only want to rely on you from now on") is True

def test_replacement_of_care_youre_all_i_need():
    assert detect_replacement_of_care("You're all I need, honestly") is True

def test_replacement_of_care_benign_message_not_flagged():
    assert detect_replacement_of_care("I had a good chat with my therapist today") is False


# --- unreliable answer requests (AC 10.3) ---

def test_unreliable_answer_will_i_definitely_get_better():
    assert detect_unreliable_answer_request("Will I definitely get better?") is True

def test_unreliable_answer_promise_me():
    assert detect_unreliable_answer_request("Promise me this will work") is True

def test_unreliable_answer_tell_me_for_certain():
    assert detect_unreliable_answer_request("Tell me for certain what's wrong with me") is True

def test_unreliable_answer_benign_message_not_flagged():
    assert detect_unreliable_answer_request("I'm feeling a bit better today, thanks") is False


# --- benign control phrases across both new categories ---

def test_benign_phrase_not_flagged_as_replacement_or_unreliable():
    benign = "I've been feeling stressed about an upcoming deadline"
    assert detect_replacement_of_care(benign) is False
    assert detect_unreliable_answer_request(benign) is False
    assert get_boundary_response(benign) is None


# --- get_boundary_response: approved wording, limitation stated first ---

def test_get_boundary_response_replacement_of_care_wording():
    message = get_boundary_response("Can you be my therapist?")
    assert message == REPLACEMENT_OF_CARE_RESPONSE_MESSAGE
    assert message.index("I can't replace") < message.index("professional in your corner")

def test_get_boundary_response_unreliable_answer_wording():
    message = get_boundary_response("Promise me this will work")
    assert message == UNRELIABLE_ANSWER_RESPONSE_MESSAGE
    assert message.startswith("I can't tell you that with certainty")

def test_get_boundary_response_replacement_of_care_includes_professional_signpost():
    # AC 10.4 specifically requires the professional-support signpost
    message = get_boundary_response("I only want to rely on you from now on")
    assert "professional" in message.lower()

def test_get_boundary_response_no_match_returns_none():
    assert get_boundary_response("How's the weather today?") is None


# --- regression: diagnosis and medication refusals unchanged ---

def test_regression_diagnosis_detection_still_works():
    assert detect_boundary("Diagnose me please") is True

def test_regression_medication_detection_still_works():
    assert detect_boundary("What medication should I take?") is True

def test_regression_diagnosis_wording_unchanged():
    message = get_boundary_response("Diagnose me please")
    assert message == BOUNDARY_RESPONSE_MESSAGE

def test_regression_medication_wording_unchanged():
    message = get_boundary_response("What medication should I take?")
    assert message == BOUNDARY_RESPONSE_MESSAGE

def test_regression_clinical_treatment_still_detected():
    assert detect_boundary("Give me a treatment plan") is True

def test_regression_clinician_involvement_still_detected():
    assert detect_boundary("Contact a clinician for me") is True