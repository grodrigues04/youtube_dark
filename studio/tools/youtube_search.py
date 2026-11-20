"""YouTube research with yt-dlp (no API key).

Usage:
    youtube_search.py search "<query>" [--limit 15] [--shorts]   ranked list of videos
    youtube_search.py details <url>                              metadata + description + tags
    youtube_search.py transcript <url> [--lang pt|en|...]        automatic captions as text

Prints Markdown, ready to paste into the research notes.
"""

import argparse
import glob
import re
import sys
import tempfile
from pathlib import Path

import yt_dlp

BASE_OPTIONS = {"quiet": True, "no_warnings": True, "skip_download": True}


def compact_number(value) -> str:
    if value is None:
        return "?"
    for limit, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if value >= limit:
            return f"{value / limit:.1f}{suffix}"
    return str(value)


def search(query: str, limit: int, shorts: bool) -> None:
    if shorts and "#shorts" not in query.lower():
        query = f"{query} #shorts"
    with yt_dlp.YoutubeDL({**BASE_OPTIONS, "extract_flat": True}) as youtube:
        result = youtube.extract_info(f"ytsearch{limit}:{query}", download=False)
    entries = sorted(result.get("entries") or [], key=lambda entry: entry.get("view_count") or 0, reverse=True)
    print(f"## YouTube: {query}\n")
    print("| Views | Duração | Título | Canal | URL |")
    print("|---|---|---|---|---|")
    for entry in entries:
        duration = entry.get("duration")
        duration_text = f"{int(duration) // 60}:{int(duration) % 60:02d}" if duration else "?"
        title = (entry.get("title") or "").replace("|", "/")
        channel = (entry.get("channel") or entry.get("uploader") or "").replace("|", "/")
        url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
        print(f"| {compact_number(entry.get('view_count'))} | {duration_text} | {title} | {channel} | {url} |")


def details(url: str) -> None:
    with yt_dlp.YoutubeDL(BASE_OPTIONS) as youtube:
        info = youtube.extract_info(url, download=False)
    print(f"## {info.get('title')}\n")
    print(f"- Canal: {info.get('channel')} ({compact_number(info.get('channel_follower_count'))} inscritos)")
    print(f"- Views: {compact_number(info.get('view_count'))} · Likes: {compact_number(info.get('like_count'))} · "
          f"Comentários: {compact_number(info.get('comment_count'))}")
    print(f"- Publicado: {info.get('upload_date')} · Duração: {info.get('duration')}s · Idioma: {info.get('language')}")
    print(f"- Tags: {', '.join((info.get('tags') or [])[:25])}")
    print(f"\n### Descrição\n\n{(info.get('description') or '')[:2500]}")


def transcript(url: str, language: str) -> None:
    with tempfile.TemporaryDirectory() as folder:
        options = {
            **BASE_OPTIONS,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [language, f"{language}-orig", "en", "pt"],
            "subtitlesformat": "vtt",
            "outtmpl": str(Path(folder) / "video.%(ext)s"),
        }
        with yt_dlp.YoutubeDL(options) as youtube:
            youtube.extract_info(url, download=True)
        files = sorted(glob.glob(str(Path(folder) / "*.vtt")))
        if not files:
            print("Sem legendas disponíveis para este vídeo.")
            return
        lines = []
        for line in Path(files[0]).read_text(encoding="utf-8").splitlines():
            line = re.sub(r"<[^>]+>", "", line).strip()
            if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")):
                continue
            if not lines or lines[-1] != line:
                lines.append(line)
        print(f"## Transcrição ({Path(files[0]).name})\n\n{' '.join(lines)[:6000]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    search_parser = commands.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=15)
    search_parser.add_argument("--shorts", action="store_true")
    details_parser = commands.add_parser("details")
    details_parser.add_argument("url")
    transcript_parser = commands.add_parser("transcript")
    transcript_parser.add_argument("url")
    transcript_parser.add_argument("--lang", default="pt")
    arguments = parser.parse_args()
    try:
        if arguments.command == "search":
            search(arguments.query, arguments.limit, arguments.shorts)
        elif arguments.command == "details":
            details(arguments.url)
        else:
            transcript(arguments.url, arguments.lang)
    except yt_dlp.utils.DownloadError as error:
        print(f"ERRO do yt-dlp: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
