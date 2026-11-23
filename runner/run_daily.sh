#!/usr/bin/env bash
# The Short of one day, made from the latest complete research (edition A of market_trends):
# exports it, chooses one theme never used before (one Claude session), produces the video (another
# Claude session) and uploads it scheduled for 08:00. Root only (MONGO_URI, YouTube credentials).
# MANUAL_RUN=1 runs a day that already has a lock again, skipping what is already done.
set -uo pipefail

RUN_DATE="${1:-$(date +%F)}"
WORK_DIR="/data/work/$RUN_DATE"
VIDEO_DIR="$WORK_DIR/videos/01"
LOCK_FILE="/data/state/$RUN_DATE.lock"
LOG_FILE="/data/logs/$RUN_DATE.log"
PYTHON=/opt/runner/bin/python

mkdir -p /data/state /data/logs /data/work
chown node:node /data/work /data/logs
# The log of the day is shared with run.sh, which runs as node
touch "$LOG_FILE" && chown node:node "$LOG_FILE"

log() {
  echo "[run_daily $(date '+%F %T')] $*" | tee -a "$LOG_FILE"
}

if [ -e "$LOCK_FILE" ] && [ "${MANUAL_RUN:-0}" != "1" ]; then
  log "Short of $RUN_DATE already attempted, skipping"
  exit 0
fi
date '+%F %T' > "$LOCK_FILE" || { echo "cannot create $LOCK_FILE"; exit 1; }

# 1. The latest complete research (a new one every Thursday night)
mkdir -p "$WORK_DIR" && chown node:node "$WORK_DIR"
research_date=$($PYTHON /app/research.py export-latest "$WORK_DIR/research" 2>> "$LOG_FILE")
if [ -z "$research_date" ]; then
  log "No complete research (edition A) to use, no Short for $RUN_DATE"
  exit 0
fi
chown -R node:node "$WORK_DIR/research"
log "Using the research of $research_date"

# 2. One theme, never used before
if ! jq -e '.videos | length >= 1' "$WORK_DIR/pauta.json" >/dev/null 2>&1; then
  /app/run.sh pauta "$RUN_DATE"
fi
if ! jq -e '.videos | length >= 1' "$WORK_DIR/pauta.json" >/dev/null 2>&1; then
  log "pauta.json missing or invalid, no Short for $RUN_DATE"
  exit 1
fi

# 3. The video, then the upload (private, published by YouTube at 08:00)
if [ -e "$VIDEO_DIR/READY" ]; then
  log "Video already produced"
else
  /app/run.sh video "$RUN_DATE" 1
fi
if [ -e "$VIDEO_DIR/READY" ]; then
  $PYTHON /app/publish.py --record "$VIDEO_DIR" produced >> "$LOG_FILE" 2>&1
  $PYTHON /app/publish.py "$VIDEO_DIR" >> "$LOG_FILE" 2>&1
else
  reason=$(cat "$VIDEO_DIR/FAILED" 2>/dev/null || echo "READY was not created")
  log "Video failed: $reason"
  $PYTHON /app/publish.py --record "$VIDEO_DIR" failed "$reason" >> "$LOG_FILE" 2>&1
fi
log "Short of $RUN_DATE finished"
