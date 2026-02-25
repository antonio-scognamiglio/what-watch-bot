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

3. **Group Changes and Prepare Commit Message(s)**
   Review the changes and group them logically. DO NOT create a single monolithic commit if multiple distinct changes were made (e.g., refactoring logic vs updating docs vs fixing a bug).
   For each logical group, formulate a commit message strictly following the **Conventional Commits** standard (e.g., `feat(api): ...`, `fix(core): ...`, `docs: ...`).

4. **Request User Approval**
   Show the user:

- The logical groupings of files that will be committed separately.
- The proposed commit message for each group.
  Explicitly ask: "May I proceed with these commits?"

5. **Execute the Commit(s)**
   ONLY AFTER receiving explicit approval from the user, proceed to stage and commit each group interactively or one by one. Do not blindly `git add .` if changes should be split.
