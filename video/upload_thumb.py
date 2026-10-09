# /// script
# dependencies = ["google-api-python-client", "google-auth-oauthlib"]
# ///
"""썸네일을 영상에 건다(채널 인증 필요).  uv run video/upload_thumb.py <videoId> <슬러그>  — <슬러그>/out/<슬러그>-thumb.png 를 올린다."""
import pathlib, sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from update_meta import credentials  # youtube 권한 토큰(token-manage.json)

vid, slug = sys.argv[1:3]
png = pathlib.Path(__file__).parent / slug / "out" / f"{slug}-thumb.png"
assert png.stat().st_size < 2_000_000, "유튜브 썸네일은 2MB 이하"
r = build("youtube", "v3", credentials=credentials()).thumbnails().set(videoId=vid, media_body=MediaFileUpload(png, mimetype="image/png")).execute()
print(vid, r["items"][0]["maxres"]["url"] if "maxres" in r["items"][0] else "set")
