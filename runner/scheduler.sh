#!/usr/bin/env bash
# Checks the wall clock every 30 seconds. From 05:00 on, once a day, starts run_daily.sh, which
# waits for the market_trends research of the day to finish and then produces the Shorts. If the
# computer was off at 05:00, the day starts as soon as the container is running again (until
# 22:59); a day never runs twice (lock in /data/state/). Every 10 minutes publish.py retries the
# uploads that are still pending (quota, network, missing credentials).
#
# Runs as root: run.sh drops to the `node` user before Claude starts.
set -uo pipefail

FIRST_HOUR="${FIRST_HOUR:-5}"
LAST_HOUR="${LAST_HOUR:-22}"
last_publish=0

echo "[scheduler] started at $(date '+%F %T %Z'), Shorts are produced every day after the 05:00 research"

while true; do
  today=$(date +%F)
  hour=$((10#$(date +%H)))

  if [ "$hour" -ge "$FIRST_HOUR" ] && [ "$hour" -le "$LAST_HOUR" ] \
     && [ ! -e "/data/state/$today.lock" ]; then
    /app/run_daily.sh "$today"
  fi

  if [ $(( $(date +%s) - last_publish )) -ge 600 ]; then
    /opt/runner/bin/python /app/publish.py >> /data/logs/publish.log 2>&1
    last_publish=$(date +%s)
  fi

  sleep 30
done
