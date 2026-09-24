import re

CRISIS_PATTERNS = [
    r"\bkill(ing)?\s+myself\b",
    r"\bsuicid(e|al)\b",
    r"\bend(ing)?\s+(my\s+)?life\b",
    r"\bwant\s+to\s+die\b",
    r"\bhurt(ing)?\s+myself\b",
    r"\bself[\s-]?harm\b",
]
_COMPILED_PATTERNS = [re.compile(p) for p in CRISIS_PATTERNS]

def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _COMPILED_PATTERNS)
CRISIS_RESPONSE_MESSAGE = (
    "Unfortunately, I’m unable to help with that request, I can help reflect on thoughts and "
    "feelings but cannot provide diagnosis, medication or crisis support - "
    "if needed, you can reach out to one of these services right away:\n\n"
    "Emergency — 000\n"
    "Lifeline Australia — 13 11 14\n"
    "Beyond Blue — 1300 22 4636"
)