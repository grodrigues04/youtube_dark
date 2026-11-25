#!/usr/bin/env bash
# Checks the wall clock every 30 seconds. Every day at 06:00 starts run_daily.sh, which makes one
# Short from the latest completed research of market_trends and uploads it scheduled
# for 08:00. It never waits for a research: it uses the one already saved. If the computer was
# off at 06:00, the day starts as soon as the container is running again, until 06:59 (later than
# that the video would not be ready by 08:00); a day never runs twice (lock in /data/state/).
# Every 10 minutes publish.py retries the uploads that are still pending (quota, network) and
# deletes the media of the videos already uploaded.
#
# Runs as root: run.sh drops to the `node` user before Claude starts.
set -uo pipefail

START_HOUR=6
last_publish=0

echo "[scheduler] started at $(date '+%F %T %Z'), one Short every day at 06:00, published at 08:00"

while true; do
  today=$(date +%F)
  hour=$((10#$(date +%H)))

  if [ "$hour" -eq "$START_HOUR" ] && [ ! -e "/data/state/$today.lock" ]; then
    /app/run_daily.sh "$today"
  fi

  if [ $(( $(date +%s) - last_publish )) -ge 600 ]; then
    /opt/runner/bin/python /app/publish.py >> /data/logs/publish.log 2>&1
    last_publish=$(date +%s)
  fi

  sleep 30
done
