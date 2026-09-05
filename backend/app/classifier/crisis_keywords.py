import re

CRISIS_PATTERNS = [
    r"\bkill(ing)?\s+myself\b",
    r"\bsuicid(e|al)\b",
    r"\bend(ing)?\s+(my\s+)?life\b",
    r"\bwant\s+to\s+die\b",
    r"\bhurt(ing)?\s+myself\b",
    r"\bself[\s-]?harm\b",
]

def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in CRISIS_PATTERNS)