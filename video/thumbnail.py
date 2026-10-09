#!/usr/bin/env python3
"""video/<슬러그>/script.md 표지(1장)로 유튜브 썸네일(1280x720 PNG)을 만든다. 화면 디자인과 같은 결(종이 바탕, 명조 제목, 잉크색 밑줄).

    python3 thumbnail.py <슬러그> [<슬러그> …]          # → <슬러그>/out/<슬러그>-thumb.png

유튜브에 올리려면 update_meta.py 처럼 youtube 권한 토큰이 필요하다:  uv run upload_thumb.py <videoId> <슬러그>
"""
import html
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1280, 720


def parse(slug: str) -> dict:
    text = (HERE / slug / "script.md").read_text(encoding="utf-8")
    meta = dict(re.findall(r"^(출처|잉크): (.+)$", text, re.M))
    cover = re.search(r"^## 1 \|.*\n((?:> .*\n)+)", text, re.M)[1]
    lines = [ln[2:].strip() for ln in cover.splitlines()]
    weeks = {r[1]: r[0] for r in (ln.split("\t") for ln in (HERE / "episodes.tsv").read_text(encoding="utf-8").splitlines()[1:])}
    return {"title": lines[0], "sub": lines[1] if len(lines) > 1 else "", "ink": meta.get("잉크", "#1C2E6B"),
            "src": meta.get("출처", ""), "week": weeks.get(slug, "")}


def inline(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<span class=u>\1</span>", html.escape(s, quote=False)).replace(" / ", "<br>")


def render(slug: str) -> Path:
    m = parse(slug)
    long = len(re.sub(r"\*|/", "", m["title"])) > 20
    page = f"""<!doctype html><meta charset="utf-8"><style>
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; background: #F4F4F1; color: #141414; font-family: "NanumGothic", "Nanum Gothic", sans-serif;
       padding: 56px 72px 48px 92px; position: relative; overflow: hidden; word-break: keep-all; }}
.bar {{ position: absolute; left: 0; top: 0; bottom: 0; width: 28px; background: {m["ink"]}; }}
.top {{ display: flex; justify-content: space-between; gap: 40px; font-size: 30px; color: #6B6B68; white-space: nowrap; }}
.top span:last-child {{ overflow: hidden; text-overflow: ellipsis; }}
.top b {{ color: {m["ink"]}; font-weight: 800; }}
h1 {{ font-family: "NanumMyeongjo ExtraBold", "NanumMyeongjoExtraBold", "NanumMyeongjo", serif; font-weight: 800;
      font-size: {96 if long else 124}px; line-height: 1.28; letter-spacing: -0.015em; margin-top: {44 if long else 56}px; max-width: 1110px; }}
.u {{ text-decoration: underline; text-decoration-color: {m["ink"]}; text-decoration-thickness: 14px; text-underline-offset: 18px; text-decoration-skip-ink: none; }}
.sub {{ position: absolute; left: 92px; right: 72px; bottom: 48px; font-size: 34px; line-height: 1.45; color: #4A4A48; }}
</style>
<div class=bar></div>
<div class=top><span><b>듣는편람</b> · {html.escape(m["week"])}</span><span>{html.escape(m["src"])}</span></div>
<h1>{inline(m["title"])}</h1>
<div class=sub>{inline(m["sub"])}</div>"""
    work = HERE / slug / "work"; work.mkdir(parents=True, exist_ok=True)
    (work / "thumb.html").write_text(page, encoding="utf-8")
    out = HERE / slug / "out" / f"{slug}-thumb.png"; out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={out}", f"--window-size={W},{H}",
                    (work / "thumb.html").as_uri()], check=True, capture_output=True)
    return out


if __name__ == "__main__":
    for slug in sys.argv[1:]:
        print(render(slug))
