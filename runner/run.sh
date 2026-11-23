#!/usr/bin/env bash
# Runs one Claude session as `node`:
#   run.sh pauta <date>          chooses the theme of the day → /data/work/<date>/pauta.json
#   run.sh video <date> <index>  produces one Short → /data/work/<date>/videos/<NN>/ (READY)
# Claude runs with --dangerously-skip-permissions: it is a non-root user in a container whose
# environment holds only the Claude token (see run-as-claude-user.sh).
set -uo pipefail

# Never run Claude as root: see run-as-claude-user.sh
source /app/run-as-claude-user.sh

MODE="${1:?usage: run.sh pauta|video <date> [index]}"
RUN_DATE="${2:?usage: run.sh pauta|video <date> [index]}"
WORK_DIR="/data/work/$RUN_DATE"
LOG_FILE="/data/logs/$RUN_DATE.log"
CLAUDE_MODEL="${CLAUDE_MODEL:-claude-opus-5-5}"

log() {
  echo "[run $(date '+%F %T')] $*" | tee -a "$LOG_FILE"
}

render_prompt() {
  sed -e "s/{{DATE}}/$RUN_DATE/g" -e "s/{{INDEX}}/${INDEX:-}/g" "$1"
}

[ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] || { log "CLAUDE_CODE_OAUTH_TOKEN is not set"; exit 1; }

case "$MODE" in
  pauta)
    cd "$WORK_DIR" || exit 1
    PROMPT_FILE=/app/studio/prompts/pauta.md
    TIMEOUT="${CLAUDE_TIMEOUT_PAUTA:-40m}"
    MAX_TURNS=80
    ;;
  video)
    INDEX="${3:?usage: run.sh video <date> <index>}"
    VIDEO_DIR="$WORK_DIR/videos/$(printf '%02d' "$INDEX")"
    mkdir -p "$VIDEO_DIR" && cd "$VIDEO_DIR" || exit 1
    rm -f FAILED
    jq ".videos[$((INDEX - 1))]" "$WORK_DIR/pauta.json" > tema.json
    PROMPT_FILE=/app/studio/prompts/video.md
    TIMEOUT="${CLAUDE_TIMEOUT:-2h}"
    MAX_TURNS=400
    ;;
  *)
    echo "unknown mode $MODE"; exit 1 ;;
esac

log "Claude $MODE ${INDEX:-} (model $CLAUDE_MODEL, timeout $TIMEOUT)"
render_prompt "$PROMPT_FILE" | timeout "$TIMEOUT" claude -p \
  --model "$CLAUDE_MODEL" \
  --max-turns "$MAX_TURNS" \
  --dangerously-skip-permissions \
  --output-format stream-json --verbose \
  >> "claude-$MODE-$(date +%H%M%S).jsonl" 2>> "$LOG_FILE"
exit_code=$?
log "Claude $MODE ${INDEX:-} finished with exit code $exit_code"
if [ "$MODE" = "video" ] && [ ! -e READY ] && [ ! -s FAILED ]; then
  echo "o Claude terminou (código $exit_code) sem criar READY" > FAILED
fi
exit "$exit_code"
