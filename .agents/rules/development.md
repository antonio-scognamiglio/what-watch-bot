---
trigger: always_on
---

# Development Workflow Rules

- **Docker Synchronization Layer**: This project follows a strict container isolation pattern with no Workspace bind mounts.
- **Applying Changes**: Whenever you modify the **Bot Core Logic** (specifically `SOUL.md`, `IDENTITY.md`, or `SKILL.md`), you MUST inform the user that a Docker image rebuild is required for the changes to take effect in the running container.
- **Sync Command**: The required command to apply and verify these changes is: `docker compose up -d --build`.
- **Bot Commands Sync**: After a Docker rebuild, Telegram bot commands may need to be re-synchronized. Remind the user to copy-paste the contents of `BOT_COMMANDS.md` into [@BotFather](https://t.me/BotFather) using the `/setcommands` command if they appear out of sync.
