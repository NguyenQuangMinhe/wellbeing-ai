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

# AC 10.4: Requests to replace, or rely solely on, this AI in place of human/professional support (MWB-1002a rule 28: "If the person says they
# only want to rely on it..."). TR005 above ("can you replace my therapist") already exists and is left where it is for the regression requirement -
REPLACEMENT_OF_CARE_PATTERNS = [
    # RC001
    r"\bcan\s+you\s+be\s+my\s+therapist\b",
    # RC002
    r"\bi\s+only\s+want\s+to\s+rely\s+on\s+you\b",
    # RC003
    r"\byou'?re\s+all\s+i\s+need\b",
    # RC004
    r"\bi\s+don'?t\s+need\s+(?:a\s+)?(?:real\s+)?(?:therapist|counsellor|counselor|doctor)\s+any\s*more\b",
    # RC005
    r"\bcan\s+you\s+be\s+my\s+(?:only|sole)\s+support\b",
    # RC006
    r"\bi'?m\s+going\s+to\s+stop\s+seeing\s+my\s+(?:therapist|counsellor|counselor)\b",
]

# AC 10.3: Requests for a certain answer this prototype has no reliable way to determine (MWB-1002a rule 10: "If you cannot answer
# reliably, clearly explain what you cannot determine. Do not guess or present an uncertain conclusion as fact.")
UNRELIABLE_ANSWER_PATTERNS = [
    # UA001
    r"\bwill\s+i\s+(?:definitely|for\s+sure)\s+get\s+better\b",
    # UA002
    r"\bpromise\s+me\s+(?:this\s+will|i'?ll)\s+(?:work|be\s+(?:ok|okay|fine))\b",
    # UA003
    r"\btell\s+me\s+for\s+(?:certain|sure)\s+(?:what|if|whether)\b",
    # UA004
    r"\bwhat\s+will\s+happen\s+to\s+me\s+in\s+the\s+future\b",
    # UA005
    r"\bguarantee\s+(?:that\s+)?(?:this\s+will|i'?ll)\b",
    # UA006
    r"\bare\s+you\s+(?:100%\s+)?sure\s+this\s+will\s+work\b",
]

_DIAGNOSIS_COMPILED = [re.compile(p) for p in DIAGNOSIS_PATTERNS]
_MEDICATION_COMPILED = [re.compile(p) for p in MEDICATION_PATTERNS]
_CLINICAL_TREATMENT_COMPILED = [re.compile(p) for p in CLINICAL_TREATMENT_PATTERNS]
_CLINICIAN_INVOLVEMENT_COMPILED = [re.compile(p) for p in CLINICIAN_INVOLVEMENT_PATTERNS]
_REPLACEMENT_OF_CARE_COMPILED = [re.compile(p) for p in REPLACEMENT_OF_CARE_PATTERNS]
_UNRELIABLE_ANSWER_COMPILED = [re.compile(p) for p in UNRELIABLE_ANSWER_PATTERNS]


def detect_boundary(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in (
        _DIAGNOSIS_COMPILED + _MEDICATION_COMPILED
        + _CLINICAL_TREATMENT_COMPILED + _CLINICIAN_INVOLVEMENT_COMPILED
    ))


def detect_replacement_of_care(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _REPLACEMENT_OF_CARE_COMPILED)


def detect_unreliable_answer_request(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _UNRELIABLE_ANSWER_COMPILED)


# behaviour for diagnosis, medication, clinical-treatment and clinician-involvement requests
BOUNDARY_RESPONSE_MESSAGE = (
    "I have detected that you're asking about a diagnosis or medication — that needs a qualified professional. "
    "That's a conversation for a doctor or pharmacist. I'm happy to help you think through what to raise with them."
)

# AC 10.4: Limitation stated first, then a professional-support signpost that never promises contact or access (MWB-1002a rule 28)
REPLACEMENT_OF_CARE_RESPONSE_MESSAGE = (
    "I can't replace a therapist, counsellor, or other professional support — I'm an AI prototype, not a substitute for human care. "
    "It's worth keeping a professional in your corner alongside anything we talk about here, and I'm glad to help you think about what to bring to them."
)

# AC 10.3: Limitation stated first; no guess presented as fact (MWB-1002a rule 10)
UNRELIABLE_ANSWER_RESPONSE_MESSAGE = (
    "I can't tell you that with certainty — I don't have a reliable way to determine how things will turn out for you, "
    "and I don't want to guess and present an uncertain answer as fact."
)


def get_boundary_response(text: str) -> str | None:
    
    # Single entry point for the application: returns the approved response text for whichever boundary category matched, or None if nothing
    # matched. Checked in this order: diagnosis/medication/clinical-treatment/clinician-involvement
    
    if detect_boundary(text):
        return BOUNDARY_RESPONSE_MESSAGE
    if detect_replacement_of_care(text):
        return REPLACEMENT_OF_CARE_RESPONSE_MESSAGE
    if detect_unreliable_answer_request(text):
        return UNRELIABLE_ANSWER_RESPONSE_MESSAGE
    return None