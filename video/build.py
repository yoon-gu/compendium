#!/usr/bin/env python3
"""video/<슬러그>/script.md 를 읽어 타입캐스트 나레이션 + 세로(1080x1920) 텍스트 화면 mp4 를 굽는다.

    python3 build.py managers-path-in-the-age-of-ai              # 진우 목소리로 <슬러그>/out/<슬러그>.mp4
    python3 build.py <슬러그> --voice=준호                         # 다른 목소리(이름 또는 tc_ 아이디). 목소리마다 캐시가 따로다
    python3 build.py <슬러그> --slides-only                       # 화면 PNG 만 굽는다(크레딧 안 씀)

흐름은 toys/world-flags/build 의 퀴즈 빌더와 같다: 문단 단위로 타입캐스트 wav(내용으로 캐시) → 장면 wav 로 이어 붙이고 →
화면 HTML 을 Chrome 으로 PDF → pdftoppm PNG → ffmpeg concat(화면 길이 = 그 화면에 딸린 나레이션 길이).

script.md 형식
- 첫 장면 앞: `출처: …`(모든 화면 위에 작게), `잉크: #rrggbb`(밑줄 색).
- `## 번호 | 장 이름 | 메모` 로 장면 시작. 장 이름이 화면 아래에 작게 들어간다.
- 장면 안에서 `>` 줄 묶음 하나 + 뒤따르는 나레이션 문단(한 줄 = 한 문단)이 화면 하나. `>` 줄이 다시 나오면 새 화면.
  `>` 첫 줄이 큰 문장(명조), 나머지는 보조 줄(고딕). 「 로 시작하면 인용, — 로 시작하면 말한 사람. `**…**` 는 잉크색 밑줄.
- 나레이션 문단을 고치면 그 문단만 다시 생성된다(300자 넘는 문단은 문장 경계로 잘라 보내므로, 조각 경계에서 나누면 재생성 없음).
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

SLUG = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
assert SLUG, "사용법: python3 build.py <슬러그> [--voice=이름] [--slides-only]"
HERE = Path(__file__).resolve().parent / SLUG
SCRIPT, WORK, OUT = HERE / "script.md", HERE / "work", HERE / "out" / f"{SLUG}.mp4"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TTS_URL = "https://api.typecast.ai/v1/text-to-speech"
KEY_PATH = Path.home() / ".config/typecast-key.txt"
VOICES = {"진우": "tc_632293f759d649937b97f323", "준호": "tc_632a7588e7c78a412f5a36cd",
          "다은": "tc_692799c46508f6b9468c54c7", "소혜": "tc_642f9d147ce3f79717423466"}
VOICE = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--voice=")), "진우")
VOICE_ID = VOICES.get(VOICE, VOICE)
MODEL, EMOTION = "ssfm-v30", "normal"
MAX_CHARS = 300                     # 한 요청에 보내는 글자 수 상한(문장 경계로 자른다)
GAP_CHUNK, GAP_PARA, GAP_SCENE = 0.25, 0.6, 1.0   # 초. 요청 조각 / 문단 / 장면 사이 쉼
W, H = 1080, 1920


# ---------- 대본 ----------
def parse(text: str) -> tuple[dict, list[dict]]:
    """(머리말 {출처, 잉크}, 장면 목록). 장면 = {n, label, frames: [{slide: [...], narration: [...]}]}."""
    meta, scenes = {"출처": "", "잉크": "#1C2E6B"}, []
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"^## (\d+) \| (.+?) \| (.+)$", line)
        if m:
            scenes.append({"n": int(m[1]), "label": m[2], "frames": []})
            continue
        if not scenes:
            key, _, val = line.partition(":")
            if key in meta and val.strip():
                meta[key] = val.strip()
            continue
        if not line or line.startswith("<!--"):
            continue
        frames = scenes[-1]["frames"]
        if line.startswith(">"):
            if not frames or frames[-1]["narration"]:
                frames.append({"slide": [], "narration": []})
            frames[-1]["slide"].append(line[1:].strip())
        else:
            assert frames, f"장면 {scenes[-1]['n']}: 화면 글(>) 없이 나레이션이 시작된다"
            frames[-1]["narration"].append(line)
    assert scenes and [s["n"] for s in scenes] == list(range(1, len(scenes) + 1)), "장면 번호가 1부터 차례여야 한다"
    for s in scenes:
        assert s["frames"] and all(f["narration"] for f in s["frames"]), f"장면 {s['n']}: 나레이션 없는 화면이 있다"
    return meta, scenes


def chunks(paragraph: str) -> list[str]:
    """문단을 문장 경계에서 MAX_CHARS 이하 조각으로 묶는다."""
    out, cur = [], ""
    for sent in re.split(r"(?<=[.?!])\s+", paragraph):
        assert len(sent) <= MAX_CHARS, f"한 문장이 너무 길다({len(sent)}자): {sent[:40]}…"
        if cur and len(cur) + 1 + len(sent) > MAX_CHARS:
            out.append(cur); cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    return out + [cur]


# ---------- 음성 ----------
def tts(text: str) -> Path:
    cache = WORK / f"voice-{VOICE}"
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / (hashlib.sha1(f"{VOICE_ID}|{EMOTION}|{MODEL}|{text}".encode()).hexdigest()[:12] + ".wav")
    if dest.exists():
        return dest
    body = json.dumps({"voice_id": VOICE_ID, "text": text, "model": MODEL, "emotion": EMOTION}).encode()
    for attempt in range(5):
        req = urllib.request.Request(TTS_URL, data=body, headers={
            "X-API-KEY": KEY_PATH.read_text().strip(), "Content-Type": "application/json"})
        try:
            dest.write_bytes(urllib.request.urlopen(req, timeout=180).read())
            print(f"  타입캐스트 생성 {len(text)}자: {text[:30]}…")
            return dest
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")[:300]
            if err.code not in (429, 500, 502, 503) or attempt == 4:
                raise RuntimeError(f"타입캐스트 호출 실패({err.code}): {detail} — {text[:40]}…") from err
            time.sleep(5 * (attempt + 1))
    raise AssertionError("unreachable")


def scene_audio(scene: dict) -> tuple[Path, list[float]]:
    """장면의 문단 wav 들을 쉼을 두고 이어 붙인 wav 와 화면별 길이(초)."""
    dest = WORK / f"voice-{VOICE}" / f"scene-{scene['n']:02d}.wav"
    frames = scene["frames"]
    params, data, seconds = None, [], []
    for fi, frame in enumerate(frames):
        samples = 0
        for p, para in enumerate(frame["narration"]):
            cs = chunks(para)
            for c, text in enumerate(cs):
                last_in_scene = fi == len(frames) - 1 and p == len(frame["narration"]) - 1
                gap = GAP_CHUNK if c < len(cs) - 1 else (GAP_SCENE if last_in_scene else GAP_PARA)
                with wave.open(str(tts(text))) as f:
                    if params is None:
                        params = f.getparams()
                    assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == params[:3], f"wav 형식이 다르다: {text[:20]}"
                    data.append(f.readframes(f.getnframes()))
                    silence = int(gap * f.getframerate())
                    data.append(b"\x00" * silence * f.getnchannels() * f.getsampwidth())
                    samples += f.getnframes() + silence
        seconds.append(samples / params.framerate)
    with wave.open(str(dest), "wb") as out:
        out.setnchannels(params.nchannels); out.setsampwidth(params.sampwidth); out.setframerate(params.framerate)
        out.writeframes(b"".join(data))
    assert all(s > 2 for s in seconds), f"장면 {scene['n']} 에 너무 짧은 화면이 있다: {seconds}"
    return dest, seconds


def join_audio(scene_wavs: list[Path]) -> Path:
    dest = WORK / f"voice-{VOICE}" / "track.wav"
    with wave.open(str(scene_wavs[0])) as f:
        params = f.getparams()
    with wave.open(str(dest), "wb") as out:
        out.setnchannels(params.nchannels); out.setsampwidth(params.sampwidth); out.setframerate(params.framerate)
        for p in scene_wavs:
            with wave.open(str(p)) as f:
                out.writeframes(f.readframes(f.getnframes()))
    return dest


# ---------- 화면 ----------
# 옮겨 적은 노트: 종이색 바탕에 명조 한 문장, 강조는 색 글자가 아니라 잉크색 밑줄 하나. 카드·점·라벨·쪽번호 없음.
def css(ink: str) -> str:
    return f"""
