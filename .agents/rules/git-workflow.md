# Git Workflow & Commit Rules

When modifying the `what-watch-bot` repository, you must adhere to the following deterministic constraints to guarantee a clean commit history and proper user approval.

- **Validation Before Commit**: You MUST ALWAYS verify that your code works by running the full test suite (`pytest tests/`) and ensuring all tests pass BEFORE proposing a commit.
- **Explicit User Approval**: You MUST NEVER run `git commit` unless the feature is fully verified, the `pytest` output confirms all tests pass, and you have received EXPLICIT APPROVAL from the USER to commit. If the user has not explicitly said "you can commit", "commit these changes", or similar, just ask them for feedback and do not act.
- **Conventional Commits**: You MUST strictly follow the Conventional Commits specification for all commit messages. Examples: `feat(api): ...`, `fix(pagination): ...`, `test(db): ...`, `refactor(core): ...`.
