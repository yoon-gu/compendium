#!/usr/bin/env python3
"""video/<슬러그>/podcast.md 를 읽어 두 진행자 대화 오디오를 굽는다(화면 없음).

    python3 podcast.py <슬러그> --dry        # 보낼 글자 수·예상 크레딧만 보여 준다(캐시된 조각은 0)
    python3 podcast.py <슬러그>              # 타입캐스트로 녹음 → <슬러그>/out/<슬러그>-podcast.m4a + -podcast-chapters.txt
    python3 podcast.py <슬러그> --preview    # macOS 목소리(Reed·Yuna)로 미리 듣기 — 크레딧 0

podcast.md 형식
- 첫 `##` 앞: `화자: 지민=준호, 서연=다은`(이름=build.py VOICES 이름 또는 tc_ 아이디). 나레이션 목소리(NARRATORS)는 쓸 수 없다.
- `이름: 말` 한 줄이 말 한 차례. 줄 앞 `(짧게) ` 는 앞 말에 바로 붙는 맞장구(쉼을 짧게).
- 말 속 `‖` 는 생각하는 쉼. `## …` 줄은 구간(읽지 않음, 유튜브 챕터 이름이 된다).

차례마다 시작 시각은 work/podcast-turns.tsv 에 남는다(화면을 입힐 때 `@분:초` 기준).
녹음은 build.py 와 같은 캐시(work/voice-<목소리>/<내용 해시>.wav)를 쓰므로 고친 줄만 다시 산다. 쉼은 무음이라 바꿔도 크레딧 0.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SLUG = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
assert SLUG, "사용법: python3 podcast.py <슬러그> [--dry|--preview]"
VIDEO = Path(__file__).resolve().parent
HERE = VIDEO / SLUG
DRY, PREVIEW = "--dry" in sys.argv, "--preview" in sys.argv
TTS_URL = "https://api.typecast.ai/v1/text-to-speech"
KEY_PATH = Path.home() / ".config/typecast-key.txt"
MODEL = "ssfm-v30"
# ponytail: build.py 와 같은 목록을 복사해 둔다(build.py 는 import 하면 바로 실행된다)
VOICES = {"진우": "tc_632293f759d649937b97f323", "준호": "tc_632a7588e7c78a412f5a36cd",
          "다은": "tc_692799c46508f6b9468c54c7", "소혜": "tc_642f9d147ce3f79717423466",
          "진한": "tc_673ecaa071c8f61f01459243", "준규": "tc_6436dbbb602bde66c6b39504",
          "연우": "tc_5eb55cf1f0b0a700071f89c7", "김건": "tc_61c2f7741330d213c238cba6"}
# 나레이션 전용 목소리(build.py VOICES 주석). 대화편 진행자는 나레이터와 다른 인물이어야 한다 → 준호·다은·소혜
NARRATORS = {"진우", "진한", "준규", "연우", "김건"}
MAC_VOICES = ["Reed", "Yuna"]       # --preview 때 화자 순서대로
MAX_CHARS = 300
# 쉼(초). 무음이라 바꿔도 크레딧 0
GAP_TURN = 0.35      # 말이 넘어갈 때
GAP_QUICK = 0.12     # (짧게) 맞장구 앞
GAP_SAME = 0.25      # 한 사람 말 안의 300자 조각 사이
GAP_THINK = 0.8      # ‖
GAP_SECTION = 1.2    # ## 구간이 바뀔 때
PRONOUNCE = [ln.split("\t") for ln in (VIDEO / "pronounce.tsv").read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]


def parse(text: str) -> tuple[dict[str, str], list[dict]]:
    """(화자 → 목소리, 차례 목록). 차례 = {who, text, quick, section(이 차례에서 새 구간이 시작되면 그 이름)}."""
    speakers, turns, section = {}, [], None
    for line in map(str.strip, text.splitlines()):
        if line.startswith("화자:") and not turns:
            speakers = dict(p.strip().split("=") for p in line[3:].split(","))
        elif line.startswith("## "):
            section = line[3:].split("|")[-1].strip()
        elif m := re.match(r"^(\(짧게\) )?(\S+): (.+)$", line):
            if m[2] in speakers:
                turns.append({"who": m[2], "text": m[3], "quick": bool(m[1]), "section": section})
                section = None
    assert speakers and turns, "화자: 줄과 `이름: 말` 줄이 필요하다"
    taken = NARRATORS & set(speakers.values())
    assert not taken, f"{taken}은 나레이션 목소리다. 대화편은 준호·다은·소혜 중에서 고른다"
    return speakers, turns


def chunks(text: str) -> list[str]:
    """`‖` 로 자르고, 300자 넘는 조각은 문장 경계에서 다시 자른다. [(조각, 뒤에 생각 쉼?)]"""
    out = []
    parts = [p.strip() for p in text.split("‖") if p.strip()]
    for k, part in enumerate(parts):
        cur = ""
        for sent in re.split(r"(?<=[.?!])\s+", part):
            assert len(sent) <= MAX_CHARS, f"한 문장이 너무 길다: {sent[:40]}…"
            if cur and len(cur) + 1 + len(sent) > MAX_CHARS:
                out.append((cur, False)); cur = sent
            else:
                cur = f"{cur} {sent}".strip()
        out.append((cur, k < len(parts) - 1))
    return out


def spoken(text: str) -> str:
    for src, say in PRONOUNCE:
        text = re.sub(rf"(?<![A-Za-z]){re.escape(src)}(?![A-Za-z])", say, text, flags=re.I)
    return text


def cache_path(text: str, voice: str) -> Path:
    vid = VOICES.get(voice, voice)
    # build.py 의 기본(normal 프리셋)과 같은 키라 두 빌더가 캐시를 나눠 쓴다
    key = f"{vid}|normal|{MODEL}|{spoken(text)}"
    return HERE / "work" / f"voice-{voice}" / (hashlib.sha1(key.encode()).hexdigest()[:12] + ".wav")


def tts(text: str, voice: str) -> Path:
    dest, said = cache_path(text, voice), spoken(text)
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    if voice in MAC_VOICES:
        subprocess.run(["say", "-v", voice, "--file-format=WAVE", "--data-format=LEI16@24000", "-o", str(dest), said], check=True)
        return dest
    body = json.dumps({"voice_id": VOICES.get(voice, voice), "text": said, "model": MODEL,
                       "prompt": {"emotion_type": "preset", "emotion_preset": "normal"}}).encode()
    for attempt in range(5):
        req = urllib.request.Request(TTS_URL, data=body, headers={
            "X-API-KEY": KEY_PATH.read_text().strip(), "Content-Type": "application/json"})
        try:
            tmp = dest.with_suffix(".part")   # 받다가 끊겨도 반쪽 wav 가 캐시로 남지 않게
            tmp.write_bytes(urllib.request.urlopen(req, timeout=180).read())
            tmp.rename(dest)
            print(f"  타입캐스트 {voice} {len(said)}자: {said[:30]}…")
            return dest
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")[:300]
            if err.code not in (429, 500, 502, 503) or attempt == 4:
                raise RuntimeError(f"타입캐스트 호출 실패({err.code}): {detail} — {said[:40]}…") from err
            time.sleep(5 * (attempt + 1))
    raise AssertionError("unreachable")


def main() -> None:
    speakers, turns = parse((HERE / "podcast.md").read_text(encoding="utf-8"))
    if PREVIEW:
        speakers = dict(zip(speakers, MAC_VOICES))
    jobs = [(c, speakers[t["who"]]) for t in turns for c, _ in chunks(t["text"])]
    todo = [(c, v) for c, v in dict.fromkeys(jobs) if not cache_path(c, v).exists()]
    need = sum(len(spoken(c)) for c, v in todo if v not in MAC_VOICES)
    print(f"차례 {len(turns)} · 조각 {len(jobs)} · 새로 녹음 {len(todo)}조각 · 예상 크레딧 {need:,} · 목소리 {speakers}")
    if DRY:
        return
    with ThreadPoolExecutor(4) as pool:   # 타입캐스트 동시 요청 한도 5
        list(pool.map(lambda job: tts(*job), todo))

    params, data, marks, starts, samples = None, [], [], [], 0

    def add_silence(sec: float) -> None:
        nonlocal samples
        n = int(sec * params.framerate)
        data.append(b"\x00" * n * params.nchannels * params.sampwidth)
        samples += n

    for i, t in enumerate(turns):
        if i and params:
            add_silence(GAP_SECTION if t["section"] else GAP_QUICK if t["quick"] else GAP_TURN)
        if t["section"]:
            marks.append((samples, t["section"]))
        starts.append(samples)
        cs = chunks(t["text"])
        for k, (text, think) in enumerate(cs):
            with wave.open(str(tts(text, speakers[t["who"]]))) as f:
                params = params or f.getparams()
                assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == params[:3], f"wav 형식이 다르다: {text[:20]}"
                data.append(f.readframes(f.getnframes()))
                samples += f.getnframes()
            if k < len(cs) - 1:
                add_silence(GAP_THINK if think else GAP_SAME)

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    track = HERE / "work" / f"podcast-{'preview' if PREVIEW else 'track'}.wav"
    with wave.open(str(track), "wb") as w:
        w.setnchannels(params.nchannels); w.setsampwidth(params.sampwidth); w.setframerate(params.framerate)
        w.writeframes(b"".join(data))
    m4a = out / f"{SLUG}-podcast{'-preview' if PREVIEW else ''}.m4a"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(track), "-af", "loudnorm=I=-16:TP=-1.5",
                    "-c:a", "aac", "-b:a", "128k", str(m4a)], check=True)
    rate = params.framerate
    chapters = "\n".join(f"{int(s / rate // 60)}:{int(s / rate % 60):02d} {name}" for s, name in marks)
    (out / f"{SLUG}-podcast-chapters.txt").write_text(chapters + "\n", encoding="utf-8")
    # 화면 대본(script-podcast.md)의 `@분:초` 를 잡을 때 쓴다
    (HERE / "work" / "podcast-turns.tsv").write_text("".join(
        f"{s / rate // 60:.0f}:{s / rate % 60:05.2f}\t{t['who']}\t{t['text']}\n" for s, t in zip(starts, turns)), encoding="utf-8")
    print(f"{m4a.name} · {samples / rate / 60:.1f}분 · 차례 {len(turns)}\n{chapters}")


if __name__ == "__main__":
    main()
