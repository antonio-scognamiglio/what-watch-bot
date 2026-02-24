# Git Workflow & Commit Rules

When modifying the `what-watch-bot` repository, you must adhere to the following deterministic constraints to guarantee a clean commit history and proper user approval.

- **Explicit User Approval**: You MUST NEVER commit code unless the feature is fully verified, tests are passing, and you have received EXPLICIT APPROVAL from the USER to commit. If the user has not explicitly said "you can commit", "commit these changes", or similar, just ask them for feedback and do not run `git commit`.
- **Conventional Commits**: You MUST strictly follow the Conventional Commits specification for all commit messages. Examples: `feat(api): ...`, `fix(pagination): ...`, `test(db): ...`, `refactor(core): ...`.
