# WhatWatchBot 🎬🍿

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

WhatWatchBot is a powerful Telegram bot designed to help you discover, explore, and find where to stream your next favorite movie or TV series.

> **Architectural Note:** This repository is structured as an **OpenClaw Workspace**. It contains the core configuration for an OpenClaw Agent (`SOUL.md`, `IDENTITY.md`) and a self-contained Python **Skill** located in `skills/what-watch-bot/` which provides the actual movie and TV series recommendation capabilities.

Powered by **OpenClaw** and integrated with various external APIs (TMDB, OMDB, YouTube, Wikipedia), WhatWatchBot understands natural language queries, fetches detailed media information (including ratings and trailers), and guides you directly to the streaming platforms available in your region.

## What it does

- **Natural Language Search:** Ask for movies or series freely in chat (e.g., "Find me a good sci-fi movie from the 80s", or "What should I watch tonight?").
- **Rich Media Info:** Get plots, release dates, cast info, genres, and more.
- **Accurate Ratings:** Pulls data from various sources like IMDb, TMDB, and Metacritic via OMDB to help you pick the best content.
- **Trailers:** Automatically fetches relevant YouTube trailers.
- **Where to Watch:** Tells you exactly where you can stream, rent, or buy the title in your region (powered by JustWatch via TMDB).
  - _Note on Rent/Buy:_ The bot acts as a filter across your existing subscriptions. Activating the Rent/Buy option will show paid content _only_ for the platforms you have already selected (e.g., Amazon Prime Video, Apple TV+), rather than querying purely transactional stores.
  - _Single Source of Truth:_ The supported platforms are managed dynamically. Developers can easily add new providers to `src/utils/platforms.py`, and when rebuilding the Docker image (`docker compose up -d --build`), the build process will automatically trigger the `tools/sync_platforms.py` generator script to update the bot's capabilities and internal prompt tables.
- **Personalized Suggestions:** Keeps track of your watched list and gives recommendations based on your preferences.

---

## 🚀 Getting Started

To run this project, you need Docker installed on your machine. The bot relies on OpenClaw as its core framework.

### 1. Prerequisites (API Keys)

Before starting the setup, you must obtain a few free API keys. The bot uses these to fetch information:

