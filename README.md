# Wellbeing AI — Mental Wellbeing Support Prototype

A locally-run prototype chat interface linked to a generative AI model, designed to
provide safe, early-stage mental wellbeing support using CBT-based approaches.

> **Research prototype.** This system does not provide clinical advice, diagnosis,
> or treatment. It is not a replacement for professional mental health care.

## Project Status

🚧 Early development — frontend scaffold in progress, backend not yet started.

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

### 2. Bootstrap (once per clone)

```bash
pnpm run bootstrap
```

This installs dependencies across the workspace, creates `.env` from
`.env.example` if it doesn't already exist, and sets up git hooks (if
configured).

### 3. Run the frontend

```bash
pnpm dev
```

Opens the local dev server (default `http://localhost:5173`).