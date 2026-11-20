#!/usr/bin/env bash
# Copies the studio into <video_dir>/remotion so this video can have custom scene components
# (edit src/scenes, src/types.ts). node_modules is shared through a symlink. render.sh,
# frames.sh and thumbnail.sh use the copy automatically.
set -euo pipefail

VIDEO_DIR=$(realpath "${1:?usage: custom-studio.sh <video_dir>}")
mkdir -p "$VIDEO_DIR/remotion"
cp -r /app/studio/remotion/src /app/studio/remotion/package.json /app/studio/remotion/tsconfig.json \
  /app/studio/remotion/remotion.config.ts "$VIDEO_DIR/remotion/"
ln -sfn /app/studio/remotion/node_modules "$VIDEO_DIR/remotion/node_modules"
echo "OK: $VIDEO_DIR/remotion (rode 'npx tsc --noEmit' lá dentro depois de editar)"
