---
trigger: always_on
---

# Development Workflow Rules

- **Docker Synchronization Layer**: This project follows a strict container isolation pattern with no Workspace bind mounts.
- **Applying Changes**: Whenever you modify the **Bot Core Logic** (specifically `SOUL.md`, `IDENTITY.md`, or `SKILL.md`), you MUST inform the user that a Docker image rebuild is required for the changes to take effect in the running container.
- **Sync Command**: The required command to apply and verify these changes is: `docker compose up -d --build`.
- **Verify before Commit**: Always run the `/test` workflow before proposing commits that affect the Python logic.
