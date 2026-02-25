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

Start the Docker container in detached mode:

```bash
docker compose up -d
```

This will automatically **build** a local Docker image from the included `Dockerfile` (which pre-installs all required Python dependencies) and start the service. A Docker named volume is created automatically to persist your configuration, session data, and cache.

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

---

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
