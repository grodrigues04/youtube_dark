"""Turns video.json (written by Claude) into narration audio + props.json for the render.

Usage: prepare.py <video_dir>

For every scene: validates the fields, generates the pt-BR narration with edge-tts (one mp3 per
scene in <video_dir>/assets/) with word timings for the captions, and sets the scene duration to
the narration length. Copies the sound effects and the chosen music. Fails (exit 2) with a clear
message when something is wrong, including a total above MAX_SECONDS: shorten the narration and
run again.
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import edge_tts

FPS = 30
MAX_SECONDS = float(os.environ.get("MAX_VIDEO_SECONDS") or "58")
SCENE_PADDING_SECONDS = 0.18
MIN_SCENE_SECONDS = 1.2
SFX_DIR = Path(os.environ.get("SFX_DIR") or "/app/studio/sfx")
MUSIC_DIR = Path(os.environ.get("MUSIC_DIR") or "/music")
PALETTES = {"neon", "sunset", "ocean", "candy", "lime", "fire"}
SFX = {"whoosh", "pop", "ding", "riser", "boom"}
VOICES = {"pt-BR-AntonioNeural", "pt-BR-FranciscaNeural", "pt-BR-ThalitaMultilingualNeural"}

# Required fields of each scene type, besides `narration` (see remotion/src/types.ts)
REQUIRED_FIELDS = {
    "hook": ["text"],
    "statement": ["title"],
    "stat": ["value", "label"],
    "list": ["title", "items"],
    "compare": ["left", "right"],
    "journey": ["from", "to", "text"],
    "steps": ["title", "steps"],
    "question": ["text"],
    "reveal": ["teaser", "reveal"],
    "cta": ["text"],
}


class SpecError(Exception):
    pass


def validate(spec: dict) -> None:
    if spec.get("palette", "neon") not in PALETTES:
        raise SpecError(f"palette deve ser uma de {sorted(PALETTES)}")
    if spec.get("voice", "pt-BR-AntonioNeural") not in VOICES:
        raise SpecError(f"voice deve ser uma de {sorted(VOICES)}")
    scenes = spec.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SpecError("scenes precisa ser uma lista com pelo menos uma cena")
    for index, scene in enumerate(scenes, start=1):
        scene_type = scene.get("type")
        if scene_type not in REQUIRED_FIELDS:
            raise SpecError(f"cena {index}: type deve ser um de {sorted(REQUIRED_FIELDS)}")
        missing = [field for field in ["narration", *REQUIRED_FIELDS[scene_type]] if not scene.get(field)]
        if missing:
            raise SpecError(f"cena {index} ({scene_type}): faltam os campos {missing}")
        if scene.get("palette") and scene["palette"] not in PALETTES:
            raise SpecError(f"cena {index}: palette deve ser uma de {sorted(PALETTES)}")
        if scene.get("sfx") and scene["sfx"] not in SFX:
            raise SpecError(f"cena {index}: sfx deve ser um de {sorted(SFX)} ou null")
        if scene_type == "stat" and not isinstance(scene["value"], (int, float)):
            raise SpecError(f"cena {index}: value precisa ser número (o texto vai em prefix/suffix)")
        if scene_type == "list":
            scene["items"] = [item if isinstance(item, dict) else {"text": str(item)} for item in scene["items"]]
    if scenes[0]["type"] not in ("hook", "question", "reveal", "statement", "stat", "journey"):
        raise SpecError("a primeira cena precisa prender a atenção: use hook, question, reveal, stat, statement ou journey")


def audio_seconds(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def clean_caption(text: str) -> str:
    return re.sub(r"^[^\w$R%]+|[^\w%]+$", "", text, flags=re.UNICODE) or text


async def narrate(text: str, voice: str, rate: str, output: Path) -> list[dict]:
    communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with output.open("wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000_000
                end = (chunk["offset"] + chunk["duration"]) / 10_000_000
                words.append({"text": clean_caption(chunk["text"]), "start": start, "end": end})
    return words


async def prepare(video_dir: Path) -> None:
    spec = json.loads((video_dir / "video.json").read_text(encoding="utf-8"))
    validate(spec)
    assets = video_dir / "assets"
    shutil.rmtree(assets, ignore_errors=True)
    (assets / "sfx").mkdir(parents=True)
    for sfx in SFX_DIR.glob("*.wav"):
        shutil.copy(sfx, assets / "sfx" / sfx.name)

    music = spec.get("music")
    if music:
        source = MUSIC_DIR / music
        if not source.is_file():
            raise SpecError(f"música {music} não existe em {MUSIC_DIR} (use null para sem música)")
        (assets / "music").mkdir()
        shutil.copy(source, assets / "music" / music)

    voice = spec.get("voice", "pt-BR-AntonioNeural")
    rate = spec.get("rate", "+10%")
    scenes = []
    report = []
    for index, scene in enumerate(spec["scenes"], start=1):
        audio_name = f"narration-{index:02d}.mp3"
        words = await narrate(scene["narration"], voice, rate, assets / audio_name)
        seconds = max(audio_seconds(assets / audio_name) + SCENE_PADDING_SECONDS, MIN_SCENE_SECONDS)
        duration = round(seconds * FPS)
        scene = {
            **scene,
            "audio": audio_name,
            "durationInFrames": duration,
            "words": [
                {"text": word["text"], "startFrame": round(word["start"] * FPS), "endFrame": max(round(word["end"] * FPS), round(word["start"] * FPS) + 1)}
                for word in words
            ],
        }
        scenes.append(scene)
        report.append(f"  cena {index:>2} {scene['type']:<9} {seconds:5.1f}s  {scene['narration'][:70]}")

    total = sum(scene["durationInFrames"] for scene in scenes) / FPS
    print("\n".join(report))
    print(f"  TOTAL {total:.1f}s (máximo {MAX_SECONDS:.0f}s)")
    if total > MAX_SECONDS:
        raise SpecError(f"o vídeo ficou com {total:.1f}s: corte {total - MAX_SECONDS:.1f}s de narração e rode de novo")

    props = {
        "fps": FPS,
        "palette": spec.get("palette", "neon"),
        "music": music or None,
        "musicVolume": spec.get("music_volume", 0.12),
        "scenes": scenes,
    }
    (video_dir / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {video_dir / 'props.json'}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    try:
        asyncio.run(prepare(Path(sys.argv[1]).resolve()))
    except SpecError as error:
        print(f"ERRO: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
