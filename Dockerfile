# Extends the base OpenClaw image and adds the Python dependencies
# required by the bot's scripts using pip for pinned version control.
FROM ghcr.io/openclaw/openclaw:latest

USER root

# Install pip, then install pinned Python dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends python3-pip && \
    pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /tmp/requirements.txt

# Switch back to the default non-root user
USER node
