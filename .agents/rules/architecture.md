---
trigger: always_on
---

# Architecture & Code Organization Rules

- **The OpenClaw Paradigm (Workspace vs Skill)**: The root of this repository represents an **OpenClaw Workspace**, NOT a Python app. The workspace defines the agent's identity via `SOUL.md` and `IDENTITY.md`. The actual bot logic is an isolated **Skill** located in `skills/what-watch-bot/`.
- **Separation of Concerns**: Within the `skills/what-watch-bot/` directory, you MUST strictly categorize all logic into three directories:
  - `src/api/` for external HTTP interactions
  - `src/utils/` for reusable helpers/formatters
  - `scripts/` for OpenClaw action entrypoints
  - `tests/` for pytest logic checking the skill functionality
- **No New Top-Level Logic Dirs**: You MUST NOT create new top-level directories for Python logic in the workspace root. All Python code belongs inside `skills/what-watch-bot/`.
- **Centralize & Reuse**: You MUST extract any duplicated logic into a shared module in `src/utils/` or `src/api/`. Do not copy-paste code.
- **State Management**: You MUST store all user preferences, application state variables, and dynamic configurations inside the SQLite database via `src/database.py`. You MUST NOT hardcode state variables. The DB file is mounted at `/home/node/bot_data/`.
- **Configuration & Secrets**: You MUST NOT read environment variables (`os.environ` or `os.getenv`) directly within application logic. You MUST declare all environment-specific secrets and configuration variables centrally in `src/config.py` and import them from the `Config` class when needed.
