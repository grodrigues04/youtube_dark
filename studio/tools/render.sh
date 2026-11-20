#!/usr/bin/env bash
# Renders <video_dir>/video.mp4 from props.json (run prepare.py first) and checks the duration.
# Uses <video_dir>/remotion when the video has custom scenes (see custom-studio.sh), otherwise
# the shared studio in /app/studio/remotion.
set -euo pipefail

VIDEO_DIR=$(realpath "${1:?usage: render.sh <video_dir>}")
MAX_SECONDS="${MAX_VIDEO_SECONDS:-58}"
STUDIO="/app/studio/remotion"
[ -d "$VIDEO_DIR/remotion/src" ] && STUDIO="$VIDEO_DIR/remotion"
[ -s "$VIDEO_DIR/props.json" ] || { echo "ERRO: $VIDEO_DIR/props.json não existe, rode prepare.py antes"; exit 2; }

cd "$STUDIO"
npx remotion render src/index.ts Short "$VIDEO_DIR/video.mp4" \
  --props="$VIDEO_DIR/props.json" \
  --public-dir="$VIDEO_DIR/assets" \
  --concurrency="${RENDER_CONCURRENCY:-4}" \
  --log=warn

seconds=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO_DIR/video.mp4")
size=$(du -h "$VIDEO_DIR/video.mp4" | cut -f1)
echo "OK: $VIDEO_DIR/video.mp4 (${seconds}s, $size)"
if awk -v seconds="$seconds" -v max="$MAX_SECONDS" 'BEGIN { exit !(seconds > max + 0.5) }'; then
  echo "ERRO: o vídeo tem ${seconds}s, o máximo é ${MAX_SECONDS}s"
  exit 2
fi
