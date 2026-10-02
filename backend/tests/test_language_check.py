from app.classifier.language_check import is_non_english


def test_short_english_not_flagged():
    assert is_non_english("hi") == False


def test_short_english_fragment_not_flagged():
    assert is_non_english("im stressed") == False


def test_long_english_not_flagged():
    assert is_non_english("I have been feeling really stressed about an upcoming deadline at work") == False


def test_long_french_flagged():
    assert is_non_english("Je me sens vraiment stressé à propos d'un délai qui approche au travail") == True


def test_long_spanish_flagged():
    assert is_non_english("No puedo dormir bien, estoy muy preocupado por el trabajo") == True