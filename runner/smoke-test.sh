#!/usr/bin/env bash
# Manual test of the video chain without Claude: narration, render, frames and thumbnail of a tiny
# example video. Run as root: docker exec youtube-dark /app/smoke-test.sh
# The result stays in /data/work/teste-<timestamp>/videos/01 (nothing is uploaded).
set -euo pipefail

source /app/run-as-claude-user.sh

VIDEO_DIR="/data/work/teste-$(date +%Y%m%d-%H%M%S)/videos/01"
mkdir -p "$VIDEO_DIR"
cat > "$VIDEO_DIR/video.json" <<'JSON'
{
  "palette": "neon",
  "voice": "pt-BR-AntonioNeural",
  "rate": "+12%",
  "music": null,
  "scenes": [
    {"type": "hook", "text": "Isso está bombando no Japão", "highlight": ["Japão"], "emoji": "🤯", "sfx": "boom",
     "narration": "Isso está bombando no Japão, e quase ninguém no Brasil sabe."},
    {"type": "stat", "value": 300, "prefix": "+", "suffix": "%", "label": "de buscas em seis meses", "emoji": "📈", "sfx": "riser", "palette": "sunset",
     "narration": "As buscas cresceram trezentos por cento em seis meses."},
    {"type": "compare", "title": "Lá fora × Brasil", "left": {"title": "Japão", "emoji": "🇯🇵", "items": ["Milhares de lojas", "Assinatura mensal"]},
     "right": {"title": "Brasil", "emoji": "🇧🇷", "items": ["Quase ninguém", "Espaço aberto"]}, "sfx": "whoosh", "palette": "ocean",
     "narration": "Lá já tem milhares de lojas. Aqui, quase ninguém faz."},
    {"type": "journey", "from": {"flag": "🇯🇵", "label": "Japão"}, "to": {"flag": "🇧🇷", "label": "Brasil"}, "text": "Próxima parada", "highlight": ["parada"], "emoji": "✈️", "sfx": "whoosh", "palette": "candy",
     "narration": "E a próxima parada pode ser o Brasil."},
    {"type": "cta", "text": "Quer ver antes de todo mundo?", "subtext": "Segue o canal", "emoji": "🔔", "sfx": "ding", "palette": "fire",
     "narration": "Segue pra ver a próxima tendência antes de todo mundo."}
  ]
}
JSON
cat > "$VIDEO_DIR/thumbnail.json" <<'JSON'
{"title": "Isso vai chegar no Brasil", "highlight": ["Brasil"], "emoji": "🚀", "badge": "🇯🇵 → 🇧🇷", "palette": "sunset"}
JSON
python3 /app/studio/tools/prepare.py "$VIDEO_DIR"
bash /app/studio/tools/render.sh "$VIDEO_DIR"
bash /app/studio/tools/frames.sh "$VIDEO_DIR" 0.5 3 6 9
bash /app/studio/tools/thumbnail.sh "$VIDEO_DIR"
python3 /app/studio/tools/youtube_search.py search "tendências de negócio" --limit 3 --shorts
echo "OK: $VIDEO_DIR"
