---
trigger: always_on
description: "Rules for OpenClaw development, definitions of native template files, and anti-hallucination mandate for fetching official documentation."
---

# OpenClaw Development Rules

- **Anti-Hallucination Mandate**: When building or modifying OpenClaw features (e.g., wizards, configuration files, core behaviors), you MUST NOT hallucinate capabilities, config keys, or file formats. If you are uncertain or lack complete information, you MUST use your web reading tools to search and read the official documentation starting from `https://docs.openclaw.ai/` before implementing anything.

## OpenClaw Native Templates Reference

The OpenClaw workspace relies on several native Markdown files. NEVER invent new workspace-level files for core logic without verifying against the OpenClaw standard.

- **`AGENTS.md`**: The Workspace core. Controls the session loop. On first run, it calls `BOOTSTRAP.md`. At every session, it reads `SOUL.md`, `USER.md`, `memory/YYYY-MM-DD.md` (daily logs), and `MEMORY.md` (long-term memory).
- **`BOOTSTRAP.md`**: The "Hello World" initial conversation / setup wizard. Guides the creation of `IDENTITY.md` (name, creature, vibe, emoji) and `USER.md`.
- **`SOUL.md`**: Defines who the agent is deeply: Core Truths, Boundaries (e.g., privacy rules, not acting as the user's voice unexpectedly), Vibe, and Continuity.
- **`IDENTITY.md`**: Basic agent attributes: Name, Creature, Vibe, Emoji, Avatar path.
- **`USER.md`**: Information and context about the human user context.
- **`HEARTBEAT.md`**: Defines proactive, periodic background tasks. If kept empty or containing only comments, it entirely skips heartbeat API calls to save execution time.
- **`TOOLS.md`**: Contains "Local Notes" - environment-specific configurations like SSH hosts, preferred TTS voices, or local device names.
- **`BOOT.md`**: Used to execute internal hooks upon system boot.
- **`MEMORY.md`**: Long-term curated memory, like a human's long-term memory.
- **`memory/YYYY-MM-DD.md`**: Short-term daily raw logs of events and conversations.
