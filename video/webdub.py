#!/usr/bin/env python3
"""타입캐스트 웹 에디터에서 만든 나레이션을 build.py 녹음 캐시에 넣는다(API 크레딧 대신 웹으로 녹음할 때).

    python3 video/webdub.py <슬러그> --list              # 웹에 붙여 넣을 조각(한 줄에 하나, 발음 교정 반영)
    python3 video/webdub.py <슬러그> ~/Downloads/x.zip   # 웹에서 받은 audio_0…audio_N 을 조각 순서대로 캐시에 넣는다
    (--list 는 캐시에 없는 조각만 뽑고 싶으면 --list-missing. 받은 파일 수가 빠진 조각 수와 같으면 빠진 조각에 차례로 넣는다)

조각 = build.py 가 TTS 한 번에 보내는 단위(문단을 ‖ 에서 자르고 300자 넘으면 문장 경계에서 자른 것).
웹 에디터에서 조각마다 문단 하나로 두고 목소리는 진우, 문단별 파일로 내려받는다. 캐시 이름은 build.py 의 tts() 와 같다.
"""
import hashlib
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

slug, arg = sys.argv[1], sys.argv[2]
sys.argv = ["build.py", slug]                       # build.py 는 import 할 때 sys.argv 를 읽는다
import importlib.util                               # noqa: E402
spec = importlib.util.spec_from_file_location("build", Path(__file__).with_name("build.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

_, scenes = b.parse(b.SCRIPT.read_text(encoding="utf-8"))
pieces = [c for s in scenes for f in s["frames"] for para in f["narration"]
          for part in (x.strip() for x in para.split("‖")) if part for c in b.chunks(part)]
spoken = [b.spoken(c) for c in pieces]
cache = b.WORK / f"voice-{b.VOICE}"
dest_of = lambda text: cache / (hashlib.sha1(f"{b.VOICE_ID}|{b.EMOTION}|{b.MODEL}|{text}".encode()).hexdigest()[:12] + ".wav")
missing = [t for t in spoken if not dest_of(t).exists()]

if arg in ("--list", "--list-missing"):
    print("\n".join(spoken if arg == "--list" else missing))
    sys.exit()

src = Path(arg).expanduser()
if src.suffix == ".zip":
    tmp = Path(tempfile.mkdtemp())
    zipfile.ZipFile(src).extractall(tmp)
    src = tmp
num = lambda p: int(re.match(r"\D*(\d+)", p.name).group(1))
files = sorted((p for p in src.rglob("*") if p.suffix.lower() in (".wav", ".mp3")), key=num)
targets = spoken if len(files) == len(spoken) else missing     # 고친 조각만 다시 받았으면 빠진 조각에 차례로
assert len(files) == len(targets), f"받은 파일 {len(files)}개 ≠ 조각 {len(spoken)}개(빠진 조각 {len(missing)}개)"
cache.mkdir(parents=True, exist_ok=True)
for p, text in zip(files, targets):
    dest = dest_of(text)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(p), "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(dest)], check=True)
    print(f"{p.name[:12]} → {text[:30]}…")
print(f"{len(files)}조각을 넣었다: {cache}")
