# WhatWatchBot 🎬🍿

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

WhatWatchBot is a powerful Telegram bot designed to help you discover, explore, and find where to stream your next favorite movie or TV series.

Powered by **OpenClaw** and integrated with various external APIs (TMDB, OMDB, YouTube, Wikipedia), WhatWatchBot understands natural language queries, fetches detailed media information (including ratings and trailers), and guides you directly to the streaming platforms available in your region.

## What it does

- **Natural Language Search:** Ask for movies or series freely in chat (e.g., "Find me a good sci-fi movie from the 80s", or "What should I watch tonight?").
- **Rich Media Info:** Get plots, release dates, cast info, genres, and more.
- **Accurate Ratings:** Pulls data from sources like Rotten Tomatoes via OMDB to help you pick the best content.
- **Trailers:** Automatically fetches relevant YouTube trailers.
- **Where to Watch:** Tells you exactly where you can stream, rent, or buy the title in your region (powered by JustWatch via TMDB).
- **Personalized Suggestions:** Keeps track of your watched list and gives recommendations based on your preferences.

---

## 🚀 Getting Started

To run this project, you need Docker installed on your machine. The bot relies on OpenClaw as its core framework.

### 1. Prerequisites (API Keys)

Before starting the setup, you must obtain a few free API keys. The bot uses these to fetch information:

- **TMDB API Key:** Required for searching titles, getting metadata, and finding streaming providers. [Get it here](https://developer.themoviedb.org/docs/getting-started).
- **OMDB API Key:** Required for fetching Rotten Tomatoes ratings. [Get it here](http://www.omdbapi.com/apikey.aspx).
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
When deploying to a server, you must explicitly use the production configuration to ensure the code is sealed within the image and data is kept safe in Named Volumes:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Both scenarios will automatically **build** a local Docker image from the included `Dockerfile` (which pre-installs all required Python dependencies) and start the service.

> [!NOTE]
> The first `docker compose up -d` takes slightly longer because it builds the image. Subsequent runs are instant. If you pull an update and want to rebuild the image, run `docker compose up -d --build`.

### 4. Restore Agent Skills

This project uses agent skills tracked via `skills-lock.json`. To restore them after cloning:

```bash
npx skills experimental_install
```

> [!NOTE]
> If you create a custom skill in this folder, it will not be committed. Skills installed from the official registry are not committed and must be restored with the command above.

### 5. ⚠️ CRITICAL: OpenClaw Onboarding & Setup

Once the container is running, **you must onboard your own Telegram bot into OpenClaw**.

> **Note:** You cannot use the original WhatWatchBot Telegram account. You need to create your own!
>
> 1. Go to Telegram and message [@BotFather](https://t.me/BotFather).
> 2. Send the command `/newbot`, choose a name and a username for your bot.
> 3. Save the **HTTP API Token** provided by BotFather. You will need it in the next step!
> 4. **Important**: Send `/setcommands` to BotFather, select your bot, and paste the list of commands found in the `BOT_COMMANDS.md` file. This is crucial for the bot to show the interactive menu.

DO NOT manually edit Telegram keys or sessions. It's highly recommended to use the internal setup process:

1. Open your terminal and connect to the running container:
   ```bash
   docker exec -it what-watch-openclaw bash
   ```
2. Run the onboarding command:

   ```bash
   node dist/index.js onboard
   ```

   _Follow the interactive prompt. When asked, paste the Telegram Token you just got from BotFather and select the `what-watch-bot` skill._

3. Ensure the `what-watch-bot` skill is properly registered in OpenClaw. OpenClaw needs to know this folder contains a skill.

   **During the Onboarding Wizard:**
   - Security Warning: type `y` (Yes)
   - Onboarding mode: choose `QuickStart`
   - Config handling: choose `Use existing values` (or `Update values` to review)
   - Model provider: choose your preferred model (e.g., Google `gemini-3-flash`)
   - **Hooks (CRITICAL):** Use the Spacebar to enable the following 4 hooks before pressing Enter:
     - `[x] boot-md` (CRITICAL: Loads the SKILL.md identity immediately)
     - `[x] bootstrap-extra-files` (Links your project's scripts to the agent)
     - `[x] command-logger` (For debugging and terminal logs)
     - `[x] session-memory` (For context retention and chat history)
   - When asked "How do you want to hatch your bot?", choose `Do this later`.

> [!CAUTION]
> **Web UI Access via Docker:**
> At the end of the wizard, OpenClaw will output a Web UI URL containing an internal Docker IP (e.g., `http://172.x.x.x:18789/`). **This link will not work directly on your Mac.**
> To access the dashboard, you must replace the IP with `localhost`:
> 👉 `http://localhost:18789/`
>
> **Browser Compatibility:** The OpenClaw Web UI relies on modern WebSockets and is currently optimized for **Google Chrome**. If it fails to load or connect via Firefox, switch to Chrome.

## 📁 Project Structure

The project is organized as follows:

- **`src/`**: Contains the core logic and integrations.
  - `api/`: API modules (`tmdb.py`, `omdb.py`, `youtube.py`, `wikipedia.py`).
  - `utils/`: Utilities for formatting messages (`formatters.py`), handling pagination (`pagination.py`), and platform mapping (`platforms.py`).
  - `database.py`: SQLite logic for tracking watched movies and user preferences.
  - `config.py`: Centralized configuration mapping the `.env` file constants.
- **`scripts/`**: Lightweight CLI entrypoints that OpenClaw calls when triggering the bot's abilities (e.g., `search.py`, `search_title.py`, `fetch_plot.py`).
- **`SKILL.md`**: The brain of the bot. This file defines the agent's instructions, prompts, and how it maps natural language to the internal `scripts/`.
- **`docker-compose.yml`**: The Docker configuration to run the OpenClaw host.

---

## 🧪 Testing

This project uses `pytest` for automated testing, ensuring the core logics (pagination, SQLite caching, API fallbacks) are stable without making real network requests.

To run the test suite and check code coverage:

```bash
# 1. Install testing dependencies (if not already installed)
pip install -r requirements.txt

# 2. Run the full test suite
pytest tests/ -v --cov=src --cov-report=term-missing
```
