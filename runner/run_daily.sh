#!/usr/bin/env bash
# The Shorts of one day: waits for the research of market_trends, exports it, chooses the themes
# (one Claude session) and produces each video in its own Claude session, uploading it as soon as
# it is ready. Root only (MONGO_URI, YouTube credentials). MANUAL_RUN=1 runs a day that already has
# a lock again, skipping the videos that already have READY.
set -uo pipefail

RUN_DATE="${1:-$(date +%F)}"
WORK_DIR="/data/work/$RUN_DATE"
LOCK_FILE="/data/state/$RUN_DATE.lock"
LOG_FILE="/data/logs/$RUN_DATE.log"
PYTHON=/opt/runner/bin/python
VIDEO_COUNT="${VIDEO_COUNT:-7}"

mkdir -p /data/state /data/logs /data/work
chown node:node /data/work /data/logs
# The log of the day is shared with run.sh, which runs as node
touch "$LOG_FILE" && chown node:node "$LOG_FILE"

log() {
  echo "[run_daily $(date '+%F %T')] $*" | tee -a "$LOG_FILE"
}

if [ -e "$LOCK_FILE" ] && [ "${MANUAL_RUN:-0}" != "1" ]; then
  log "Shorts of $RUN_DATE already attempted, skipping"
  exit 0
fi
date '+%F %T' > "$LOCK_FILE" || { echo "cannot create $LOCK_FILE"; exit 1; }

# 1. The research of the day must finish first (status completed or failed in MongoDB)
log "Waiting for the market_trends research of $RUN_DATE"
$PYTHON /app/research.py wait "$RUN_DATE" >> "$LOG_FILE" 2>&1
wait_code=$?
if [ "$wait_code" != "0" ]; then
  log "No research to use today (code $wait_code), no Shorts for $RUN_DATE"
  exit 0
fi

mkdir -p "$WORK_DIR" && chown node:node "$WORK_DIR"
$PYTHON /app/research.py export "$RUN_DATE" "$WORK_DIR/research" >> "$LOG_FILE" 2>&1 \
  || { log "Could not export the research"; exit 1; }
chown -R node:node "$WORK_DIR/research"

# 2. Themes (one per list of part 11)
if ! jq -e ".videos | length == $VIDEO_COUNT" "$WORK_DIR/pauta.json" >/dev/null 2>&1; then
  /app/run.sh pauta "$RUN_DATE"
fi
if ! jq -e ".videos | length >= 1" "$WORK_DIR/pauta.json" >/dev/null 2>&1; then
  log "pauta.json missing or invalid, no Shorts for $RUN_DATE"
  exit 1
fi
count=$(jq '.videos | length' "$WORK_DIR/pauta.json")
[ "$count" -gt "$VIDEO_COUNT" ] && count=$VIDEO_COUNT
log "Producing $count Shorts"

# 3. One Claude session per video; each finished video is uploaded right away
for index in $(seq 1 "$count"); do
  video_dir="$WORK_DIR/videos/$(printf '%02d' "$index")"
  if [ -e "$video_dir/READY" ]; then
    log "Video $index already produced"
  else
    /app/run.sh video "$RUN_DATE" "$index"
  fi
  if [ -e "$video_dir/READY" ]; then
    $PYTHON /app/publish.py --record "$video_dir" produced >> "$LOG_FILE" 2>&1
    $PYTHON /app/publish.py "$video_dir" >> "$LOG_FILE" 2>&1
  else
    reason=$(cat "$video_dir/FAILED" 2>/dev/null || echo "READY was not created")
    log "Video $index failed: $reason"
    $PYTHON /app/publish.py --record "$video_dir" failed "$reason" >> "$LOG_FILE" 2>&1
  fi
done
log "Shorts of $RUN_DATE finished"
