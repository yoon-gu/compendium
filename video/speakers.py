#!/usr/bin/env python3
"""여러 사람 대화편 영상에 '누가 말하는지' 이름표 줄을 얹는다(지금 말하는 사람의 이름표만 칠한다).

    python3 video/speakers.py <슬러그>      # out/<슬러그>-podcast.mp4 를 제자리에서 덮어쓴다(build.py --audio 뒤에 돌린다)

- 화자와 이름표 글은 podcast.md 머리말의 `화자:` 와 `배역: 사회=사회자, 실행=마케팅/실행부, …`(`/`는 줄바꿈, 없으면 화자 이름).
- 말하는 구간은 podcast.py 가 남긴 work/podcast-turns.tsv(차례 시작 시각 → 다음 차례 시작까지).
- 위치는 유튜브 UI 가 덮는 아래 20% 바로 위, 본문과 같은 좌우 여백(96px). 잉크색은 script-podcast.md 의 `잉크:`.
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

VIDEO = Path(__file__).resolve().parent
SLUG = sys.argv[1]
HERE = VIDEO / SLUG
OUT = HERE / "out" / f"{SLUG}-podcast.mp4"
FONTS = Path.home() / "Library/Fonts"
X, Y, W, H, GAP = 96, 1400, 888, 116, 12          # 1080x1920 기준, 아래 20%(1536~)를 피한다


def header(text: str, key: str) -> dict:
    m = re.search(rf"^{key}: (.+)$", text, re.M)
    return dict(p.strip().split("=", 1) for p in m[1].split(",")) if m else {}


def to_sec(s: str) -> float:
    m, sec = s.split(":")
    return int(m) * 60 + float(sec)


def chips(names: list[str], roles: dict, active: int, ink: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(FONTS / "NanumGothic-ExtraBold.ttf"), 27)
    w = (W - 4 - GAP * (len(names) - 1)) / len(names)   # 양 끝 테두리가 잘리지 않게 2px씩 안쪽으로
    for k, n in enumerate(names):
        x0 = 2 + k * (w + GAP)
        on = k == active
        d.rounded_rectangle([x0, 2, x0 + w, H - 3], radius=22, fill=ink if on else (255, 255, 255, 225),
                            outline=ink if on else (185, 185, 180, 255), width=3)
        lines = roles.get(n, n).split("/")
        for i, ln in enumerate(lines):
            d.text((x0 + w / 2, H / 2 + (i - (len(lines) - 1) / 2) * 36), ln.strip(), font=font,
                   fill=(255, 255, 255, 255) if on else (70, 70, 68, 255), anchor="mm")
    return img


def main() -> None:
    pod = (HERE / "podcast.md").read_text(encoding="utf-8")
    names = list(header(pod, "화자"))
    roles = header(pod, "배역")
    scr = HERE / "script-podcast.md"
    ink = (re.search(r"^잉크: (#[0-9A-Fa-f]{6})", scr.read_text(encoding="utf-8"), re.M) or [None, "#1C2E6B"])[1] if scr.exists() else "#1C2E6B"
    rows = [ln.split("\t") for ln in (HERE / "work" / "podcast-turns.tsv").read_text(encoding="utf-8").splitlines() if ln.strip()]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT)],
                               check=True, capture_output=True, text=True).stdout)
    spans = {n: [] for n in names}
    for i, (t, who, *_rest) in enumerate(rows):
        end = to_sec(rows[i + 1][0]) if i + 1 < len(rows) else dur
        spans[who].append((to_sec(t), end))
    work = HERE / "work"
    inputs, chain, prev = ["-i", str(OUT)], [], "0:v"
    for k, n in enumerate(names):
        png = work / f"speaker-{k}.png"
        chips(names, roles, k, ink).save(png)
        inputs += ["-i", str(png)]
        when = "+".join(f"between(t,{a:.2f},{b - 0.02:.2f})" for a, b in spans[n]) or "0"
        chain.append(f"[{prev}][{k + 1}:v]overlay={X}:{Y}:enable='{when}'[v{k}]")
        prev = f"v{k}"
    tmp = OUT.with_suffix(".speakers.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "copy", "-movflags", "+faststart", str(tmp)], check=True)
    tmp.replace(OUT)
    assert all(spans[n] for n in names), f"말한 적 없는 화자가 있다: {[n for n in names if not spans[n]]}"
    print(f"{OUT.name}: 이름표 {len(names)}명, 차례 {len(rows)}개")


if __name__ == "__main__":
    main()