- **TMDB API Key:** Required for searching titles, getting metadata, and finding streaming providers. [Get it here](https://developer.themoviedb.org/docs/getting-started).
- **OMDB API Key:** Required for fetching additional ratings like IMDb and Metacritic. [Get it here](http://www.omdbapi.com/apikey.aspx).
- **YouTube API Key:** Required to find trailers. You need a Google Cloud account with the YouTube Data API v3 enabled. [Get it here](https://console.cloud.google.com/).

### 2. Configuration Setup

Clone the repository and prepare your environment variables:

```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Open .env and fill in your API keys
nano .env
```

### 3. Running the Project

The project is structured with separate Docker Compose files for Development and Production to ensure data safety and best practices.

**For Local Development (Default):**
Start the Docker container in detached mode:

```bash
docker compose up -d
```

_Note: This automatically uses `docker-compose.override.yml` behind the scenes to enable hot-reloading (Bind Mounts) and creates a local `./db` folder for your SQLite database._

**For Production Deployment:**
When deploying to a server, you must explicitly use the production configuration to ensure the code is sealed within the image and your local SQLite database is kept safe in a Named Volume:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Both scenarios will automatically **build** a local Docker image from the included `Dockerfile` (which pre-installs all required Python dependencies) and start the service.

> [!NOTE]
> If you pull an update and want to rebuild the image, run `docker compose up -d --build`.

### 4. Restore Development Tools (IDE Skills)

This project uses Antigravity Agent abilities (workflows, testing patterns) tracked via `skills-lock.json` to help you develop the codebase inside your IDE.
_(Note: These are tools for the developer's AI assistant, NOT the runtime skills injected into the WhatWatchBot)._

To restore them after cloning:

```bash
npx skills experimental_install
```

### 5. ⚠️ CRITICAL: OpenClaw Onboarding & Setup

> **CLI Command Preface:** Whenever the official OpenClaw documentation says to run an `openclaw` command, you must execute it _inside_ the container if you are using Docker. For the rest of this guide, the local equivalent of the native `openclaw` CLI command is:
> `docker exec -it what-watch-openclaw node dist/index.js`

Once the container is running, you must configure your OpenClaw agent and connect it to a messaging platform. WhatWatchBot can technically be connected to any platform supported by OpenClaw, but it has been tested for **Telegram**.

The OpenClaw setup wizard is generally fully guided. If you choose to use Telegram, you can follow the prerequisite steps below to prepare your bot, but always refer to the [official OpenClaw Channels documentation](https://docs.openclaw.ai/channels) as procedures might change in the future.

**Prerequisite (If using Telegram):**

1. Go to Telegram and message [@BotFather](https://t.me/BotFather).
2. Send the command `/newbot`, choose a name and a username for your bot.
3. Save the **HTTP API Token** provided by BotFather.
4. **Important**: Send `/setcommands` to BotFather, select your bot, and paste the list of commands found in the `BOT_COMMANDS.md` file so users see the interactive menu.

5. Open your terminal and run the onboarding command:

   ```bash
   docker exec -it what-watch-openclaw node dist/index.js onboard
   ```

   _Follow the interactive prompt. When asked, paste the Telegram Token you just got from BotFather and select the `what-watch-bot` skill._

6. **During the Onboarding Wizard:**
   The wizard will ask you a series of questions to configure the agent. Here are some guidelines:
   - **Security Warning:** Please read the security warning carefully and accept it if you agree to proceed.
   - **Onboarding mode:** `QuickStart` is recommended.
   - **Config handling:** If the wizard says "Existing config detected", select `Update values` to proceed.
   - **Model provider:** Choose your preferred AI model. You do not need a heavy or expensive model; a fast model like Google `gemini-3-flash` works perfectly for this bot.
   - **Target channel:** Choose the platform you want the bot on (e.g., `Telegram (Bot API)`). You will be asked to insert the Bot Token here.
   - **Hooks:** I recommend selecting `session-memory` and `command-logger`. You do not need `boot-md` as the bot identity is natively configured.
   - **Hatch your bot:** You can select `Do this later`.

> [!TIP]
> **Wizard Timeouts & Manual Pairing (Frequent in Docker):**
>
> - Whether you are installing the bot for the first time or recreating the container from scratch (`docker compose down -v`), the wizard might exit halfway after you paste the token. This is normal! Simply run the `onboard` command again to resume.
> - **Device Pairing Code:** After the wizard, send a message to your bot on your chosen platform (Telegram, WhatsApp, etc.). The bot will likely reply with an `"OpenClaw: access not configured"` error and provide you with a **Pairing code** (e.g., `A1B2C3D4`).
> - You **must** approve this device manually using the pairing command:
>   - 👉 `docker exec -it what-watch-openclaw node dist/index.js pairing approve <channel_name> <YOUR_CODE>`
>   - _(e.g. replace `<channel_name>` with `telegram`, `whatsapp`, `discord`)_
>   - Once approved, the bot will start replying.
>   - For more details, refer to the [official OpenClaw Pairing Docs](https://docs.openclaw.ai/channels/pairing).

> [!CAUTION]
> **Web UI Access via Docker:**
> At the end of the wizard, OpenClaw will output a Web UI URL for the dashboard. **If it shows an internal Docker IP (e.g., `http://172.x.x.x:18789/`), this link will not work directly on your Mac.**
> To access the dashboard, you must replace the IP with `localhost`:
> 👉 `http://localhost:18789/`
>
> **Browser Compatibility:** The OpenClaw Web UI relies on modern WebSockets and is currently optimized for **Google Chrome**. If it fails to load or connect via Firefox, switch to Chrome.

## 📁 Project Structure

This repository uses the official **OpenClaw Workspace Paradigm**. The root directory configures the Agent, while the Python code is contained within a specific Skill folder.

- **`IDENTITY.md`** & **`SOUL.md`**: Define the agent's core character, base instructions, tone, and language mapping.
- **`skills/what-watch-bot/`**: The standalone technical skill providing the bot's abilities.
  - `src/`: Core logic and API integrations (`tmdb.py`, `omdb.py`, `database.py`, etc.).
  - `scripts/`: CLI entrypoints used by OpenClaw to trigger the bot's abilities.
  - `tests/`: Unit tests isolating and verifying the Python logic independent of the Agent.
  - `SKILL.md`: The technical manual mapping slash commands to Python scripts.
- **`docker-compose.yml`**: Docker configuration defining the Gateway architecture.
- **`db/`**: Local binding for the SQLite database tracking user preferences.

## 🛠️ Development Workflow: Applying Changes

Since this project follows a strict container isolation pattern (no Workspace bind mounts), changes to the **Bot Core Logic** are not reflected in real-time within the running container.

"Bot Core Logic" refers to the files that define the bot's behavior and abilities:

- **`SOUL.md`**: Core instructions and persona.
- **`IDENTITY.md`**: Bot branding and identity.
- **`skills/what-watch-bot/SKILL.md`**: Slash command mapping and technical manual.

To apply changes made to these files, you must rebuild the Docker image:

```bash
# Rebuild the image and restart the container in the background
docker compose up -d --build
```

> [!IMPORTANT]
> **Skill Reloading:** To ensure OpenClaw uses the latest version of your `SKILL.md` instructions **after** rebuilding the container, you MUST explicitly tell the bot in your chat (e.g., Telegram) to _"reload your skill"_ or _"read your skill again"_. This forces the agent to refresh its internal configuration for the active session.
>
> **Sync Bot Commands:** After a rebuild, you should also re-synchronize the bot commands with Telegram. Use the `/setcommands` command in [@BotFather](https://t.me/BotFather) and paste the list from [BOT_COMMANDS.md](./BOT_COMMANDS.md).

---

## 🧪 Testing

This project uses `pytest` for automated testing, ensuring the core logics (pagination, SQLite caching, API fallbacks) are stable without making real network requests. Tests are isolated within the skill folder.

To run the test suite and check code coverage:

```bash
# 1. Install testing dependencies (if not already installed)
pip install -r requirements.txt

# 2. Run the full test suite
cd skills/what-watch-bot
PYTHONPATH=. pytest tests/ -v --cov=src --cov-report=term-missing
```
