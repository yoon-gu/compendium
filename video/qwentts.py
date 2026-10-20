#!/usr/bin/env python3
"""Qwen3-TTS(로컬, Apache-2.0)로 나레이션 조각을 만들어 build.py 녹음 캐시에 넣는다(타입캐스트 크레딧 0).

    ~/.venvs/qwen3-tts/bin/python video/qwentts.py <슬러그> --voice=sohee            # 전 조각 → work/voice-sohee/
    ~/.venvs/qwen3-tts/bin/python video/qwentts.py <슬러그> --voice=sohee --limit=2  # 앞 두 조각만(속도·음질 확인)
    python3 video/build.py <슬러그> --wide --voice=sohee                             # 캐시가 다 있으면 API 호출 0

- 조각 = build.py 가 TTS 한 번에 보내는 단위(‖ 로 자르고 300자 넘으면 문장 경계). 발음 교정(pronounce.tsv)도 build.py 와 같다.
- 캐시 이름은 build.py 의 tts() 와 같은 해시라, 조각 글자가 바뀐 곳만 다시 만든다.
- 화자 이름(--voice)은 Qwen3-TTS CustomVoice 의 preset speaker(Sohee 등)를 소문자로 쓴다. 모델은 1.7B 기본, --model=0.6b 로 바꿀 수 있다.
- 장치는 MPS(Apple Silicon) → CPU 순으로 고른다. 출력은 16비트 모노 wav(모델 샘플레이트 그대로).
"""
import hashlib
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
slug = next(a for a in sys.argv[1:] if not a.startswith("--"))
opt = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--") and "=" in a}
voice = opt.get("--voice", "sohee")
speaker = voice[:1].upper() + voice[1:]            # sohee → Sohee
model_id = {"0.6b": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"}.get(opt.get("--model", "1.7b").lower(), "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice")
limit = int(opt.get("--limit", "0"))

sys.argv = ["build.py", slug, f"--voice={voice}"]   # build.py 는 import 할 때 sys.argv 를 읽는다
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", HERE / "build.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

_, scenes = b.parse(b.SCRIPT.read_text(encoding="utf-8"))
pieces = [c for s in scenes for f in s["frames"] for para in f["narration"]
          for part in para.split("‖") if part.strip() for c in b.chunks(part.strip())]
cache = b.WORK / f"voice-{voice}"
cache.mkdir(parents=True, exist_ok=True)


def dest_of(text):   # build.tts() 와 같은 이름
    said = b.spoken(text)
    return cache / (hashlib.sha1(f"{b.VOICE_ID}|{b.EMOTION}|{b.MODEL}|{said}".encode()).hexdigest()[:12] + ".wav"), said


todo = [(p, *dest_of(p)) for p in pieces]
todo = [t for t in todo if not t[1].exists()]
if limit:
    todo = todo[:limit]
print(f"조각 {len(pieces)}개 중 만들 것 {len(todo)}개 → {cache}")
if not todo:
    sys.exit(0)

import torch  # noqa: E402
from qwen_tts import Qwen3TTSModel  # noqa: E402

device = "mps" if torch.backends.mps.is_available() else "cpu"
dtype = torch.float32
t0 = time.time()
model = Qwen3TTSModel.from_pretrained(model_id, device_map=device, dtype=dtype)
print(f"모델 {model_id} ({device}, {dtype}) 로드 {time.time() - t0:.0f}초")

total_audio = 0.0
for i, (raw, dest, said) in enumerate(todo, 1):
    t1 = time.time()
    wavs, sr = model.generate_custom_voice(text=said, language="Korean", speaker=speaker)
    wav = np.asarray(wavs[0], dtype=np.float32)
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    wav = np.clip(wav, -1.0, 1.0)
    sf.write(str(dest), (wav * 32767).astype(np.int16), sr, subtype="PCM_16")
    sec = len(wav) / sr; total_audio += sec
    print(f"  [{i}/{len(todo)}] {sec:5.1f}초 음성, {time.time() - t1:5.1f}초 걸림: {said[:28]}…")
print(f"끝. 음성 {total_audio / 60:.1f}분, 걸린 시간 {(time.time() - t0) / 60:.1f}분, 샘플레이트 {sr}")
