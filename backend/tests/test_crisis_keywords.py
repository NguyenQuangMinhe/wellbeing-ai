from app.classifier.crisis_keywords import detect_crisis


def test_crisis_detection_explicit():
    assert detect_crisis("I want to kill myself") == True


def test_crisis_detection_direct_intent():
    assert detect_crisis("I want to die") == True


def test_crisis_detection_avoids_false_trigger():
    assert detect_crisis("This assignment is killing me") == False


def test_crisis_detection_case_insensitive():
    assert detect_crisis("I WANT TO DIE") == True


def test_crisis_detection_normal_message():
    assert detect_crisis("I've been feeling a bit anxious about work") == False

def test_crisis_detection_contextual_mention_not_triggered():
    # Documents the deliberate exclusion of suicide from crisis_heywords, as a a contextual, third-person 
    # # or referential use of "suicidal" should not lock a session.
    assert detect_crisis("I read an article about suicidal thoughts in teenagers") == False