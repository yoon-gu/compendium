#!/usr/bin/env python3
"""녹음이 끝난 뒤, 모션 그래픽 화면의 나레이션에서 언급 시각을 whisper 로 잡아 <이름>-timing.json 을 쓴다.

    python3 timing.py --voice=진우 && sh render.sh && (cd ../.. && python3 build.py toss-multi-task-learning-finance --voice=진우)

화면 길이는 build.py 의 scene_audio 계산, 단어 시각은 조각 wav 마다 whisper(small, ko). 표시 규칙은 RULES.
(규칙은 무신사 회차의 timing.py 를 이 회차의 Remotion 네 편에 맞게 바꾼 것)
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
    "explosion": [("이 유저가", "다음 달에", "트리 모델을 하나씩"), ("과제가 늘고", "과제가 늘"), ("상품도 늘어나면", "상품도"), ("곱한 만큼", "곱한"), ("수십 개", "수백 개"), ("매일",)],
    "ple": [("멀티태스크 학습", "멀티테스크"), ("공유 인코더",), ("출력층만", "끝부분"), ("간섭",), ("공유 전문가와", "과제별 전문가"), ("게이트도", "게이트"), ("자기 전문가만", "자기 전문가")],
    "mask": [("뼈대는 같아요", "뼈대는", "섞여 있어요"), ("아니오라면", "답이 아니오"), ("통째로",), ("손실만",), ("손실은 모델의", "잰 값")],
    "shortcut": [("좋은 신호를", "좋은 신호"), ("흐려집니다", "흐려"), ("전용 길", "전용기", "전용"), ("나란히",), ("트리 모델도", "분기를"), ("가장 크게 달라진", "딥러닝으로")],
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
