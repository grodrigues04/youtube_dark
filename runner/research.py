"""Reads the market_trends research from MongoDB. Runs as root only (MONGO_URI).

Usage:
    research.py export-latest <folder>   exports the latest completed research (Monday to
                                         Wednesday) to <folder>: report.md, highlights.json and
                                         previous-videos.json (every video ever made, so a theme
                                         is never repeated). Prints the date of the research;
                                         exit 3 when there is no completed research yet.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from pymongo import MongoClient

RESEARCH_DATABASE = os.environ.get("RESEARCH_DATABASE", "market_trends")
VIDEOS_DATABASE = os.environ.get("VIDEOS_DATABASE", "youtube_dark")
REAL_DATE = r"^\d{4}-\d{2}-\d{2}$"


def get_client() -> MongoClient:
    return MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=30000, tz_aware=True)


def log(message: str) -> None:
    print(f"[research {datetime.now():%F %T}] {message}", file=sys.stderr, flush=True)


def export_latest(folder: Path) -> int:
    client = get_client()
    research = client[RESEARCH_DATABASE]["researches"].find_one(
        {"date": {"$regex": REAL_DATE}, "status": "completed"},
        sort=[("date", -1)],
    )
    if research is None:
        log("no completed research yet")
        return 3
    research_date = research["date"]
    folder.mkdir(parents=True, exist_ok=True)
    report = [f"# {research.get('title', '')}\n\n{research.get('summary', '')}\n"]
    for part in research.get("parts", []):
        report.append(f"# {part['title']}\n\n{part['markdown']}\n")
    (folder / "report.md").write_text("\n".join(report), encoding="utf-8")
    highlights = {
        "date": research_date,
        "title": research.get("title"),
        "summary": research.get("summary"),
        "recommendations": research.get("recommendations", []),
        "top_opportunities": research.get("top_opportunities", []),
    }
    (folder / "highlights.json").write_text(json.dumps(highlights, ensure_ascii=False, indent=2), encoding="utf-8")

    previous = list(
        client[VIDEOS_DATABASE]["videos"].find(
            {"date": {"$regex": REAL_DATE}, "theme": {"$ne": None}},
            {"_id": 0, "date": 1, "research_date": 1, "category_key": 1, "item_name": 1, "theme": 1,
             "title": 1, "status": 1},
        ).sort("date", -1)
    )
    for video in previous:
        # The first videos were made from the research of their own day
        video.setdefault("research_date", video["date"])
    (folder / "previous-videos.json").write_text(json.dumps(previous, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"exported research {research_date} to {folder} ({len(research.get('parts', []))} parts, {len(previous)} previous videos)")
    print(research_date)
    return 0


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "export-latest":
        sys.exit(export_latest(Path(sys.argv[2])))
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
