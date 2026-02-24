# Git Workflow & Commit Rules

- **Validation Before Commit**: For any changes affecting logic (`src/`, `tests/`, `scripts/`), you MUST ALWAYS run the full test suite (`pytest tests/`) and ensure all tests pass BEFORE proposing a commit.
- **Skip Conditions**: You MAY skip running `pytest` ONLY IF the changes are strictly non-functional (e.g., `.md` documentation, `.gitignore`, `.env.example`).
- **Explicit User Approval**: You MUST NEVER run `git commit` without EXPLICIT APPROVAL from the USER. If the change was functional, you must also confirm `pytest` passed before asking for approval. If the user has not explicitly said "you can commit" or similar, just ask them for feedback and do not act.
- **Conventional Commits**: You MUST strictly follow the Conventional Commits specification for all commit messages. Examples: `feat(api): ...`, `fix(pagination): ...`, `test(db): ...`, `refactor(core): ...`.
