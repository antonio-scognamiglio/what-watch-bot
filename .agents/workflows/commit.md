---
description: Guides the creation of a clean and tested commit, following the Conventional Commits standard. Use this workflow whenever you need to save changes to the repository.
---

# Git Commit Workflow

This workflow ensures that all your commits are tested, well-formatted, completely safe, and correctly synchronized with the remote branch.

1. **Run Tests (Validation)**
   Before committing any functional code, you MUST ensure that the code works.
   Call the `/test` workflow to run the test suite.
   _Note: You may skip this step ONLY if your modifications are strictly non-functional (e.g., Markdown documentation, .gitignore)._

2. **Sync with Remote (Safety Check)**
   // turbo
   Fetch the latest changes from the remote to prevent conflict issues later.
   `git fetch`

   // turbo
   Check the repository status to see which files were modified and if we are behind the remote.
   `git status`

   If `git status` indicates that your branch is behind the remote, you MUST pull the latest changes:
   `git pull --rebase`
   _(If conflicts occur, you MUST stop and resolve them with the user before proceeding further)._

3. **Analyze Local Changes**
   // turbo
   Check the differences to understand exactly what was changed locally.
   `git diff`

4. **Group Changes and Prepare Commit Message(s)**
   Review the changes and group them logically. DO NOT create a single monolithic commit if multiple distinct changes were made (e.g., refactoring logic vs updating docs vs fixing a bug).
   For each logical group, formulate a commit message strictly following the **Conventional Commits** standard (e.g., `feat(api): ...`, `fix(core): ...`, `docs: ...`).

5. **Request User Approval**
   Show the user:
   - The logical groupings of files that will be committed separately.
   - The proposed commit message for each group.
     Explicitly ask: "May I proceed with these commits and push them?"

6. **Execute the Commit(s) Safely**
   ONLY AFTER receiving explicit approval from the user, proceed to stage and commit each group **strictly by specific file paths**.
   ⛔ **CRITICAL:** DO NOT use `git add .` or `git commit -a`. You MUST use `git add <file1> <file2>` for each specific group to avoid bundling unintended changes or requiring `git reset`/`git commit --amend` later.

7. **Push to Remote**
   Once all logical commits are created successfully, push the changes to the remote repository.
   `git push`
