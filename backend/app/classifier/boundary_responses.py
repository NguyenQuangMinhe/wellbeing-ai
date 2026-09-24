## TODO: Same pattern as crisis_keywords.py, but for boundary responses.
import re

DIAGNOSIS_PATTERNS = [
    # DX001
    r"\bdiagnose\s+me\b",

    # DX002
    r"\bwhat\s+mental\s+illness\s+do\s+i\s+have\b",

    # DX003
    r"\bdo\s+i\s+have\s+depression\b",

    # DX004
    r"\bam\s+i\s+clinically\s+depressed\b",

    # DX005
    r"\btell\s+me\s+my\s+diagnosis\b",

    # DX006
    r"\bwhich\s+disorder\s+do\s+i\s+have\b",

    # DX007
    r"\bcan\s+you\s+assess\s+me\s+for\s+(?:a\s+)?mental[\s-]?health\s+condition\b",

    # DX008
    r"\bdoes\s+this\s+mean\s+i\s+have\s+anxiety\b",

    # DX009
    r"\bconfirm\s+(?:whether|if)\s+my\s+doctor\s+is\s+right\s+about\s+my\s+diagnosis\b",

    # DX010
    r"\bam\s+i\s+(?:verified|officially)\s+mentally\s+ill\b",
]


MEDICATION_PATTERNS = [
    # MD001
    r"\bwhat\s+medication\s+should\s+i\s+take\b",

    # MD002
    r"\bwhich\s+antidepressant\s+is\s+best\s+for\s+me\b",

    # MD003
    r"\bshould\s+i\s+start\s+taking\s+(?:a\s+)?medication\b",

    # MD004
    r"\bshould\s+i\s+stop\s+taking\s+my\s+medication\b",

    # MD005
    r"\bshould\s+i\s+change\s+my\s+dose\b",

    # MD006 — contextual
    r"\bhow\s+much\s+should\s+i\s+take\b",

    # MD007
    r"\bcan\s+you\s+prescribe\s+(?:something|medication)\s+for\s+me\b",
]


CLINICAL_TREATMENT_PATTERNS = [
    # TR001
    r"\bwhat\s+treatment\s+do\s+i\s+need\b",

    # TR002
    r"\bwhich\s+therapy\s+should\s+i\s+use\b",

    # TR003
    r"\bgive\s+me\s+a\s+treatment\s+plan\b",

    # TR004
    r"\btell\s+me\s+whether\s+i\s+need\s+CBT\s+or\s+(?:another|a\s+different)\s+therapy\b",

    # TR005
    r"\bcan\s+you\s+replace\s+my\s+therapist\b",
]


CLINICIAN_INVOLVEMENT_PATTERNS = [
    # CL001
    r"\bcontact\s+a\s+clinician\s+for\s+me\b",

    # CL002
    r"\bsend\s+(?:this\s+conversation|this\s+chat)\s+to\s+my\s+psychologist\b",

    # CL003
    r"\bis\s+a\s+doctor\s+monitoring\s+this\s+chat\b",

    # CL004
    r"\bbook\s+a\s+therapist\s+appointment\s+for\s+me\b",
]

_DIAGNOSIS_COMPILED = [re.compile(p) for p in DIAGNOSIS_PATTERNS]
_MEDICATION_COMPILED = [re.compile(p) for p in MEDICATION_PATTERNS]
_CLINICAL_TREATMENT_COMPILED = [re.compile(p) for p in CLINICAL_TREATMENT_PATTERNS]
_CLINICIAN_INVOLVEMENT_COMPILED = [re.compile(p) for p in CLINICIAN_INVOLVEMENT_PATTERNS]


def detect_boundary(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in (_DIAGNOSIS_COMPILED + _MEDICATION_COMPILED + _CLINICAL_TREATMENT_COMPILED + _CLINICIAN_INVOLVEMENT_COMPILED))


BOUNDARY_RESPONSE_MESSAGE = (
    "I have detected that you're asking about a diagnosis or medication — that needs a qualified professional. "
    "That's a conversation for a doctor or pharmacist. I'm happy to help you think through what to raise with them."
)