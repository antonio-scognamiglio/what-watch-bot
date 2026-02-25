---
description: Guides the creation of a clean and tested commit, following the Conventional Commits standard. Use this workflow whenever you need to save changes to the repository.
---

# Git Commit Workflow

This workflow ensures that all your commits are tested, well-formatted, and completely safe.

1. **Run Tests (Validation)**
   Before committing any functional code, you MUST ensure that the code works.
   Call the `/test` workflow to run the test suite.
   _Note: You may skip this step ONLY if your modifications are strictly non-functional (e.g., Markdown documentation, .gitignore)._

2. **Analyze Changes (Staging)**
   // turbo
   Check the repository status to see which files were modified.
   `git status`

// turbo
Check the differences to understand exactly what was changed.
`git diff`

3. **Prepare the Commit Message**
   Based on the observed modifications, formulate a commit message strictly following the **Conventional Commits** standard (e.g., `feat(api): ...`, `fix(core): ...`, `docs: ...`).

4. **Request User Approval**
   Show the user:

- The files that will be committed.
- The proposed commit message.
  Explicitly ask: "May I proceed with the commit?"

5. **Execute the Commit**
   ONLY AFTER receiving explicit approval from the user in the previous step, proceed to stage the files and create the commit.
   // turbo
   `git add .`

// turbo
`git commit -m "YOUR_APPROVED_MESSAGE_HERE"`
