---
trigger: always_on
description: Ensures the agent never commits or pushes code outside of the official /commit workflow.
---

# Git Workflow & Commit Rules

- **Workflow Mandate**: You MUST NEVER run `git commit` or `git push` autonomously. Any request to commit code, save changes, or push to the remote repository MUST be routed exclusively through the `/commit` workflow.
- **Full Delegation**: Do not attempt to bypass or pre-empt steps. The `/commit` workflow handles test validation, synchronization, conflict resolution, grouping, and pushing. Follow its instructions exactly.
