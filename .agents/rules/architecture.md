# Architecture & Code Organization Rules

- **Separation of Concerns**: You MUST strictly categorize all logic into three directories:
  - `src/api/` for external HTTP interactions
  - `src/utils/` for reusable helpers/formatters
  - `scripts/` for OpenClaw action entrypoints
- **No New Top-Level Logic Dirs**: You MUST NOT create new top-level directories for logic.
- **Centralize & Reuse**: You MUST extract any duplicated logic into a shared module in `src/utils/` or `src/api/`. Do not copy-paste code.
- **State Management**: You MUST store all user preferences, application state variables, and dynamic configurations inside the SQLite database via `src/database.py`. You MUST NOT hardcode state variables.
- **Secrets Management**: You MUST store all environment-specific secrets and constants strictly in `.env` and map them via `src/config.py`.
