# Wellbeing AI — Mental Wellbeing Support Prototype

A locally-run prototype chat interface linked to a generative AI model, designed to
provide safe, early-stage mental wellbeing support using CBT-based approaches.

> **Research prototype.** This system does not provide clinical advice, diagnosis,
> or treatment. It is not a replacement for professional mental health care.

## Scope

**In scope:** local prototype, chat interface, CBT-based responses, RAG-grounded
generation, risk/safety classification, response safety checks, local-only
conversation history with user-controlled deletion.

**Out of scope:** clinical diagnosis, professional/clinician handoff, internet
deployment, accounts/login, multi-user support.

## Getting Started

### 1. Install tools (once per machine)

- Node.js ≥ 20
- pnpm: `npm install -g pnpm`
- Python ≥ 3.11

### 2. Frontend setup

```bash
pnpm run bootstrap
```

This installs dependencies across the workspace, creates `.env` from
`.env.example` if it doesn't already exist, and sets up git hooks (if
configured).

```bash
pnpm dev
```

Opens the local dev server (default `http://localhost:5173`).

### 3. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows — use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
copy .env.example .env         # Windows — use `cp .env.example .env` on macOS/Linux
```

Then run the backend:
```bash
uvicorn app.main:app --reload --port 8000
```
API available at `http://localhost:8000`.

**Note:** the backend has its own isolated Python environment (`venv/`) and its own
`.env` — these are separate from the frontend's setup and must be activated
(`venv\Scripts\activate`) every time you open a new terminal to work on it.

### 4. Run both together

Two terminals:
```bash
# Terminal 1 — frontend
pnpm dev

# Terminal 2 — backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
## Project Structure
wellbeing-ai/
├── frontend/ # Vite + React chat UI
├── backend/ # FastAPI control-plane, RAG, LLM, guardrails
├── scripts/ # bootstrap.js, check-commit-msg.js
├── docs/ # SRS, API contract
└── package.json # root workspace scripts (frontend only)
## Testing

**Frontend:**
```bash
pnpm test              # Vitest unit/component tests
pnpm --filter frontend test:e2e   # Playwright end-to-end
```

**Backend:**
```bash
cd backend
venv\Scripts\activate
pytest
```

## Environment Variables

- `frontend/.env.local` — frontend-specific vars (e.g. `VITE_API_BASE_URL`)
- `backend/.env` — backend-specific vars (e.g. `MODEL_PATH`, `CHROMA_DB_PATH`)
- Root `.env` — pnpm workspace-level vars, if any

Each has a corresponding `.env.example` — copy and fill in locally; never commit
the real `.env` files.

## Privacy & Data

This system runs entirely locally. No conversation data or medical information
is sent to third-party services. Users can clear their stored conversation
history at any time from within the app.
