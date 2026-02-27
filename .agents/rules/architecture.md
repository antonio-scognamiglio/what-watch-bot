---
trigger: always_on
---

# Architecture & Code Organization Rules

- **The OpenClaw Paradigm (Workspace vs Skill)**: This repository is split into two layers:
  - **Dev layer (repo root)**: `Dockerfile`, `docker-compose*.yml`, `requirements.txt`, `tools/`, `.agents/`, `README.md`, `BOT_COMMANDS.md`, etc. These files are **not** copied into the Docker image as workspace files.
  - **Workspace layer (`workspace/`)**: Maps 1:1 to OpenClaw's `~/.openclaw/workspace`. The Dockerfile copies the entire `workspace/` directory into the container at `/home/node/what-watch-bot/`. This is where `SOUL.md`, `IDENTITY.md`, and the `skills/` directory live.

- **Workspace Structure (inside `workspace/`)**:

  ```
  workspace/
  ├── SOUL.md           ← agent identity and behavior
  ├── IDENTITY.md       ← name, creature, vibe, emoji
  └── skills/
      └── what-watch-bot/   ← the OpenClaw skill
          ├── SKILL.md
          ├── scripts/      ← OpenClaw action entrypoints
          ├── src/          ← Python application logic
          └── tests/        ← pytest tests (excluded from Docker image)
  ```

- **Container Path Resolution**:
  - `workspace/` → `/home/node/what-watch-bot/` (via `COPY workspace/ /home/node/what-watch-bot/`)
  - `/home/node/.openclaw/workspace` → `/home/node/what-watch-bot/` (via symlink set at container startup)
  - Skill path in container: `/home/node/what-watch-bot/skills/what-watch-bot/`

- **Separation of Concerns**: Within `workspace/skills/what-watch-bot/`, categorize all logic strictly:
  - `src/api/` for external HTTP interactions
  - `src/utils/` for reusable helpers/formatters
  - `scripts/` for OpenClaw action entrypoints
  - `tests/` for pytest logic (dev only, excluded from Docker image)

- **No New Top-Level Logic Dirs**: All Python code belongs inside `workspace/skills/what-watch-bot/`. Do NOT create new top-level directories for Python logic.

- **Centralize & Reuse**: Extract any duplicated logic into a shared module in `src/utils/` or `src/api/`. Do not copy-paste code.

- **State Management**: Store all user preferences and dynamic configurations in the SQLite database via `src/database.py`. The DB file is mounted at `/home/node/what-watch-db/` (named volume in prod, local bind mount `./db/` in dev).

- **Configuration & Secrets**: Do NOT read environment variables directly within application logic. Declare all secrets and configuration centrally in `src/config.py` and import from the `Config` class.
