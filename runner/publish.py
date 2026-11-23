"""Uploads the finished Shorts to YouTube and records them in MongoDB. Root only: the YouTube
credentials and MONGO_URI never reach Claude.

Usage:
    publish.py [<video_dir> ...]            without arguments, every /data/work/*/videos/* with READY
    publish.py --record <video_dir> <status> [<error>]   only records the video in MongoDB

A video folder is uploaded once: READY (written by Claude) → UPLOADED (video id). The video goes
up private, with YouTube scheduled to publish it at PUBLISH_HOUR (08:00, Brasília). Quota errors
stop the run and block new attempts until the quota resets (midnight Pacific time); other errors
are retried in the next runs, up to MAX_ATTEMPTS, then UPLOAD_FAILED. The media of the uploaded
videos (video, thumbnail, narration, frames) is deleted from the disk; the texts stay.
"""

import fcntl
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from pymongo import MongoClient

WORK_ROOT = Path(os.environ.get("WORK_ROOT", "/data/work"))
STATE_DIR = Path(os.environ.get("STATE_DIR", "/data/state"))
QUOTA_BLOCK_FILE = STATE_DIR / "youtube-quota-blocked-until"
LOCK_FILE = STATE_DIR / "publish.lock"
VIDEOS_DATABASE = os.environ.get("VIDEOS_DATABASE", "youtube_dark")
PUBLISH_HOUR = int(os.environ.get("YOUTUBE_PUBLISH_HOUR") or "8")
LOCAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")
MEDIA_SUFFIXES = {".mp4", ".webm", ".mov", ".jpg", ".jpeg", ".png", ".webp", ".mp3", ".wav", ".m4a", ".aac"}
MEDIA_FOLDERS = ("assets", "qa")
CATEGORY_ID = os.environ.get("YOUTUBE_CATEGORY_ID", "27")  # Education
MAX_ATTEMPTS = 5
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]


def log(message: str) -> None:
    print(f"[publish {datetime.now():%F %T}] {message}", flush=True)


def youtube_client():
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    credentials.refresh(Request())
    return build("youtube", "v3", credentials=credentials, cache_discovery=False)


def quota_blocked() -> bool:
    if not QUOTA_BLOCK_FILE.is_file():
        return False
    until = datetime.fromisoformat(QUOTA_BLOCK_FILE.read_text().strip())
    if datetime.now(timezone.utc) >= until:
        QUOTA_BLOCK_FILE.unlink()
        return False
    return True


def block_until_quota_reset() -> None:
    # The YouTube quota resets at midnight Pacific time
    pacific = ZoneInfo("America/Los_Angeles")
    reset = (datetime.now(pacific) + timedelta(days=1)).replace(hour=0, minute=10, second=0, microsecond=0)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    QUOTA_BLOCK_FILE.write_text(reset.astimezone(timezone.utc).isoformat())
    log(f"YouTube quota exceeded, next attempt after {reset.astimezone(ZoneInfo('America/Sao_Paulo')):%F %H:%M}")


def is_quota_error(error: HttpError) -> bool:
    # uploadLimitExceeded (videos per day of the channel) comes as 400, the API quota as 403
    return error.resp.status in (400, 403) and any(
        reason in str(error.content) for reason in ("quotaExceeded", "uploadLimitExceeded", "dailyLimitExceeded")
    )


def next_publish_time() -> datetime:
    # The next PUBLISH_HOUR at least 15 minutes ahead (YouTube needs publishAt in the future)
    now = datetime.now(LOCAL_TIMEZONE)
    publish_at = now.replace(hour=PUBLISH_HOUR, minute=0, second=0, microsecond=0)
    if publish_at < now + timedelta(minutes=15):
        publish_at += timedelta(days=1)
    return publish_at


def delete_media(video_dir: Path) -> None:
    removed = 0
    for name in MEDIA_FOLDERS:
        if (video_dir / name).is_dir():
            shutil.rmtree(video_dir / name)
            removed += 1
    for file in video_dir.iterdir():
        if file.is_file() and file.suffix.lower() in MEDIA_SUFFIXES:
            file.unlink()
            removed += 1
    if removed:
        log(f"{video_dir}: media deleted from the disk")


def research_date_of(video_dir: Path) -> str | None:
    highlights = video_dir.parent.parent / "research" / "highlights.json"
    if not highlights.is_file():
        return None
    return json.loads(highlights.read_text(encoding="utf-8")).get("date")


