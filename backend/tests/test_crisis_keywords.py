from app.classifier.crisis_keywords import detect_crisis


def test_crisis_detection_explicit():
    assert detect_crisis("I want to kill myself") == True


def test_crisis_detection_avoids_false_trigger():
    assert detect_crisis("This assignment is killing me") == False