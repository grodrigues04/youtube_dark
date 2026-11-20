"""One-time YouTube authorization, run on the host (it opens the browser).

    uv run --with google-auth-oauthlib python runner/auth_youtube.py client_secret.json

Log in with the channel account and allow access. The script writes YOUTUBE_CLIENT_ID,
YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN to .env (next to docker-compose.yml). Then:
docker compose up -d (recreates the container with the new variables).
"""

import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def set_env(values: dict[str, str]) -> None:
    lines = ENV_FILE.read_text().splitlines() if ENV_FILE.is_file() else []
    remaining = dict(values)
    for index, line in enumerate(lines):
        key = line.split("=", 1)[0]
        if key in remaining:
            lines[index] = f"{key}={remaining.pop(key)}"
    lines += [f"{key}={value}" for key, value in remaining.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n")
    ENV_FILE.chmod(0o600)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    client_file = Path(sys.argv[1])
    client = json.loads(client_file.read_text())["installed"]
    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
    credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    if not credentials.refresh_token:
        sys.exit("Google did not return a refresh token: remove the app access in your Google account and try again")
    set_env({
        "YOUTUBE_CLIENT_ID": client["client_id"],
        "YOUTUBE_CLIENT_SECRET": client["client_secret"],
        "YOUTUBE_REFRESH_TOKEN": credentials.refresh_token,
    })
    print(f"OK: credentials saved in {ENV_FILE}. Run: docker compose up -d")


if __name__ == "__main__":
    main()
