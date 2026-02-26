# ---------------------------------------------------------
# STAGE 1: Compiler (Builds the Markdown from Python logic)
# ---------------------------------------------------------
FROM ghcr.io/openclaw/openclaw:latest AS builder
USER root

# Install python to run our sync script
RUN apt-get update -qq && apt-get install -y --no-install-recommends python3

WORKDIR /build
COPY . /build/

# Run the sync script to automatically prepare the SKILL.md file
RUN python3 tools/sync_platforms.py

# ---------------------------------------------------------
# STAGE 2: Production Runtime (Clean Image)
# ---------------------------------------------------------
FROM ghcr.io/openclaw/openclaw:latest

USER root

# Install only the runtime dependencies (pip and Python packages)
COPY requirements.txt /tmp/requirements.txt
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends python3-pip && \
    pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /tmp/requirements.txt

# Prep the state dir and bot app dir with correct permissions
RUN mkdir -p /home/node/.openclaw /home/node/what-watch-bot && \
    chown -R node:node /home/node/.openclaw /home/node/what-watch-bot

# Copy the COMPILED code from the builder stage (contains the unified SKILL.md)
# This excludes `tools/` and everything else we don't need at runtime!
COPY --from=builder /build/skills/what-watch-bot/ /home/node/what-watch-bot/

RUN chown -R node:node /home/node/what-watch-bot

# Switch back to the default non-root user
USER node
