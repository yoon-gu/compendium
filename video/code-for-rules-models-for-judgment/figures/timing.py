#!/usr/bin/env python3
"""녹음이 끝난 뒤, 모션 그래픽 화면의 나레이션에서 언급 시각을 whisper 로 잡아 <이름>-timing.json 을 쓴다.

    python3 timing.py --voice=진우 && python3 animate.py && (cd ../.. && python3 build.py code-for-rules-models-for-judgment --voice=진우)

화면 길이는 build.py 의 scene_audio 계산, 단어 시각은 조각 wav 마다 whisper(small, ko). 표시 규칙은 RULES.
(하니스 101 회차의 timing.py 를 이 회차의 네 애니메이션에 맞게 줄인 것)
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = HERE.parent.name
sys.argv = ["build.py", SLUG] + [a for a in sys.argv[1:] if a.startswith(("--voice=", "--script="))]
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", HERE.parent.parent / "build.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

# 이름 → [(단어 후보…), …] 표시 시각 순서. 못 찾으면 앞 표시 + 2초
RULES = {
    "decide": [("그냥 물으면", "그냥"), ("꼴을", "아예 묶"), ("모르겠음이라는", "보기를 하나 더"), ("더 큰 모델", "넘어가요")],
    "questions": [("첫째",), ("둘째",), ("셋째",), ("셋 다", "비로소")],
    "steps": [("주문번호",), ("의도별로", "의도별"), ("택배사", "송장번호"), ("티켓을", "티켓"), ("답장 쓰기", "마지막으로"), ("다섯 단계 중", "하나뿐")],
    "fastpath": [("빠른 길",), ("하루", "100만", "백만", "오만", "5만"), ("더 싼", "바꾸기도")],
}


def words_of(wav: Path):
    out = Path(tempfile.mkdtemp())
    subprocess.run(["/opt/homebrew/bin/whisper", str(wav), "--model", "small", "--language", "ko", "--word_timestamps", "True",
                    "--output_format", "json", "--output_dir", str(out), "--verbose", "False"], check=True, capture_output=True)
    d = json.loads(next(out.glob("*.json")).read_text())
    return [(w["word"].strip(), w["start"]) for seg in d["segments"] for w in seg.get("words", [])]


def frame_words(frame):
    """build.py 와 같은 순서로 조각내어 화면 시작 기준 단어 시각을 모은다."""
    t, words = 0.0, []
    for p, para in enumerate(frame["narration"]):
        parts = [x.strip() for x in para.split("‖") if x.strip()]
        for k, part in enumerate(parts):
            cs = b.chunks(part)
            for c, text in enumerate(cs):
                wav = b.voice(text, b.is_slow(frame))
                words += [(w, t + s) for w, s in words_of(wav)]
                with wave.open(str(wav)) as f:
                    t += f.getnframes() / f.getframerate()
                if c < len(cs) - 1:
                    t += b.GAP_CHUNK
            if k < len(parts) - 1 or para.rstrip().endswith("‖"):
                t += b.GAP_THINK
        if p < len(frame["narration"]) - 1:
            t += b.GAP_PARA
    return words, t


def first(words, keys, after):
    """after 이후, 단어 후보 중 하나가 처음 들리는 시각(띄어쓰기 무시)."""
    flat, starts = "", []
    for w, s in words:
        starts += [s] * len(w.replace(" ", "")); flat += w.replace(" ", "")
    for k in keys:
        i = flat.find(k.replace(" ", ""))
        while i >= 0 and starts[i] < after:
            i = flat.find(k.replace(" ", ""), i + 1)
        if i >= 0:
            return starts[i]
    return None


def main():
    meta, scenes = b.parse(b.SCRIPT.read_text(encoding="utf-8"))
    b.PAD_TO_CLIP = False
    for s in scenes:
        _, secs = b.scene_audio(s)
        for frame, dur in zip(s["frames"], secs):
            for name, rules in RULES.items():
                if not any(ln.strip() == f"![](figures/{name}.mp4)" for ln in frame["slide"]):
                    continue
                words, end = frame_words(frame)
                marks, last = [], 0.0
                for keys in rules:
                    t = first(words, keys, last)
                    if t is None:
                        print(f"   (못 찾음) {name} {keys[0]!r}")
                        t = last + 2.0
                    last = round(max(t - 0.3, last + 0.6 if marks else 0.3), 2)
                    marks.append(last)
                assert marks[-1] < dur, (name, marks, dur)
                (HERE / f"{name}-timing.json").write_text(json.dumps({"duration": round(dur, 2), "marks": marks}))
                print(f"{name}: 화면 {dur:.1f}초, 말 {end:.1f}초, 표시 {marks}")


if __name__ == "__main__":
    main()
