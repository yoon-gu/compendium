#!/usr/bin/env python3
"""빌드된 영상에 효과음을 섞는다. 지금은 코드 타이핑 클립의 키보드 소리(figures/code-*-keys.wav, codeanim.py 가 만든다)를
그 화면이 시작하는 시각에 얹는다. build.py 는 클립을 무음으로 올리므로 빌드 뒤에 한 번 돌린다.

    python3 video/sfx.py <슬러그> --voice=sohee [--gain=0.35]   # out/<슬러그>-가로.mp4 → 같은 파일(원본은 out/*-nosfx.mp4 로 보관)

화면 시작 시각은 build.py 의 scene_audio 로 다시 계산한다(녹음 캐시가 있어야 한다). 영상은 다시 인코딩하지 않는다(-c:v copy).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
slug = next(a for a in sys.argv[1:] if not a.startswith("--"))
opt = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--") and "=" in a}
gain = float(opt.get("--gain", "0.35"))
sys.argv = ["build.py", slug, "--wide"] + [a for a in sys.argv[1:] if a.startswith("--voice=")]
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", HERE / "build.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

_, scenes = b.parse(b.SCRIPT.read_text(encoding="utf-8"))
t, hits = 0.0, []
for s in scenes:
    _, secs = b.scene_audio(s)
    for f, d in zip(s["frames"], secs):
        for ln in f["slide"]:
            m = re.match(r"!\[\]\(figures/(code-[^)]+)\.mp4\)", ln.strip())
            if m and (b.HERE / "figures" / f"{m[1]}-keys.wav").exists():
                hits.append((t, b.HERE / "figures" / f"{m[1]}-keys.wav"))
        t += d

video = b.OUT
keep = video.with_name(video.stem + "-nosfx.mp4")
if not keep.exists():
    shutil.copy2(video, keep)
inputs, chain = ["-i", str(keep)], []
for i, (t0, wav) in enumerate(hits, 1):
    inputs += ["-i", str(wav)]
    chain.append(f"[{i}:a]adelay={int(t0 * 1000)}|{int(t0 * 1000)},volume={gain}[k{i}]")
mix = "".join(f"[k{i}]" for i in range(1, len(hits) + 1))
chain.append(f"[0:a]{mix}amix=inputs={len(hits) + 1}:normalize=0:duration=first[a]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain), "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(video)], check=True)
print(f"{video.name}: 키보드 효과음 {len(hits)}곳, gain {gain}")
