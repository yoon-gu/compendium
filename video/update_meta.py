# /// script
# dependencies = ["google-api-python-client", "google-auth-oauthlib"]
# ///
"""올린 영상의 제목·설명·태그를 고친다. upload 전용 토큰으로는 videos.update 가 403 이라(실측 2026-10-08)
`youtube` 권한의 별도 토큰 video/token-manage.json 을 쓴다(처음 한 번 브라우저 로그인, .gitignore 대상).

    uv run video/update_meta.py <videoId> <슬러그>      # video/<슬러그>/youtube.md 의 제목·설명·태그를 반영

youtube.md 형식: 1행 제목, `태그:` 줄(쉼표 구분), 빈 줄 뒤 설명 전문. 챕터 시각은 build 산출 wav 길이로 넣는다(`{챕터}` 자리).
"""
import pathlib, re, sys, wave
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

HERE = pathlib.Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN = HERE / "token-manage.json"


def credentials():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds or not creds.valid:
        creds = InstalledAppFlow.from_client_secrets_file(HERE / "client_secret.json", SCOPES).run_local_server(port=0)
    TOKEN.write_text(creds.to_json())
    return creds


def chapters(slug: str) -> str:
    """장면 wav 길이로 '0:00 장 이름' 줄을 만든다(같은 장 이름은 첫 장면만)."""
    text = (HERE / slug / "script.md").read_text(encoding="utf-8")
    labels = re.findall(r"^## (\d+) \| (.+?) \|", text, re.M)
    t, out, seen = 0.0, [], set()
    for n, label in labels:
        if label not in seen:
            seen.add(label); out.append(f"{int(t)//60}:{int(t)%60:02d} {label}")
        with wave.open(str(HERE / slug / "work/voice-진우" / f"scene-{int(n):02d}.wav")) as f:
            t += f.getnframes() / f.getframerate()
    return "\n".join(out)


def main():
    vid, slug = sys.argv[1:3]
    meta = (HERE / slug / "youtube.md").read_text(encoding="utf-8")
    title, rest = meta.split("\n", 1)
    tagline, desc = rest.split("\n\n", 1)
    tags = [t.strip() for t in tagline.removeprefix("태그:").split(",") if t.strip()]
    assert sum(len(t) for t in tags) <= 480 and len(title) <= 100, "제목 100자, 태그 합계 500자 한도"
    desc = desc.replace("{챕터}", chapters(slug)).strip()
    assert len(desc.encode()) <= 5000
    yt = build("youtube", "v3", credentials=credentials())
    cur = yt.videos().list(id=vid, part="snippet").execute()["items"][0]["snippet"]
    cur.update(title=title.strip(), description=desc, tags=tags, categoryId="27", defaultLanguage="ko", defaultAudioLanguage="ko")
    yt.videos().update(part="snippet", body={"id": vid, "snippet": cur}).execute()
    print(f"{vid}: 제목 {len(title)}자, 설명 {len(desc)}자, 태그 {len(tags)}개({sum(len(t) for t in tags)}자)")


if __name__ == "__main__":
    main()
