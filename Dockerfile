FROM node:22-bookworm-slim

ENV TZ=America/Sao_Paulo \
    DISABLE_AUTOUPDATER=1 \
    DISABLE_TELEMETRY=1 \
    PYTHONUNBUFFERED=1 \
    REMOTION_DISABLE_TELEMETRY=1

# ffmpeg (audio/duration), fonts with color emoji, libraries of Remotion's headless Chrome
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      jq ca-certificates tzdata coreutils util-linux procps python3 python3-venv ffmpeg \
      fonts-noto-core fonts-noto-color-emoji fonts-noto-cjk \
      libnss3 libdbus-1-3 libatk1.0-0 libgbm1 libasound2 libxrandr2 libxkbcommon0 libxfixes3 \
      libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2 \
 && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code@2.1.328 && npm cache clean --force

# Tools used by Claude (as node): narration and YouTube research
RUN python3 -m venv /opt/tools \
 && /opt/tools/bin/pip install --no-cache-dir "edge-tts==7.3.1" "yt-dlp==2026.10.26"
# Root-only scripts: MongoDB and YouTube upload
RUN python3 -m venv /opt/runner \
 && /opt/runner/bin/pip install --no-cache-dir "pymongo[srv]==4.20.1" \
      "google-api-python-client==2.202.0" "google-auth==2.62.2"

# Video studio (Remotion) with its headless Chrome
COPY studio/remotion/package.json studio/remotion/package-lock.json /app/studio/remotion/
RUN cd /app/studio/remotion && npm ci && npx remotion browser ensure && npm cache clean --force
COPY studio/remotion /app/studio/remotion
COPY studio/tools /app/studio/tools
COPY studio/prompts /app/studio/prompts
RUN bash /app/studio/tools/make_sfx.sh /app/studio/sfx \
 && chmod +x /app/studio/tools/*.sh \
 && chown -R node:node /app/studio

# Subagents (roteirista, critico, pesquisador-youtube, hashtags, thumbnail, titulo)
COPY --chown=node:node studio/agents /home/node/.claude/agents
RUN chown node:node /home/node/.claude

COPY --chmod=755 runner/scheduler.sh runner/run_daily.sh runner/run.sh runner/run-as-claude-user.sh runner/smoke-test.sh /app/
COPY --chmod=644 runner/research.py runner/publish.py /app/

# python3 of Claude's tools first in PATH; root scripts call /opt/runner/bin/python explicitly
ENV PATH="/opt/tools/bin:$PATH" \
    SFX_DIR=/app/studio/sfx \
    MUSIC_DIR=/music

# Starts as root on purpose: see run-as-claude-user.sh
WORKDIR /data
CMD ["/app/scheduler.sh"]
