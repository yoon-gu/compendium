#!/usr/bin/env python3
"""녹음이 끝난 뒤, 모션 그래픽 화면의 나레이션에서 언급 시각을 whisper 로 잡아 <이름>-timing.json 을 쓴다.

    python3 timing.py --voice=진우 && sh render.sh && (cd ../.. && python3 build.py toss-targeting-model-automation --voice=진우)

화면 길이는 build.py 의 scene_audio 계산, 단어 시각은 조각 wav 마다 whisper(small, ko). 표시 규칙은 RULES.
(토스 멀티태스크 회차의 timing.py 를 이 회차의 Remotion 열여섯 편에 맞게 바꾼 것)
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
    "questions": [("주피터",), ("두 주에서", "2주", "하루로"), ("피처를 몇", "피쳐를 몇 개"), ("어떤 구조를",), ("기존 모델보다",), ("입력 데이터를",), ("손으로",), ("파이프라인에",)],
    "ranking": [("점수를",), ("줄을 세운",), ("상위 오 퍼센트", "5%", "오 퍼센트"), ("회수율은",), ("실행률은",), ("에이유씨는", "AUC는"), ("PRAUC", "PR", "피알")],
    "elbow": [("피처는", "입력 항목", "중요도 순으로"), ("같은 비율",), ("엘보였", "엘보"), ("꺾이는",), ("칠십오", "75"), ("몰려",), ("남아 있",)],
    "ktable": [("사백오십팔", "458"), ("칠십오", "75"), ("팔십사", "84"), ("눈여겨볼",), ("칠십칠", "77"), ("결론이 달라", "결론이")],
    "autok": [("Auto", "오토 케이", "오토"), ("순서를 정해", "중요도 순서"), ("늘려 가며", "늘려"), ("가장 작은 값",), ("예전 비율",), ("다섯 배", "5배"), ("이 점 육", "2.6", "2점6")],
    "funnel": [("펄널이라고", "퍼널이라고", "흐름을"), ("따로 학습",), ("곱해서",), ("남남",), ("절실한",), ("다섯 개", "5개"), ("열한 가지", "11가지"), ("수십 개로",)],
    "aitm": [("에이아이티엠", "AITM"), ("정보 전달",), ("가중치로",), ("단조성",), ("벌점",), ("모순",), ("한 테이블",), ("마지막 단계",)],
    "treevsdl": [("운영 중인 퍼널", "운영 중인"), ("일 점 사", "1.4", "1점4"), ("영 점 육", "0.6", "0점6"), ("반대",), ("칠 퍼센트", "7%"), ("삼 퍼센트", "3%"), ("안정적으로",), ("초기에는",)],
    "report": [("손으로 이어",), ("정답 테이블만",), ("로그에",), ("벌어졌는지",), ("비교표도",), ("일 분이", "1분이"), ("100분", "백분위", "마켓터"), ("정답은 아는", "아는 고객", "정답을 아는"), ("부호를",)],
    "direction": [("기어했는지", "기여했는지", "피처마다"), ("순열 중요도", "순열"), ("거꾸로",), ("내리는지",), ("크기와 방향을",), ("느낌표",), ("하위 십", "하위 10"), ("팔십오", "85"), ("신경망은",)],
    "pinned": [("매일 다시 학습해",), ("회수율은 같",), ("이틀 연속",), ("칠십일", "71"), ("구십오", "95"), ("고정하기로",), ("피처목록입니다", "대상은", "피쳐 목록"), ("해식", "해시", "지문")],
    "missing": [("원천 데이터까지", "원천 데이터"), ("4분의", "사분의 일"), ("빈 값을",), ("십삼에서", "13"), ("빈 피처를", "빈피처", "셉니다"), ("십 퍼센트를", "10%"), ("알람이",), ("신호로도",), ("영에서", "0%", "0에서")],
    "leak": [("세 평가일",), ("마지막 하루만",), ("피처 하나만", "하나만 점수처럼", "점수처럼"), ("십칠", "17"), ("달 단위로",), ("뒤에 행동", "그 뒤의 행동", "행동까지"), ("미래 정보",), ("샵으로", "샵")],
    "fixes": [("두 피처는", "빼고"), ("섞어서",), ("다시 봐요",), ("확정돼",)],
    "lessons": [("실험으로",), ("팔십사", "84"), ("라벨 테이블",), ("삼십 분", "30분"), ("계속 의심",), ("고정했고",), ("멈췄습니다",), ("쫓아갔",)],
    "closing": [("판단에만 집중", "판단에만"), ("어떤 행동을",), ("충분한지",), ("채택할지",), ("자동화한 건",), ("숫자를 믿을",), ("왜 하필",)],
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
                if not any(ln.strip().endswith(f"](figures/{name}.mp4)") for ln in frame["slide"]):
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