@page {{ size: {W}px {H}px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ background: #F4F4F1; color: #141414; font-family: "NanumGothic", "Nanum Gothic", sans-serif; }}
.f {{ width: {W}px; height: {H}px; padding: 150px 96px 140px; position: relative; break-after: page; background: #F4F4F1;
     word-break: keep-all; overflow-wrap: break-word; }}
.f:last-child {{ break-after: auto; }}
.src {{ font-size: 30px; line-height: 1.5; color: #6B6B68; max-width: 760px; }}
.cover .src {{ visibility: hidden; }}
.main {{ margin-top: 300px; display: flex; flex-direction: column; gap: 56px; }}
h1 {{ font-family: "NanumMyeongjo ExtraBold", "NanumMyeongjoExtraBold", "NanumMyeongjo", serif; font-weight: 800;
     font-size: 84px; line-height: 1.38; letter-spacing: -0.01em; }}
.long h1 {{ font-size: 70px; }}
.cover h1 {{ font-size: 100px; line-height: 1.3; }}
.u {{ text-decoration: underline; text-decoration-color: {ink}; text-decoration-thickness: 12px; text-underline-offset: 16px;
     text-decoration-skip-ink: none; }}
.sup {{ font-size: 42px; line-height: 1.55; color: #4A4A48; }}
.q {{ font-family: "NanumMyeongjo", serif; font-weight: 700; font-size: 60px; line-height: 1.5; }}
.by {{ font-size: 36px; line-height: 1.5; color: #6B6B68; margin-top: -24px; }}
/* 유튜브 세로 재생은 아래 ~20%를 제목·채널·진행바가, 오른쪽 가장자리를 버튼이 덮는다. 장 이름은 위쪽 출처 밑에 둔다 */
.sec {{ position: absolute; left: 96px; top: 205px; font-size: 30px; color: #6B6B68; }}
.pg {{ position: absolute; right: 96px; top: 150px; font-size: 30px; line-height: 1.5; color: #6B6B68; font-variant-numeric: tabular-nums; }}
/* 배경 6종을 화면마다 돌려 쓴다: 미색 / 크림 / 잉크 틴트 / 어두운 반전 / 상단 색 띠 / 청회 */
.b1 {{ background: #F3EFE6; }}
.b2 {{ background: color-mix(in srgb, {ink} 8%, #F4F4F1); }}
.b3 {{ background: #1E1E1C; color: #F4F4F1; }}
.b3 .src, .b3 .sec, .b3 .pg, .b3 .sup, .b3 .by {{ color: #B9B9B4; }}
.b4 {{ background: linear-gradient(180deg, color-mix(in srgb, {ink} 16%, #F4F4F1) 0 300px, #F4F4F1 300px); }}
.b5 {{ background: #EAEEF0; }}
"""


def inline(s: str) -> str:
    """`**…**` 는 잉크색 밑줄, ` / ` 는 줄바꿈(표지 제목처럼 한 글자가 다음 줄로 떨어지는 것을 막을 때)."""
    return re.sub(r"\*\*(.+?)\*\*", r'<span class=u>\1</span>', html.escape(s, quote=False)).replace(" / ", "<br>")


def frame_html(frame: dict, scene: dict, meta: dict, cover: bool, page: int = 1, pages: int = 1) -> str:
    head, *rest = frame["slide"]
    parts = []
    for ln in rest:
        if ln.startswith("「"):
            parts.append(f"<p class=q>{inline(ln)}</p>")
        elif ln.startswith("—"):
            parts.append(f"<p class=by>{inline(ln[1:].strip())}</p>")
        else:
            parts.append(f"<p class=sup>{inline(ln)}</p>")
    cls = f"f b{(page - 1) % 6}" + (" cover" if cover else "") + (" long" if len(re.sub(r"\*", "", head)) > 44 else "")
    return (f'<section class="{cls}"><div class=src>{inline(meta["출처"])}</div>'
            f'<div class=main><h1>{inline(head)}</h1>{"".join(parts)}</div>'
            f'<div class=sec>{inline(scene["label"])}</div><div class=pg>{page} / {pages}</div></section>')


def render_slides(meta: dict, scenes: list[dict]) -> list[Path]:
    work = WORK / "slides"
    work.mkdir(parents=True, exist_ok=True)
    page, pdf = work / "slides.html", work / "slides.pdf"
    flat = [(fr, s) for s in scenes for fr in s["frames"]]
    sections = [frame_html(fr, s, meta, i == 0, i + 1, len(flat)) for i, (fr, s) in enumerate(flat)]
    page.write_text(f'<!doctype html><meta charset="utf-8"><style>{css(meta["잉크"])}</style>{"".join(sections)}', encoding="utf-8")
    for old in work.glob("s-*.png"):
        old.unlink()
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", page.as_uri()], check=True, capture_output=True)
    # CSS px -> PDF pt 는 0.75배라 96dpi 로 되돌리면 정확히 1080x1920 이 된다
    subprocess.run(["pdftoppm", "-png", "-r", "96", str(pdf), str(work / "s")], check=True)
    shots = sorted(work.glob("s-*.png"))
    assert len(shots) == len(sections), f"화면 수가 맞지 않는다: {len(shots)} != {len(sections)}"
    return shots


# ---------- 조립 ----------
def encode(shots: list[Path], seconds: list[float], track: Path) -> Path:
    listing = shots[0].parent / "list.txt"
    lines = []
    for shot, sec in zip(shots, seconds):
        lines += [f"file '{shot.name}'", f"duration {sec:.3f}"]
    lines.append(f"file '{shots[-1].name}'")   # 마지막 프레임 길이를 살리려면 한 번 더 적어야 한다
    listing.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", str(listing), "-i", str(track),
                    "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-t", f"{sum(seconds):.3f}",
                    "-movflags", "+faststart", str(OUT)], check=True)
    return OUT


def build() -> tuple[Path, list[float]]:
    meta, scenes = parse(SCRIPT.read_text(encoding="utf-8"))
    shots = render_slides(meta, scenes)
    if "--slides-only" in sys.argv:
        print(f"화면 {len(shots)}장: {shots[0].parent}")
        sys.exit(0)
    wavs, seconds, chapters = [], [], []
    for s in scenes:
        wav, secs = scene_audio(s)
        t = int(sum(seconds))
        if not chapters or not chapters[-1].endswith(" " + s["label"]):   # 같은 장이 이어지면 한 챕터
            chapters.append(f"{t // 60}:{t % 60:02d} {s['label']}")
        wavs.append(wav); seconds += secs
        print(f"장면 {s['n']:2d} {sum(secs):6.1f}초  화면 {len(secs)}개 {[round(x) for x in secs]}  {s['label']}")
    assert len(seconds) == len(shots)
    # 유튜브 설명란에 붙이면 챕터가 된다(0:00 시작, 3개 이상, 각 10초 이상)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.with_name(f"{SLUG}-chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    return encode(shots, seconds, join_audio(wavs)), seconds


def demo() -> None:
    out, seconds = build()
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                           "-of", "default=nw=1:nk=1", str(out)], check=True, capture_output=True, text=True).stdout.split()
    width, height, total = int(info[1]), int(info[2]), float(info[-1])
    assert (width, height) == (W, H), f"해상도가 다르다: {width}x{height}"
    assert "audio" in info, "소리가 들어가지 않았다"
    assert abs(total - sum(seconds)) < 1, f"길이가 어긋난다: {total:.1f} vs {sum(seconds):.1f}"
    chars = sum(len(p) for s in parse(SCRIPT.read_text(encoding="utf-8"))[1] for f in s["frames"] for p in f["narration"])
    print(f"{out.name} · {width}x{height} · {total / 60:.1f}분 · 화면 {len(seconds)}개 · {out.stat().st_size / 1e6:.0f}MB · 대본 {chars:,}자 · 목소리 {VOICE}")


if __name__ == "__main__":
    demo()
