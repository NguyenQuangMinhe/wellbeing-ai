# Backend

## Prerequisites

- Python v3.14+ 
- Ollama (https://ollama.com/download) installed and running locally

## Ollama Model Setup

This project backend utilises three local models via Ollama. Each can be pulled using the following commands:
- ollama pull gemma4:e4b
- ollama pull nomic-embed-text
- ollama pull llama-guard3:1b

| Role | Model | Used by |
|---|---|---|
| Generation | `gemma4:e4b` | `app/llm/generator.py` |
| Embeddings | `nomic-embed-text` | `app/rag/retriever.py` |
| Classification / Guardrail | `llama-guard3:1b` | `app/classifier/intent_classifier.py`, `app/classifier/output_check.py` |

Verify all three are present using:

    ollama list

Expected 'ollama list' output includes all three model names (ID, SIZE, and MODIFIED values may differ)

| NAME | ID | SIZE | MODIFIED |
|---|---|---|---|
| llama-guard3:1b | 494147e06bf9 | 1.6 GB | X weeks ago |
| nomic-embed-text:latest | 0a109f422b47 | 274 MB | X weeks ago |
| gemma4:e4b | c6eb396dbd59 | 9.6 GB | X weeks ago |

If any model is missing, ensure you have accurately pulled the correct model before continuing.

## Backend Setup
Within terminal:

    cd backend
    python -m venv venv
    ./venv\Scripts\Activate.ps1
    pip install -r requirements.txt

## Running the Backend
Two terminals are required:

Terminal 1:

    cd backend
    ./venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload --port 8000

Terminal 2:

    cd frontend
    pnpm dev

The frontend dev server must appear at 'http://localhost:5173', as the backend's CORS config explicity requires that origin.

## Knowledge base ingestion
Run once before first use, and again any time the knowledge base markdown files or `coverage_map.csv` change. Requires Ollama running (uses `nomic-embed-text` for embeddings). From `backend/` with the venv active:

    python -m app.rag.ingest

This command is safe to re-run at anytime, as chunks are upserted by 'section_id', so duplicate executions overwrite existing entries with no risk of duplication.

Upon success you'll see an output such as the following:

    Ingested X chunks into ChromaDB at '<path>'
    Collection count: X

...followed by three sample queries with their top retrieved chunks to serve as a sanity check.

## Troubleshooting

**Timeout errors (`ReadTimeout`) on first message after startup.** 
The first call to a given model after Ollama (re)starts has to load it into memory, which is significantly slower than subsequent calls. Testing showed Gemma 4 E4B's cold-start call alone occasionally exceeding 60 seconds, resulting in `OLLAMA_REQUEST_TIMEOUT` being set to 90s. 
This means: a session's first message will take noticeably longer than later ones. This is expected, and should not be confused as a sign of failure.

**Chat returns "We couldn't generate a response right now. Please try again later, sorry for the inconvenience." on every message.** 
This is `MODEL_UNAVAILABLE_MESSAGE`, returned by the catch-all error handler in `app/main.py` whenever `handle_message` raises an unhandled exception, including an Ollama error for a model that hasn't been pulled. 

Not something encountered during development but inferred from code: `ollama_clients.py` builds its model clients at import time without calling Ollama, so a missing model won't fail until the first chat request actually needs it. 
If you see this, check the backend terminal for a traceback under "Unhandled error processing message for session...". A 404 or "model not found" error there means you must re-check `ollama list` against the three required models above.

**CORS rejection in the browser console.** 
`app/main.py` only allows requests from `http://localhost:5173` (Vite's default port). If you see an error like:

    Access to fetch at 'http://localhost:8000/api/message' from origin 'http://localhost:5174' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.

check what port `pnpm dev` actually printed on startup. If port 5173 is already in use, Vite silently picks the next free port (e.g., 5174), which the backend won't accept.

## Running tests

Unit tests only (No live services required, i.e., Ollama does not need to be running):

    pytest

Full suite including live integration checks (requires Ollama running locally with Llama Guard pulled):

    pytest -m live

Everything in one run (Unit $ Live Tests):

    pytest -m "live or not live"

Generate backend test coverage report:

    pytest --cov=app --cov-report=term-missing

Coverage report saved as .txt file:

    pytest --cov=app --cov-report=term-missing > coverage_report.txt

