#!/usr/bin/env python3
"""script.md 를 읽어 타입캐스트 나레이션 + 텍스트 슬라이드 mp4 를 굽는다.

    python3 build.py                 # 진우 목소리로 out/managers-path-in-the-age-of-ai.mp4
    python3 build.py --voice=준호     # 다른 목소리(이름 또는 tc_ 아이디). 목소리마다 캐시가 따로다
    python3 build.py --slides-only   # 슬라이드 PNG 만 굽는다(크레딧 안 씀)

흐름은 toys/world-flags/build 의 퀴즈 빌더와 같다: 장면마다 문단 단위로 타입캐스트 wav(내용으로 캐시) →
장면 wav 로 이어 붙이고 → 슬라이드 HTML 을 Chrome 으로 PDF → pdftoppm PNG → ffmpeg concat(장면 길이 = 그 장면 음성 길이).
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

HERE = Path(__file__).resolve().parent
SCRIPT, WORK, OUT = HERE / "script.md", HERE / "work", HERE / "out" / "managers-path-in-the-age-of-ai.mp4"
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
W, H = 1920, 1080
FOOT = "Camille Fournier — The Manager's Path in the Age of AI (Medium, 2026-09) · 한국어 정리·해설"


# ---------- 대본 ----------
def parse(text: str) -> list[dict]:
    scenes: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"^## (\d+) \| (.+?) \| (.+)$", line)
        if m:
            scenes.append({"n": int(m[1]), "kicker": m[2], "title": m[3], "slide": [], "narration": []})
            continue
        if not scenes or not line or line.startswith("<!--"):
            continue
        if line.startswith(">"):
            scenes[-1]["slide"].append(line[1:].strip())
        else:
            scenes[-1]["narration"].append(line)
    assert scenes and [s["n"] for s in scenes] == list(range(1, len(scenes) + 1)), "장면 번호가 1부터 차례여야 한다"
    assert all(s["narration"] for s in scenes), "나레이션이 없는 장면이 있다"
    return scenes


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
            return dest
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")[:300]
            if err.code not in (429, 500, 502, 503) or attempt == 4:
                raise RuntimeError(f"타입캐스트 호출 실패({err.code}): {detail} — {text[:40]}…") from err
            time.sleep(5 * (attempt + 1))
    raise AssertionError("unreachable")


def scene_audio(scene: dict) -> tuple[Path, float]:
    """장면의 문단 wav 들을 쉼을 두고 이어 붙인 wav 와 길이(초)."""
    dest = WORK / f"voice-{VOICE}" / f"scene-{scene['n']:02d}.wav"
    pieces: list[tuple[Path, float]] = []          # (wav, 뒤에 둘 쉼)
    for p, para in enumerate(scene["narration"]):
        cs = chunks(para)
        for c, text in enumerate(cs):
            last_in_para = c == len(cs) - 1
            gap = GAP_CHUNK if not last_in_para else (GAP_PARA if p < len(scene["narration"]) - 1 else GAP_SCENE)
            pieces.append((tts(text), gap))
    params = None
    frames = []
    for path, gap in pieces:
        with wave.open(str(path)) as f:
            if params is None:
                params = f.getparams()
            assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == params[:3], f"wav 형식이 다르다: {path}"
            frames.append(f.readframes(f.getnframes()))
            frames.append(b"\x00" * int(gap * f.getframerate()) * f.getnchannels() * f.getsampwidth())
    data = b"".join(frames)
    with wave.open(str(dest), "wb") as out:
        out.setnchannels(params.nchannels); out.setsampwidth(params.sampwidth); out.setframerate(params.framerate)
        out.writeframes(data)
    seconds = len(data) / (params.nchannels * params.sampwidth * params.framerate)
    assert seconds > 3, f"장면 {scene['n']} 음성이 비었다({seconds:.1f}초)"
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


# ---------- 슬라이드 ----------
CSS = f"""
@page {{ size: {W}px {H}px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ font-family: "Apple SD Gothic Neo", "NanumGothic", sans-serif; background: #161A23; color: #F3EFE7; }}
.f {{ width: {W}px; height: {H}px; padding: 96px 120px 90px; display: flex; flex-direction: column;
     break-after: page; position: relative; background: #161A23; }}
.f:last-child {{ break-after: auto; }}
.kicker {{ font-size: 32px; color: #E3A23B; font-weight: 700; letter-spacing: .04em; margin-bottom: 22px; }}
h1 {{ font-size: 70px; line-height: 1.25; letter-spacing: -0.02em; font-weight: 800; margin-bottom: 44px; }}
.body {{ display: flex; flex-direction: column; gap: 26px; }}
.dense .body {{ gap: 18px; }}
.line {{ position: relative; padding-left: 44px; font-size: 40px; line-height: 1.5; color: #D9D4CA; }}
.dense .line {{ font-size: 35px; }}
.line::before {{ content: ""; position: absolute; left: 0; top: 23px; width: 14px; height: 14px; border-radius: 50%; background: #E3A23B; }}
.dense .line::before {{ top: 19px; }}
.big {{ font-size: 92px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.2; margin: 10px 0 30px; }}
.quote {{ font-family: "NanumMyeongjo", serif; font-size: 40px; line-height: 1.55; border-left: 10px solid #E3A23B;
         padding: 6px 0 6px 36px; color: #F3EFE7; }}
.dense .quote {{ font-size: 35px; }}
.cards {{ display: grid; gap: 30px; margin: 4px 0 30px; }}
.card {{ background: #1F2531; border: 2px solid #2C3444; border-radius: 24px; padding: 38px 34px; font-size: 36px; line-height: 1.45; color: #D9D4CA; }}
.card b {{ display: block; font-size: 42px; color: #E3A23B; margin-bottom: 16px; }}
.foot {{ position: absolute; left: 120px; right: 120px; bottom: 36px; display: flex; justify-content: space-between;
        font-size: 24px; color: #7E8798; }}
.title {{ justify-content: center; }}
.title h1 {{ font-size: 108px; margin-bottom: 56px; }}
.title .line {{ padding-left: 0; font-size: 42px; color: #D9D4CA; line-height: 1.6; }}
.title .line::before {{ display: none; }}
"""


def inline(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s, quote=False))


def slide_html(scene: dict, total: int) -> str:
    lines, cards, body = scene["slide"], [], []
    for ln in lines:
        if ln.startswith("# "):
            head, _, rest = ln[2:].partition(" — ")
            cards.append(f"<div class=card><b>{inline(head)}</b>{inline(rest)}</div>")
        elif ln.startswith("! "):
            body.append(f"<div class=big>{inline(ln[2:])}</div>")
        elif ln.startswith("“") or ln.startswith('"'):
            body.append(f"<div class=quote>{inline(ln)}</div>")
        else:
            body.append(f"<div class=line>{inline(ln)}</div>")
    if cards:
        body.insert(0, f'<div class=cards style="grid-template-columns: repeat({len(cards)}, 1fr)">{"".join(cards)}</div>')
    cls = "f title" if scene["n"] == 1 else ("f dense" if len(lines) >= 5 or sum(len(l) for l in lines) > 260 else "f")
    return (f'<section class="{cls}"><div class=kicker>{inline(scene["kicker"])}</div><h1>{inline(scene["title"])}</h1>'
            f'<div class=body>{"".join(body)}</div>'
            f'<div class=foot><span>{html.escape(FOOT)}</span><span>{scene["n"]} / {total}</span></div></section>')


def render_slides(scenes: list[dict]) -> list[Path]:
    work = WORK / "slides"
    work.mkdir(parents=True, exist_ok=True)
    page, pdf = work / "slides.html", work / "slides.pdf"
    page.write_text(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>'
                    + "".join(slide_html(s, len(scenes)) for s in scenes), encoding="utf-8")
    for old in work.glob("s-*.png"):
        old.unlink()
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", page.as_uri()], check=True, capture_output=True)
    # CSS px -> PDF pt 는 0.75배라 96dpi 로 되돌리면 정확히 1920x1080 이 된다
    subprocess.run(["pdftoppm", "-png", "-r", "96", str(pdf), str(work / "s")], check=True)
    shots = sorted(work.glob("s-*.png"))
    assert len(shots) == len(scenes), f"슬라이드 수가 맞지 않는다: {len(shots)} != {len(scenes)}"
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
    scenes = parse(SCRIPT.read_text(encoding="utf-8"))
    shots = render_slides(scenes)
    if "--slides-only" in sys.argv:
        print(f"슬라이드 {len(shots)}장: {shots[0].parent}")
        sys.exit(0)
    wavs, seconds = [], []
    for s in scenes:
        wav, sec = scene_audio(s)
        wavs.append(wav); seconds.append(sec)
        print(f"장면 {s['n']:2d} {sec:6.1f}초  {sum(len(p) for p in s['narration']):4d}자  {s['title']}")
    return encode(shots, seconds, join_audio(wavs)), seconds


def demo() -> None:
    out, seconds = build()
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                           "-of", "default=nw=1:nk=1", str(out)], check=True, capture_output=True, text=True).stdout.split()
    width, height, total = int(info[1]), int(info[2]), float(info[-1])
    assert (width, height) == (W, H), f"해상도가 다르다: {width}x{height}"
    assert "audio" in info, "소리가 들어가지 않았다"
    assert abs(total - sum(seconds)) < 1, f"길이가 어긋난다: {total:.1f} vs {sum(seconds):.1f}"
    chars = sum(len(p) for s in parse(SCRIPT.read_text(encoding="utf-8")) for p in s["narration"])
    print(f"{out.name} · {width}x{height} · {total / 60:.1f}분 · {out.stat().st_size / 1e6:.0f}MB · 대본 {chars:,}자 · 목소리 {VOICE}")


if __name__ == "__main__":
    demo()
