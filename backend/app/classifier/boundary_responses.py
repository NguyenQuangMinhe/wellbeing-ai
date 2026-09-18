## TODO: Same pattern as crisis_keywords.py, but for boundary responses.
import re

DIAGNOSIS_PATTERNS = [
    r"\bdiagnose\s+me\b",
    r"\bwhat\s+disorder\s+(do\s+i\s+have|is\s+this)\b",
    r"\bdo\s+i\s+have\s+(depression|anxiety|bpd|ptsd|ocd|adhd)\b",
    r"\bam\s+i\s+(depressed|bipolar|autistic)\b",
]

MEDICATION_PATTERNS = [
    r"\bwhat\s+medication\b",
    r"\bwhich\s+(pills|medication|meds)\b",
    r"\bhow\s+much\s+(should\s+i\s+take|dosage)\b",
    r"\bprescri(be|ption)\b",
    r"\bshould\s+i\s+(take|stop\s+taking)\s+(my\s+)?medication\b",
]

_DIAGNOSIS_COMPILED = [re.compile(p) for p in DIAGNOSIS_PATTERNS]
_MEDICATION_COMPILED = [re.compile(p) for p in MEDICATION_PATTERNS]


def detect_boundary(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in (_DIAGNOSIS_COMPILED + _MEDICATION_COMPILED))


BOUNDARY_RESPONSE_MESSAGE = (
    "I have detected that you're asking about a diagnosis or medication — that needs a qualified professional. "
    "That's a conversation for a doctor or pharmacist. I'm happy to help you think through what to raise with them."
)