def record(video_dir: Path, fields: dict) -> None:
    run_date, index = video_dir.parent.parent.name, int(video_dir.name)
    tema = json.loads((video_dir / "tema.json").read_text(encoding="utf-8")) if (video_dir / "tema.json").is_file() else {}
    client = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=30000, tz_aware=True)
    collection = client[VIDEOS_DATABASE]["videos"]
    collection.create_index([("date", 1), ("index", 1)], unique=True)
    now = datetime.now(timezone.utc)
    collection.update_one(
        {"date": run_date, "index": index},
        {
            "$set": {
                "theme": tema.get("theme"),
                "item_name": tema.get("item_name"),
                "category_key": tema.get("category_key"),
                "research_date": research_date_of(video_dir),
                "updated_at": now,
                **fields,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )
    client.close()


def upload(youtube, video_dir: Path, publish_at: datetime) -> str:
    metadata = json.loads((video_dir / "metadata.json").read_text(encoding="utf-8"))
    body = {
        "snippet": {
            "title": metadata["title"][:100],
            "description": metadata["description"].replace("<", "").replace(">", "")[:4900],
            "tags": metadata.get("tags", [])[:30],
            "categoryId": CATEGORY_ID,
            "defaultLanguage": "pt-BR",
            "defaultAudioLanguage": "pt-BR",
        },
        "status": {
            # Private until YouTube publishes it at publishAt
            "privacyStatus": "private",
            "publishAt": publish_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
        },
    }
    media = MediaFileUpload(str(video_dir / metadata.get("video", "video.mp4")), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]

    thumbnail = video_dir / metadata.get("thumbnail", "thumbnail.jpg")
    if thumbnail.is_file():
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail), mimetype="image/jpeg")).execute()
        except HttpError as error:
            # Custom thumbnails need a verified channel (phone verification on YouTube)
            log(f"{video_dir}: thumbnail not set ({error.resp.status}): {error.reason}")
    return video_id


def pending_videos() -> list[Path]:
    # Only real days: test runs (teste-*) are never uploaded automatically
    return sorted(
        folder for folder in WORK_ROOT.glob("*/videos/*")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", folder.parent.parent.name)
        and (folder / "READY").is_file() and not (folder / "UPLOADED").is_file() and not (folder / "UPLOAD_FAILED").is_file()
    )


def main() -> None:
    if sys.argv[1:2] == ["--record"]:
        folder = Path(sys.argv[2]).resolve()
        fields = {"status": sys.argv[3]}
        if len(sys.argv) > 4:
            fields["error"] = sys.argv[4][:2000]
        metadata_file = folder / "metadata.json"
        if metadata_file.is_file():
            fields["title"] = json.loads(metadata_file.read_text(encoding="utf-8")).get("title")
        record(folder, fields)
        return
    # The scheduler and run_daily.sh both call this script: one run at a time, or a video is uploaded twice
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    lock = LOCK_FILE.open("w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    folders = [Path(argument).resolve() for argument in sys.argv[1:]] or pending_videos()
    folders = [folder for folder in folders if (folder / "READY").is_file() and not (folder / "UPLOADED").is_file()]
    # The videos already on YouTube must not stay on the disk
    for uploaded in sorted(WORK_ROOT.glob("*/videos/*/UPLOADED")):
        delete_media(uploaded.parent)
    if not folders or quota_blocked():
        return
    if not all(os.environ.get(key) for key in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")):
        log(f"{len(folders)} video(s) ready, but the YouTube credentials are not in .env (see README)")
        return
    youtube = youtube_client()
    for folder in folders:
        attempts_file = folder / "upload-attempts"
        attempts = int(attempts_file.read_text()) if attempts_file.is_file() else 0
        publish_at = next_publish_time()
        try:
            video_id = upload(youtube, folder, publish_at)
        except HttpError as error:
            if is_quota_error(error):
                block_until_quota_reset()
                return
            attempts += 1
            attempts_file.write_text(str(attempts))
            log(f"{folder}: upload failed (attempt {attempts}/{MAX_ATTEMPTS}): {error}")
            if attempts >= MAX_ATTEMPTS:
                (folder / "UPLOAD_FAILED").write_text(str(error))
                record(folder, {"status": "upload_failed", "error": str(error)[:2000]})
            continue
        url = f"https://www.youtube.com/shorts/{video_id}"
        (folder / "UPLOADED").write_text(video_id)
        metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
        record(folder, {
            "status": "uploaded",
            "youtube_id": video_id,
            "url": url,
            "title": metadata.get("title"),
            "description": metadata.get("description"),
            "hashtags": metadata.get("hashtags", []),
            "privacy_status": "scheduled",
            "publish_at": publish_at.astimezone(timezone.utc),
            "uploaded_at": datetime.now(timezone.utc),
        })
        log(f"{folder}: uploaded {url}, published by YouTube at {publish_at:%F %H:%M}")
        delete_media(folder)


if __name__ == "__main__":
    main()
