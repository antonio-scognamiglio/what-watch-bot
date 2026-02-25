---
trigger: always_on
---

# Bot Commands & Wizard Rules

- **Sync Bot Commands**: Whenever you modify, add, or delete a user-facing trigger command in the `SKILL.md` file (the OpenClaw agent wizard), you MUST immediately synchronize the change in `BOT_COMMANDS.md`.
- **BotFather Pasteability**: You MUST use `BOT_COMMANDS.md` strictly as a clean, copy-pasteable list for Telegram's BotFather (`command - description` format).
- **Exclude Dynamic Contexts**: You MUST NOT place contextual, dynamic, or ID-specific commands (such as inline button callbacks or entity-specific actions that the user cannot type directly) inside `BOT_COMMANDS.md`. Put only general entrypoint commands (e.g., `/start`, `/find_title`, `/help`).
