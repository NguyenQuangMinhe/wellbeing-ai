# CBT knowledge base — local prototype

This package is sectioned for local RAG chunking; it is not a clinical protocol or a substitute for the application safety layer.

## Contents

| File                      | Purpose                                                                    |
| ------------------------- | -------------------------------------------------------------------------- |
| `01_cbt_principles.md`    | Five project CBT principles and safe educational framing                   |
| `02_cbt_stages.md`        | Start, Explore, Reflect and Finish conversation stages                     |
| `03_scope_and_safety.md`  | Constraints for use of these notes                                         |
| `coverage_map.csv`        | Explicit document-to-principle/stage mapping                               |
| `reference_registry.csv`  | Disposition and rights notes for all six supplied source links and the SRS |
| `RAG Knowledge Base.docx` | A six link RAG knowledge base source list approved by client (Tarique)     |

Chunk by `##` section. Retain the `document_id`, `section_id`, `source_refs`, and `stage` fields in each chunk's metadata. Keep `coverage_map.csv` beside the indexed documents. Do not automatically download source URLs during ingestion or call them at runtime. URL fields serve citation and human review only. The SRS requires a free-to-use local LLM; any embedding stage must also run locally to meet this task's no-external-calls constraint. This package does not select or install models.

Retrieval must remain downstream of the safety/risk decision. A high-risk classification ends normal CBT support according to SRS 1.4.1 and 1.4.3. Retrieved CBT content never overrides that decision. Preserve the user's choice to redirect or end a conversation (AC 7.3, AC 9.2–9.3). A stage label is an aid for retrieval, not a rigid script, diagnosis, or claim that the AI is delivering therapy.

## Provenance and review

Project requirements: the latest supplied `SRS – Gen AI Systems Mental Wellbeing.docx`, especially 1.3–1.4, 1.8 (US 7, 9–11), 2.1–2.5. The project-specific four-stage model is drawn from 2.5; it is **not** presented as a universally accepted clinical CBT protocol. . The supplied `RAG Knowledge Base.docx` is a six-link source list; all six links appear in `reference_registry.csv`. All knowledge-base prose is newly written synthesis; no website page, PDF, clinical note, patient example, or user transcript is bundled. The CCI PDF is marked reference-only because it is a clinician-facing depression information sheet and is unnecessary for this general support corpus.
