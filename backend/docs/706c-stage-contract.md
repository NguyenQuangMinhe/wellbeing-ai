# Task 706c - Stage Data Contract

** Status; Schema and pipeline wiring complete, gate logic is a placeholder.

## Schema

'sessions' table, 'stage' column:

```sql
stage TEXT DEFAULT 'Start' CHECK(stage IN ('Start', 'Explore', 'Reflect', 'Finish'))
```

A session with no row yet (new session) reads as `"Start"`, so there is no fifth "no session" state to handle.

## Reading and writing

`app/storage/history_store.py`:

```python
def get_session_stage(session_id: str) -> str
def set_session_stage(session_id: str, stage: str) -> None
```

`get_session_stage` returns `"Start"` for an unknown session_id, never raises or returns `None`. `set_session_stage` upserts, safe to call on a session with no existing row.

## Where stage lives in the pipeline

`app/control_plane.py`, `handle_message()`:

- **Read**: immediately after the session-lock check, before crisis/non-English/boundary checks (`current_stage = get_session_stage(session_id)`). Available to any stage-aware logic added later in the function.
- **Write**: only at the very end, inside the output-guardrail `else` branch — i.e. only when the guardrail verdict is `"safe"` and a `type="normal"` response is actually going back to the user.

## When stage does and doesn't advance

| Path                                                        | Stage behaviour                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Locked session                                              | Never reached — function returns before stage is even read                                                                |
| Crisis keyword match                                        | Stage is read but never written — crisis response returns before `evaluate_gate` runs                                     |
| Non-English / boundary match                                | Same — read but not written                                                                                               |
| Intent classification / generation timeout or connect error | Read but not written — these all `return` before guardrail check                                                          |
| Guardrail verdict `"unsafe"`                                | Read but not written — an unsafe response never reaches the user, so per Rule 27 it can't count as a delivered invitation |
| Guardrail verdict `"safe"`                                  | `evaluate_gate(current_stage, user_message)` runs; stage is written only if the result differs from `current_stage`       |

Net effect: stage only ever moves on the genuine happy path, a normal response the user actually sees.

## Note: `evaluate_gate` is a placeholder, not real gate evaluation

`app/classifier/stage_gate.py`:

```python
def evaluate_gate(current_stage: str, user_message: str) -> str
```

Current behaviour: advances exactly one stage forward only if `len(user_message.split()) >= 5`. No evidence extraction, no check against the B01–B04 gate criteria in `system_prompt.md` v1.2 (confirmed situation+thought+feeling+action, goal consent, etc.).

This means a reply like _"yeah that happened again today"_ will currently advance the stage, even though it supplies none of the structured evidence Rule 27's gates actually require. **706b's prompt-selection logic should not treat a stage transition as confirmation that real CBT-gate evidence was captured** — it's only a schema/plumbing placeholder so the rest of the system has a working `stage` value to build and test against.

The real extractor (reading user replies for concrete evidence per gate) is flagged to the PM as unscoped work, not part of 706c. `evaluate_gate`'s signature (`current_stage`, `user_message` → `new_stage`) is intended to stay stable when the real implementation replaces the body, so 706b's integration point shouldn't need to change later.

## Quick reference for 706b

```python
from app.storage.history_store import get_session_stage

stage = get_session_stage(session_id)
# stage is one of "Start", "Explore", "Reflect", "Finish"
# use this to select which prompt variant / rule set to assemble
```
