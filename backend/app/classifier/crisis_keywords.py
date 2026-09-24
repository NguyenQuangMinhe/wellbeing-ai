import re

CRISIS_PATTERNS = [
    # HR001
    r"\bkill(ing)?\s+myself\b",

    # HR002 / HR003
    r"\bend(ing)?\s+(my\s+)?life\b",
    r"\btake(ing)?\s+my\s+own\s+life\b",

    # HR004
    r"\b(?:i\s+)?want\s+to\s+die\b",

    # HR005
    r"\bi\s+(?:do\s+not|don't)\s+want\s+to\s+be\s+alive(?:\s+anymore)?\b",

    # HR006
    r"\bi\s+wish\s+i\s+(?:were|was)\s+dead\b",

    # HR007 / HR008
    r"\bi\s+(?:am|'m)\s+going\s+to\s+hurt\s+myself\b",
    r"\bi\s+might\s+hurt\s+myself\b",

    # HR009
    r"\bi\s+(?:am|'m)\s+thinking\s+about\s+self[\s-]?harm\b",

    # HR010
    r"\bi\s+(?:can\s*not|can't)\s+keep\s+myself\s+safe\b",

    # HR011
    r"\bi\s+am\s+in\s+immediate\s+danger\s+from\s+myself\b",

    # HR012 / HR013
    r"\bi\s+have\s+a\s+plan\s+to\s+harm\s+myself\b",
    r"\bi\s+plan\s+to\s+harm\s+myself(?:\s+(?:tonight|today|now))?\b",

    # HR014
    r"\bi\s+have\s+the\s+means\s+to\s+end\s+my\s+life\b",

    # HR015
    r"\bi\s+have\s+decided\s+to\s+end\s+my\s+life\b",

    # HR016
    r"\bgoodbye\b.*\bi\s+will\s+not\s+be\s+here\s+tomorrow\b",

    # HR017
    r"\bi\s+want\s+to\s+quit\s+the\s+world\b",

    # HR018
    r"\bthere\s+is\s+no\s+reason\s+for\s+me\s+to\s+live\b",

    # HR019
    r"\bi\s+am\s+about\s+to\s+harm\s+myself\b",

    # HR020
    r"\bi\s+already\s+hurt\s+myself\b.*\b(?:again|again\s+soon|do\s+it\s+again)\b",

    # HR021
    r"\bthere\s+is\s+no\s+point\s+anymore\b",

    # HR022 HR023 - contextual
    #r"\bsuicid(e|al)\b"
    #r"\bself[\s-]?harm\b"
]
HARMFUL_PATTERNS = [
    ## harmful_information_request
    # HI001
    r"\btell\s+me\s+how\s+to\s+hurt\s+myself\b",
    
    # HI002
    r"\bhow\s+can\s+i\s+kill\s+myself\b",
    
    # HI003
    r"\bwhat\s+(?:is|are)\s+the\s+medicine(?:s)?\s+that\s+can\s+end\s+my\s+suffering\b",
    
    # HI004
    r"\bwhat\s+is\s+the\s+easiest\s+way\s+to\s+die\b",
    
    # HI005
    r"\bgive\s+me\s+self[\s-]?harm\s+instructions\b",
    
    # HI006
    r"\btell\s+me\s+a\s+method\s+that\s+would\s+work\b",
]
_COMPILED_CRISIS = [re.compile(p) for p in CRISIS_PATTERNS]
_COMPILED_HARMFUL = [re.compile(p) for p in HARMFUL_PATTERNS]

def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _COMPILED_CRISIS + _COMPILED_HARMFUL)

CRISIS_RESPONSE_MESSAGE = (
    "Unfortunately, I’m unable to help with that request, I can help reflect on thoughts and "
    "feelings but cannot provide diagnosis, medication or crisis support - "
    "if needed, you can reach out to one of these services right away:\n\n"
    "Emergency — 000\n"
    "Lifeline Australia — 13 11 14\n"
    "Beyond Blue — 1300 22 4636"
)