from langdetect import detect, LangDetectException

MIN_CHAR_FOR_DETECTION = 20

NON_ENGLISH_RESPONSE_MESSAGE = (
    "I'm currently only able to support English. Please share your thoughts and feelings in English, and I'll do my best to help."
)

def is_non_english(text: str) -> bool:
    #returns True if the text is non-English
    #messages shorter than MiN_CHAR_FOR_DETECTION will always be assumed english accouting for langdetect limitations
    if len(text.strip()) < MIN_CHAR_FOR_DETECTION:
        return False
    try:
        detected = detect(text)
    except LangDetectException:
        return False

    return detected != "en"