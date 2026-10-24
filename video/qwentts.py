#!/usr/bin/env python3
"""Qwen3-TTS(로컬, Apache-2.0)로 나레이션 조각을 만들어 build.py 녹음 캐시에 넣는다(타입캐스트 크레딧 0).

    ~/.venvs/qwen3-tts/bin/python video/qwentts.py <슬러그> --voice=sohee            # 전 조각 → work/voice-sohee/
    ~/.venvs/qwen3-tts/bin/python video/qwentts.py <슬러그> --voice=sohee --limit=2  # 앞 두 조각만(속도·음질 확인)
    python3 video/build.py <슬러그> --wide --voice=sohee                             # 캐시가 다 있으면 API 호출 0

- 조각 = build.py 가 TTS 한 번에 보내는 단위(‖ 로 자르고 300자 넘으면 문장 경계). 발음 교정(pronounce.tsv)도 build.py 와 같다.
- 캐시 이름은 build.py 의 tts() 와 같은 해시라, 조각 글자가 바뀐 곳만 다시 만든다.
- 화자 이름(--voice)은 Qwen3-TTS CustomVoice 의 preset speaker(Sohee 등)를 소문자로 쓴다. 모델은 1.7B 기본, --model=0.6b 로 바꿀 수 있다.
- --instruct(기본: 차분한 강의 말투), --temperature(기본 0.6), --seed(기본 7)로 조각 사이 톤을 고르게 한다. 지시문을 바꾸면 캐시 폴더를 비우고 다시 만든다(캐시 이름에 지시문은 안 들어간다).
- 장치는 MPS(Apple Silicon) → CPU 순으로 고른다. dtype 은 --dtype=fp16(기본)|fp32|bf16. 출력은 16비트 모노 wav(모델 샘플레이트 그대로).
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
dtype_name = opt.get("--dtype", "fp16")                # 16GB 맥에서 1.7B fp32(≈8GB)는 스왑을 일으킨다 → 기본 fp16
# 조각마다 감정이 널뛰지 않게: 같은 지시문 + 낮은 온도 + 조각마다 같은 시드. 지시문은 모든 조각에 똑같이 준다
instruct = opt.get("--instruct", "차분하고 안정된 강의 말투. 감정 기복 없이 처음부터 끝까지 일정한 속도와 높낮이로, 또렷하고 친절하게 읽는다.")
temperature = float(opt.get("--temperature", "0.6"))
seed = int(opt.get("--seed", "7"))
tempo = float(opt.get("--tempo", "1.0"))                   # 1.2 면 ffmpeg atempo 로 1.2배(음높이 유지)해서 저장
MAX_SEC_PER_CHAR = float(opt.get("--max-spc", "0.26"))     # 이보다 느리면 긴 무음·반복이 붙은 것 → 시드를 바꿔 다시 만든다
MAX_GAP = float(opt.get("--max-gap", "2.5"))                # 문장 사이 무음이 이보다 길어도 다시 만든다(TTS가 중간에 멈추는 사고)


def longest_gap(wav, sr, thr=0.02, win=0.05):
    """가장 긴 내부 무음(초). 50ms 창의 최대 진폭이 thr 아래인 구간."""
    n = int(win * sr)
    env = np.array([np.abs(wav[i:i + n]).max() for i in range(0, len(wav) - n, n)])
    best = cur = 0
    for v in env > thr:
        cur = 0 if v else cur + 1; best = max(best, cur)
    return best * win

sys.argv = ["build.py", slug, f"--voice={voice}"] + [a for a in sys.argv[1:] if a.startswith("--script=")]   # build.py 는 import 할 때 sys.argv 를 읽는다
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
dtype = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[dtype_name]
t0 = time.time()
model = Qwen3TTSModel.from_pretrained(model_id, device_map=device, dtype=dtype)
print(f"모델 {model_id} ({device}, {dtype}) 로드 {time.time() - t0:.0f}초")

total_audio = 0.0
for i, (raw, dest, said) in enumerate(todo, 1):
    t1 = time.time()
    for attempt in range(4):
        torch.manual_seed(seed + attempt)
        wavs, sr = model.generate_custom_voice(text=said, language="Korean", speaker=speaker, instruct=instruct or None,
                                               do_sample=True, temperature=temperature, top_p=0.9, top_k=50,
                                               max_new_tokens=int(len(said) * 4.5) + 60)   # 12Hz 코덱: 글자당 토큰 ~3, 여유 50%
        wav = np.asarray(wavs[0], dtype=np.float32)
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        wav = np.clip(wav, -1.0, 1.0)
        sec = len(wav) / sr; gap = longest_gap(wav, sr)
        if sec / len(said) <= MAX_SEC_PER_CHAR and gap <= MAX_GAP:
            break
        print(f"     느림({sec:.0f}초/{len(said)}자) 또는 무음 {gap:.1f}초 → 시드 {seed + attempt + 1}로 다시")
    sf.write(str(dest), (wav * 32767).astype(np.int16), sr, subtype="PCM_16")
    if tempo != 1.0:
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dest), "-filter:a", f"atempo={tempo}", "-ar", str(sr), "-ac", "1",
                        "-sample_fmt", "s16", str(dest) + ".tmp.wav"], check=True)
        Path(str(dest) + ".tmp.wav").replace(dest)
        sec /= tempo
    total_audio += sec
    print(f"  [{i}/{len(todo)}] {sec:5.1f}초 음성, {time.time() - t1:5.1f}초 걸림: {said[:28]}…")
print(f"끝. 음성 {total_audio / 60:.1f}분, 걸린 시간 {(time.time() - t0) / 60:.1f}분, 샘플레이트 {sr}")
