"""Reads the daily research of market_trends from MongoDB. Runs as root only (MONGO_URI).

Usage:
    research.py wait <date>              waits until the research of <date> finishes; exit 0 when
                                         completed, 3 when failed, 4 when the deadline passed
    research.py export <date> <folder>   writes report.md, highlights.json and previous-videos.json
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pymongo import MongoClient

RESEARCH_DATABASE = os.environ.get("RESEARCH_DATABASE", "market_trends")
VIDEOS_DATABASE = os.environ.get("VIDEOS_DATABASE", "youtube_dark")
POLL_SECONDS = int(os.environ.get("RESEARCH_POLL_SECONDS", "120"))
WAIT_UNTIL_HOUR = int(os.environ.get("RESEARCH_WAIT_UNTIL_HOUR", "23"))


def get_client() -> MongoClient:
    return MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=30000, tz_aware=True)


def log(message: str) -> None:
    print(f"[research {datetime.now():%F %T}] {message}", flush=True)


def wait(run_date: str) -> int:
    researches = get_client()[RESEARCH_DATABASE]["researches"]
    last_status = None
    while True:
        try:
            research = researches.find_one({"date": run_date}, {"status": 1, "error": 1})
        except Exception as error:  # network blips must not end a wait of hours
            log(f"MongoDB error, retrying: {error}")
            research = None
        status = (research or {}).get("status", "not started")
        if status != last_status:
            log(f"research of {run_date}: {status}")
            last_status = status
        if status == "completed":
            return 0
        if status == "failed":
            log(f"research failed: {research.get('error')}")
            return 3
        if datetime.now().hour >= WAIT_UNTIL_HOUR:
            log(f"research of {run_date} did not finish until {WAIT_UNTIL_HOUR}:00, giving up")
            return 4
        time.sleep(POLL_SECONDS)


def export(run_date: str, folder: Path) -> int:
    client = get_client()
    research = client[RESEARCH_DATABASE]["researches"].find_one({"date": run_date, "status": "completed"})
    if research is None:
        log(f"no completed research for {run_date}")
        return 3
    folder.mkdir(parents=True, exist_ok=True)
    report = [f"# {research.get('title', '')}\n\n{research.get('summary', '')}\n"]
    for part in research.get("parts", []):
        report.append(f"# {part['title']}\n\n{part['markdown']}\n")
    (folder / "report.md").write_text("\n".join(report), encoding="utf-8")
    highlights = {
        "date": run_date,
        "title": research.get("title"),
        "summary": research.get("summary"),
        "recommendations": research.get("recommendations", []),
        "top_opportunities": research.get("top_opportunities", []),
    }
    (folder / "highlights.json").write_text(json.dumps(highlights, ensure_ascii=False, indent=2), encoding="utf-8")

    since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    previous = list(
        client[VIDEOS_DATABASE]["videos"].find(
            {"date": {"$gte": since, "$lt": run_date}},
            {"_id": 0, "date": 1, "theme": 1, "item_name": 1, "title": 1},
        ).sort("date", -1)
    )
    (folder / "previous-videos.json").write_text(json.dumps(previous, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"exported research of {run_date} to {folder} ({len(research.get('parts', []))} parts, {len(previous)} previous videos)")
    return 0


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "wait":
        sys.exit(wait(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == "export":
        sys.exit(export(sys.argv[2], Path(sys.argv[3])))
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
