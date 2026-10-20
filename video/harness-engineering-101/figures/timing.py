#!/usr/bin/env python3
"""녹음이 끝난 뒤, 모션 그래픽이 붙은 화면의 나레이션에서 언급 시각을 잡아 <이름>-timing.json 을 쓴다.

    python3 timing.py --voice=유나            # build.py 와 같은 목소리 캐시를 쓴다 → array-grow/loop/cache/errors-timing.json
    python3 animate.py array-grow loop cache errors && (cd ../.. && python3 build.py harness-engineering-101 --wide --voice=유나)

화면 길이(duration)는 build.py 의 scene_audio 와 같은 계산이고, 단어 시각은 whisper(small, ko)로 조각 wav 마다 잡아 조각 앞 무음을 더한다.
표시 규칙(언제 무엇이 뜨는지)은 아래 RULES 에 있다: 열거가 나레이션에 없는 화면은 구간 안에 고르게 나눈다.
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = HERE.parent.name
sys.argv = ["build.py", SLUG, "--wide"] + [a for a in sys.argv[1:] if a.startswith("--voice=")]
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", HERE.parent.parent / "build.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

ANIMS = ["array-grow", "loop", "cache", "errors"]


def words_of(wav: Path):
    """whisper 단어 시각 [(단어, 시작초)]"""
    out = Path(tempfile.mkdtemp())
    subprocess.run(["/opt/homebrew/bin/whisper", str(wav), "--model", "small", "--language", "ko", "--word_timestamps", "True",
                    "--output_format", "json", "--output_dir", str(out), "--verbose", "False"], check=True, capture_output=True)
    d = json.loads(next(out.glob("*.json")).read_text())
    return [(w["word"].strip(), w["start"]) for seg in d["segments"] for w in seg.get("words", [])]


def frame_words(frame):
    """화면의 나레이션을 build.py 와 같은 순서로 조각내어, 화면 시작 기준 단어 시각과 조각 경계(‖ 자리)를 모은다."""
    t, words, pauses = 0.0, [], []
    for p, para in enumerate(frame["narration"]):
        parts = [x.strip() for x in para.split("‖") if x.strip()]
        for k, part in enumerate(parts):
            cs = b.chunks(part)
            for c, text in enumerate(cs):
                wav = b.tts(text)
                words += [(w, t + s) for w, s in words_of(wav)]
                with wave.open(str(wav)) as f:
                    t += f.getnframes() / f.getframerate()
                if c < len(cs) - 1:
                    t += b.GAP_CHUNK
            if k < len(parts) - 1 or para.rstrip().endswith("‖"):
                pauses.append(t); t += b.GAP_THINK
        if p < len(frame["narration"]) - 1:
            t += b.GAP_PARA
    return words, pauses, t


def first(words, *keys):
    for w, s in words:
        if any(k in w for k in keys):
            return s
    return None


def spread(a, z, n):
    return [round(a + (z - a) * i / max(n - 1, 1), 2) for i in range(n)]


def RULES(name, words, pauses, speech_end, dur):
    if name == "array-grow":   # 턴 4개 → /clear → 턴 2개. '클리어'가 기준
        tc = first(words, "클리어", "클리") or speech_end * 0.55
        return spread(0.6, tc - 0.6, 4) + [round(tc - 0.1, 2)] + spread(tc + 1.0, speech_end - 1.0, 2)
    if name == "loop":         # 호출 6개를 '여섯'부터 끝까지 고르게
        t6 = first(words, "여섯") or 1.0
        return spread(t6 - 0.1, speech_end - 1.5, 6)
    if name == "cache":        # 바퀴 5개는 ‖ 앞 구간에, 결론은 ‖ 뒤
        tp = pauses[0] if pauses else speech_end * 0.6
        return spread(0.6, tp - 0.5, 5) + [round(tp + b.GAP_THINK + 0.2, 2)]
    if name == "errors":       # 정직한 줄 → 삼킨 줄 → 결론('체크포인트')
        tc = first(words, "체크포인트", "체크") or speech_end * 0.7
        return [0.5, round((0.5 + tc) / 2, 2), round(tc - 0.1, 2)]
    raise KeyError(name)


def main():
    meta, scenes = b.parse(b.SCRIPT.read_text(encoding="utf-8"))
    for s in scenes:
        _, secs = b.scene_audio(s)
        for frame, dur in zip(s["frames"], secs):
            for name in ANIMS:
                if any(ln.strip() == f"![](figures/{name}.mp4)" for ln in frame["slide"]):
                    words, pauses, speech_end = frame_words(frame)
                    marks = RULES(name, words, pauses, speech_end, dur)
                    assert marks == sorted(marks) and marks[-1] < dur, (name, marks, dur)
                    (HERE / f"{name}-timing.json").write_text(json.dumps({"duration": round(dur, 2), "marks": marks}, ensure_ascii=False))
                    print(f"{name}: 화면 {dur:.1f}초, 말 {speech_end:.1f}초, 표시 {marks}")


if __name__ == "__main__":
    main()
