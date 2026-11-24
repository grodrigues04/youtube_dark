"""Turns video.json (written by Claude) into narration audio + props.json for the render.

Usage: prepare.py <video_dir>

For every scene: validates the fields, generates the pt-BR narration with edge-tts (one mp3 per
scene in <video_dir>/assets/) with word timings for the captions, and sets the scene duration to
the narration length. The pauses of edge-tts are cut out: it leaves ~0.15s of silence before and
~0.75s after every clip, ~0.7s after every period and ~0.25s after every comma, so the narration
sounded slow and robotic. Copies the sound effects and the chosen music. Fails (exit 2) with a
clear message when something is wrong, including a total above MAX_SECONDS: shorten the narration
and run again.
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
MIN_SCENE_SECONDS = 0.8
# Longest silence kept between two words (also between the last word of a scene and the first of
# the next one): none in the hook (the first HOOK_SECONDS), only a breath after it
HOOK_SECONDS = 8.0
HOOK_MAX_GAP_SECONDS = 0.03
MAX_GAP_SECONDS = 0.08
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


def max_gap(video_seconds: float) -> float:
    return HOOK_MAX_GAP_SECONDS if video_seconds < HOOK_SECONDS else MAX_GAP_SECONDS


def tighten(raw: Path, output: Path, words: list[dict], scene_start: float) -> list[dict]:
    """Writes `output` with the pauses of `raw` cut out and returns the word timings shifted to it.

    Keeps half of the allowed gap after each word and half before the next one, so a scene ends
    and the next one starts with the same short gap as two words inside a scene.
    """
    segments = []
    shifted = []
    removed = max(words[0]["start"] - max_gap(scene_start) / 2, 0)
    segment_start = removed
    for index, word in enumerate(words):
        if index > 0:
            previous = words[index - 1]
            gap_limit = max_gap(scene_start + previous["end"] - removed)
            gap = word["start"] - previous["end"]
            if gap > gap_limit:
                segments.append((segment_start, previous["end"] + gap_limit / 2))
                segment_start = word["start"] - gap_limit / 2
                removed += gap - gap_limit
        shifted.append({**word, "start": word["start"] - removed, "end": word["end"] - removed})
    last_end = words[-1]["end"]
    segments.append((segment_start, last_end + max_gap(scene_start + last_end - removed) / 2))

    filters = [
        f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{index}]"
        for index, (start, end) in enumerate(segments)
    ]
    inputs = "".join(f"[a{index}]" for index in range(len(segments)))
    filters.append(f"{inputs}concat=n={len(segments)}:v=0:a=1[out]")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-filter_complex", ";".join(filters),
         "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(output)],
        check=True,
    )
    raw.unlink()
    return shifted


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
    video_seconds = 0.0
    for index, scene in enumerate(spec["scenes"], start=1):
        audio_name = f"narration-{index:02d}.mp3"
        raw = assets / f"raw-{audio_name}"
        words = await narrate(scene["narration"], voice, rate, raw)
        if not words:
            raise SpecError(f"cena {index}: o edge-tts não devolveu as palavras da narração, rode de novo")
        words = tighten(raw, assets / audio_name, words, video_seconds)
        seconds = max(audio_seconds(assets / audio_name), MIN_SCENE_SECONDS)
        duration = round(seconds * FPS)
        video_seconds += duration / FPS
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
