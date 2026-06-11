# Engineering Plan: AI Resume Analyzer

## Phase 1: Environment & Pre-requisites
- [x] Declare environment constants in `.env.example`.
- [x] Install central dependencies (`@google/genai`, `pdf-parse`, `mammoth`, `react-markdown`).

## Phase 2: Core Business Logic & API Layout
- [x] Write backend Express routes inside `server.ts` binding static client middleware and custom endpoints.
- [x] Build `/api/parse` using Mammoth and pdf-parse.
- [x] Build `/api/analyze` connected with `gemini-3.5-flash` utilizing JSON schema constraints.

## Phase 3: Frontend View & Integration
- [x] Design beautiful comparative layout with Inter and JetBrains Mono fonts.
- [x] Code file dragging and manual paste overrides.
- [x] Hook local states to call processing APIs, render step loader, circular match dial, comparative pills, and detailed markdown summaries.

## Phase 4: Verification & Certify
- [x] Compile application locally via `compile_applet`.
- [x] Ensure 100% compliance score is achieved across pre-commit hooks, linters, and GitLab checkers.
