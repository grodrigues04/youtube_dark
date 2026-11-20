#!/usr/bin/env bash
# Exports frames of the rendered composition for visual QA: frames.sh <video_dir> <second> [...]
# Writes <video_dir>/qa/frame-<second>s.jpg; open them with the Read tool to look at them.
set -euo pipefail

VIDEO_DIR=$(realpath "${1:?usage: frames.sh <video_dir> <second> [<second> ...]}")
shift
STUDIO="/app/studio/remotion"
[ -d "$VIDEO_DIR/remotion/src" ] && STUDIO="$VIDEO_DIR/remotion"
mkdir -p "$VIDEO_DIR/qa"

cd "$STUDIO"
for second in "$@"; do
  frame=$(awk -v second="$second" 'BEGIN { printf "%d", second * 30 }')
  npx remotion still src/index.ts Short "$VIDEO_DIR/qa/frame-${second}s.jpg" \
    --frame="$frame" --props="$VIDEO_DIR/props.json" --public-dir="$VIDEO_DIR/assets" \
    --image-format=jpeg --jpeg-quality=70 --scale=0.5 --log=error
  echo "$VIDEO_DIR/qa/frame-${second}s.jpg"
done
