#!/usr/bin/env bash
# Renders <video_dir>/thumbnail.jpg (1080x1920) from <video_dir>/thumbnail.json and checks the
# 2MB limit of YouTube.
set -euo pipefail

VIDEO_DIR=$(realpath "${1:?usage: thumbnail.sh <video_dir>}")
STUDIO="/app/studio/remotion"
[ -d "$VIDEO_DIR/remotion/src" ] && STUDIO="$VIDEO_DIR/remotion"
[ -s "$VIDEO_DIR/thumbnail.json" ] || { echo "ERRO: $VIDEO_DIR/thumbnail.json não existe"; exit 2; }

cd "$STUDIO"
npx remotion still src/index.ts Thumbnail "$VIDEO_DIR/thumbnail.jpg" \
  --props="$VIDEO_DIR/thumbnail.json" --image-format=jpeg --jpeg-quality=88 --log=error

bytes=$(stat -c %s "$VIDEO_DIR/thumbnail.jpg")
[ "$bytes" -lt 2000000 ] || { echo "ERRO: thumbnail com $bytes bytes, o limite do YouTube é 2MB"; exit 2; }
echo "OK: $VIDEO_DIR/thumbnail.jpg ($bytes bytes)"
