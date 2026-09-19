# Scope and safety

## KB-03.1 | What these notes can support

These notes support general, CBT-informed wellbeing conversation and user-led reflection in a local English-language prototype. They do not qualify the AI as a clinician. The four stages are a project conversation design derived from SRS 2.5, not a clinical treatment pathway. The user may redirect the conversation, decline a question, or end it. [SRS 1.3–1.5, 2.4–2.5; AC 7.3, 9.1–9.3]

## KB-03.2 | Safety comes before retrieval

For each user turn, the application's safety/risk assessment happens before CBT content is retrieved or generated. If that message is classified as high risk or indicates immediate danger, the approved high-risk response takes precedence and the normal CBT conversation will be terminated by the end of the turn. At moderate risk, the SRS calls for a suggestion to seek professional support. The knowledge base does not implement risk classification, provide crisis response, or decide wording for the approved notification. [SRS 1.4.1, 1.4.3; AC 11.4]

## KB-03.3 | No diagnosis or treatment recommendation

Do not use retrieved CBT information to diagnose, recommend medication or a clinical treatment, or answer a request for specific treatment. Follow the application's approved limitation/refusal flow. General educational discussion of thoughts, feelings, and actions is distinct from a recommendation that a specific person receive CBT. [SRS 1.3.2, 1.4.3; AC 10.1–10.4]

## KB-03.4 | Content limits

No patient record, personal story, medical chart, user chat transcript, identifying information, dosage, symptom-to-diagnosis mapping, or therapist instruction belongs in the persistent knowledge-base corpus. User chat context, if handled separately under the SRS, must not be inserted into these static reference documents. External URLs in the manifest are provenance only; local retrieval has no network dependency. [SRS 1.3, 1.4.2, 2.4]
