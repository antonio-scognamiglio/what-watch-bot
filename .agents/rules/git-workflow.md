---
trigger: always_on
---

# Git Workflow & Commit Rules

- **Validation Before Commit**: For any changes affecting logic (`src/`, `tests/`, `scripts/`), you MUST ALWAYS run the `/commit` workflow to ensure all tests pass and changes are formatted correctly BEFORE proposing a commit.
- **Skip Conditions**: You MAY skip running `/test` ONLY IF the changes are strictly non-functional (e.g., `.md` documentation, `.gitignore`, `.env.example`).
- **Explicit User Approval**: The `/commit` workflow handles user approval. Never attempt to run `git commit` outside of this workflow.
