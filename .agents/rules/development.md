---
trigger: always_on
---

# Development Workflow Rules

- **Docker Synchronization Layer**: This project follows a strict container isolation pattern with no Workspace bind mounts.
- **Applying Changes**: Whenever you modify the **Bot Core Logic** (specifically `SOUL.md`, `IDENTITY.md`, or `SKILL.md`), you MUST inform the user that a Docker image rebuild is required for the changes to take effect in the running container.
- **Sync Command**: The required command to apply and verify these changes is: `docker compose up -d --build`.
- **Skill Reloading**: After a Docker rebuild, the user MUST explicitly tell the bot in the chat (e.g. on Telegram) to "reload your skill" or "read your skill again" to ensure it uses the latest `SKILL.md` logic in the current session.
- **Bot Commands Sync**: After a Docker rebuild, Telegram bot commands may need to be re-synchronized. Remind the user to copy-paste the contents of `BOT_COMMANDS.md` into [@BotFather](https://t.me/BotFather) using the `/setcommands` command if they appear out of sync.
- **Single Source of Truth (Platforms)**: The list of supported streaming platforms is managed entirely through a Python registry in `workspace/skills/what-watch-bot/src/utils/platforms.py`. You MUST NOT manually add or remove platforms from the markdown lists or lookup tables within `SKILL.md`. If a new platform needs to be supported, you MUST add it to the `SUPPORTED_PLATFORMS` dictionary in `platforms.py`, and when rebuilding the Docker image (`docker compose up -d --build`), the build process will automatically run `tools/sync_platforms.py` to generate and inject the updated Markdown into `SKILL.md` using its HTML comment markers.
