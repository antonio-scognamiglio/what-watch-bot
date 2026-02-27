---
trigger: always_on
description: "Rules for language and localization consistency"
---

# Localization & Language Rules

- **Single Source of Truth (English)**: All "core" logic documentation, manifests, and instructions (specifically `SKILL.md`, `SOUL.md`, `IDENTITY.md`) MUST be written entirely in English.
- **Dynamic Translation**: The OpenClaw agent is responsible for translating the final output to the user's language based on their `USER.md` profile and specific localization instructions provided in the manifest.
- **No Hardcoded Non-English Strings**: Do NOT hardcode non-English strings (e.g., Italian) directly into `SKILL.md` instructions or placeholders unless they are explicitly marked as `[Translated phrase for ...]`.
- **Placeholder Pattern**: Use English for all instruction-level messages (e.g., "Not available" instead of "Non disponibile"). The agent will automatically provide the localized version during the session.
