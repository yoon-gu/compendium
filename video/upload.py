# /// script
# dependencies = ["google-api-python-client", "google-auth-oauthlib"]
# ///
"""mp4 를 유튜브에 비공개로 올린다. 공개 전환은 YouTube Studio 에서.

    uv run video/upload.py <mp4> "<제목>" ["<설명>"]

처음 한 번 브라우저로 로그인해 채널을 고르면 video/token.json 에 저장된다(동의 화면이 테스트 상태면 7일 뒤 만료 → 지우고 다시).
video/client_secret.json(데스크톱 OAuth 클라이언트)과 token.json 은 .gitignore 대상.
"""
import pathlib
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

HERE = pathlib.Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN = HERE / "token.json"


def credentials():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(HERE / "client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
    TOKEN.write_text(creds.to_json())
    return creds


def main():
    path, title, desc = (sys.argv[1:] + [""])[:3]
    yt = build("youtube", "v3", credentials=credentials())
    req = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": desc, "categoryId": "27", "defaultLanguage": "ko"},
            # ponytail: 감사 안 받은 API 프로젝트는 어차피 private 로 잠긴다
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(path, resumable=True, chunksize=8 * 1024 * 1024),
    )
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"{status.progress():.0%}", flush=True)
    print("https://youtu.be/" + resp["id"])


if __name__ == "__main__":
    main()
