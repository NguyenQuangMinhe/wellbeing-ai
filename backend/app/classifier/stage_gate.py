import re
from app.llm.ollama_clients import embedding_model

# stage advancement logic for the four-stage CBT conversation flow. Rule 23 (system_prompt.md v1.3): decline, topic change, and a request to end
# override normal sequencing immediately and must never be read as advancement evidence. This module checks those overrides before falling back to the
# existing word-count heuristic.

STAGE_SEQUENCE = ["Start", "Explore", "Reflect", "Finish"]

_DONT = r"(?:don'?t|do\s+not)"

# AC 9.1: Decline must pause (not advance) and must not be satisfied by rewording
DECLINE_PATTERNS = [
    rf"\bi\s+{_DONT}\s+want\s+to\s+(?:answer|talk\s+about)\s+(?:that|this)\b",
    r"\bi'?d\s+rather\s+not\b",
    r"\bno\s+thanks\b",
    r"\bnot\s+(?:right\s+)?now\b",
    r"\bskip\s+(?:that|this)\s+question\b",
    rf"\bi\s+{_DONT}\s+want\s+(?:a\s+)?question\b",
    r"\bi\s+just\s+want\s+to\s+(?:vent|talk)\b",
    r"\bi\s+only\s+want\s+(?:you\s+to\s+)?listen\b",
    rf"\bi\s+{_DONT}\s+want\s+advice\b",
]

# AC 9.3: A request to end must close without another question and must never be read as word-count evidence for advancement
CLOSE_PATTERNS = [
    r"\blet'?s\s+stop\s+here\b",
    r"\bwe\s+can\s+stop\s+here\b",
    r"\bi\s+want\s+to\s+(?:end|stop)\s+(?:this|the)?\s*(?:conversation|chat)?\b",
    r"\bthat'?s\s+enough\s+for\s+(?:today|now)\b",
    r"\bi'?m\s+done\b",
    r"\bgoodbye\b",
    r"\bi\s+(?:need|have)\s+to\s+go\b",
]

_DECLINE_COMPILED = [re.compile(p, re.IGNORECASE) for p in DECLINE_PATTERNS]
_CLOSE_COMPILED = [re.compile(p, re.IGNORECASE) for p in CLOSE_PATTERNS]

# AC 9.2: Topic change resets to Start without steering back. Measured as semantic drift from the immediately preceding user turn rather than a keyword list
# Value calibrated via scripts/calibrate_topic_threshold.py agaonst evaluation_examples.md scenario pairs 
# (same-topic min=0.5276, different-topic max=0.5002)
TOPIC_CHANGE_SIMILARITY_THRESHOLD = 0.5139

# Minimum amount of leftover content required before a topic change check is attempted on a message which aalso includes decline/close phrasing
MIN_REMAINDER_WORDS_FOR_TOPIC_OVERRIDE = 5


def detect_decline(text: str) -> bool:
    return any(p.search(text) for p in _DECLINE_COMPILED)


def detect_close(text: str) -> bool:
    return any(p.search(text) for p in _CLOSE_COMPILED)

def _strip_matched_patterns(text: str, compiled_patterns: list) -> str:
    remainder = text
    for pattern in compiled_patterns:
        remainder = pattern.sub("", remainder)
    return remainder

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def detect_topic_change(current_message: str, previous_user_message: str | None) -> bool:
    if not previous_user_message or not current_message.strip():
        return False

    current_embedding = embedding_model.get_text_embedding(current_message)
    previous_embedding = embedding_model.get_text_embedding(previous_user_message)
    similarity = _cosine_similarity(current_embedding, previous_embedding)
    return similarity < TOPIC_CHANGE_SIMILARITY_THRESHOLD


def evaluate_gate(current_stage: str, user_message: str, previous_user_message: str | None = None) -> str:
    if current_stage not in STAGE_SEQUENCE:
        return "Start"

    is_decline = detect_decline(user_message)
    is_close = detect_close(user_message)

    if is_decline or is_close:
        # A new topic introduced in the same message as a decline/close still overrides the sequence (rule 23) and resets to Start, but
        # only when there's genuine topical content left after the decline/close wording is removed. Otherwise a content-free
        # refusal like "I don't want to answer that" would be misread as a topic change purely because it has nothing in common with the previous turn's specific concern.
        remainder = _strip_matched_patterns(user_message, _DECLINE_COMPILED + _CLOSE_COMPILED)
        remainder_word_count = len(remainder.split())

        if (
            current_stage != "Start"
            and remainder_word_count >= MIN_REMAINDER_WORDS_FOR_TOPIC_OVERRIDE
            and detect_topic_change(remainder, previous_user_message)
        ):
            return "Start"

        return current_stage  # pause - decline/close wins when there's no genuine new topic

    if current_stage != "Start" and detect_topic_change(user_message, previous_user_message):
        return "Start"

    current_index = STAGE_SEQUENCE.index(current_stage)
    if current_index == len(STAGE_SEQUENCE) - 1:
        return current_stage  # already at Finish, nothing further to advance to

    word_count = len(user_message.split())
    if word_count < 5:
        return current_stage  # too short to count as real evidence, stay put

    return STAGE_SEQUENCE[current_index + 1]