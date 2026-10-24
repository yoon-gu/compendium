#!/usr/bin/env python3
"""녹음 캐시의 조각 wav 를 whisper 로 다시 받아 적어 대본과 얼마나 맞는지 잰다(LLM 기반 TTS 가 문장을 빼먹거나 바꿔 읽는 사고 검출).

    python3 video/ttscheck.py <슬러그> --voice=sohee [--min=0.75]   # 유사도가 낮은 조각을 표로 보여 준다
    python3 video/ttscheck.py <슬러그> --voice=sohee --delete       # 낮은 조각 wav 를 지운다 → qwentts.py 가 그 조각만 다시 만든다

유사도 = difflib ratio(공백·문장부호 제거, 대본은 pronounce.tsv 적용 뒤). whisper(small, ko)의 받아쓰기 오차도 섞이므로 0.75 아래만 의심한다.
"""
import difflib
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
slug = next(a for a in sys.argv[1:] if not a.startswith("--"))
opt = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--") and "=" in a}
voice = opt.get("--voice", "진우")
threshold = float(opt.get("--min", "0.75"))
delete = "--delete" in sys.argv
sys.argv = ["build.py", slug, f"--voice={voice}"] + [a for a in sys.argv[1:] if a.startswith("--script=")]
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", HERE / "build.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

_, scenes = b.parse(b.SCRIPT.read_text(encoding="utf-8"))
pieces = [c for s in scenes for f in s["frames"] for para in f["narration"]
          for part in para.split("‖") if part.strip() for c in b.chunks(part.strip())]
cache = b.WORK / f"voice-{voice}"


def norm(s):
    return re.sub(r"[\s.,?!'\"·…:;()\[\]]+", "", s)


def transcribe(wav):
    out = Path(tempfile.mkdtemp())
    subprocess.run(["/opt/homebrew/bin/whisper", str(wav), "--model", "small", "--language", "ko", "--output_format", "json",
                    "--output_dir", str(out), "--verbose", "False"], check=True, capture_output=True)
    return json.loads(next(out.glob("*.json")).read_text())["text"]


low = []
for i, raw in enumerate(pieces, 1):
    said = b.spoken(raw)
    wav = cache / (hashlib.sha1(f"{b.VOICE_ID}|{b.EMOTION}|{b.MODEL}|{said}".encode()).hexdigest()[:12] + ".wav")
    if not wav.exists():
        print(f"[{i:2d}] (없음) {said[:40]}…"); continue
    heard = transcribe(wav)
    r = difflib.SequenceMatcher(None, norm(said), norm(heard)).ratio()
    flag = "  " if r >= threshold else "!!"
    print(f"[{i:2d}] {flag} {r:.2f} {said[:34]}…")
    if r < threshold:
        low.append((i, r, said, heard, wav))

print(f"\n조각 {len(pieces)}개, 의심 {len(low)}개 (유사도 < {threshold})")
for i, r, said, heard, wav in low:
    print(f"\n--- [{i}] {r:.2f} {wav.name}\n대본: {said}\n들림: {heard.strip()}")
    if delete:
        wav.unlink(); print("→ 지움")
