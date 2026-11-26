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
    "costs": [("학습 데이터 준비", "파이프라인"), ("다시 학습하긴", "오래 그대로"), ("실험이", "미뤄"), ("드문 행동", "혼자 배우기엔"), ("새로 나온 상품", "예측할 방법")],
    "two-uses": [("두 갈래",), ("공유 표현",), ("테이스트",), ("이번 글은",), ("예측값 자체", "예측값"), ("마케팅과 서비스", "바로 씁니다")],
    "share": [("공유 부분이", "모든 과제의 데이터"), ("정답이 드문", "드문 과제도"), ("출발점",), ("입력도 넓어",), ("표 한 줄",), ("신경망은",)],
    "case1": [("목적마다",), ("최근 행동",), ("유저 프로필",), ("섞어",), ("공유 전문가",), ("수십 개 확률", "수십 개"), ("동의 기반",), ("드문 행동일수록", "무게를")],
    "topn": [("에이피가", "평균 정밀도"), ("재현률도", "재현율도", "상위 엔 명"), ("거의 같았", "에이유씨는 거의"), ("전체 순위",), ("맨 위 엔 명", "맨 위"), ("바로 그 위쪽", "위쪽이 얼마나")],
    "online": [("AB", "에이비 테스트", "에이비"), ("첫 번째 상품군",), ("불필요한 발송", "삼십오"), ("2배", "두 배"), ("두 번째 상품군",), ("클릭률",), ("최종 전환율", "몇 배"), ("널리",)],
    "case2": [("셋인데", "과제가 셋"), ("분류가 하나", "분류가"), ("회기가", "회귀가 둘", "회귀"), ("수백 개",), ("엠엘이가", "새로 학습"), ("3배", "세 배"), ("한무", "한 묶음"), ("맞붙여",), ("공유 전문가",), ("상품 종류별 전문가는", "비슷한 상품끼리"), ("처음 보는 상품", "처음 보는")],
    "case2-results": [("세 과제 모두", "크게 앞섰"), ("79", "칠십구"), ("66", "육십육"), ("AUC도", "십 퍼센트"), ("두 모델이 모두", "같은 유저")],
    "seesaw": [("공유층을 거치는", "공유층을"), ("부정적 전이",), ("시소",), ("피엘이를", "간섭을 줄이기"), ("독차지", "손실의 크기"), ("표준화",)],
    "bound": [("데이터가 많은 과제", "덮기도"), ("기울기", "정답 많은"), ("작은 변경도", "모든 과제의 지표"), ("자동 채점", "채점합니다"), ("배포도 묶여", "배포도"), ("편하지만",), ("되돌리기",)],
    "group": [("메타도",), ("수천 개",), ("이십 퍼센트", "인프라"), ("무작정",), ("같은 유저의 행동끼리", "같은 유저의"), ("세 과제끼리", "같은 상품의"), ("평가 기준부터", "평가 기준"), ("일부 과제는", "평균은")],
    "takeaways": [("운영이 가벼워", "가벼워집니다"), ("새 과제와", "효과가 커요"), ("덕을 봅니다", "데이터가 적은"), ("트리 모델에 넣기", "전용 길")],
    "closing": [("모든 문제를",), ("다른 모델을 함께", "다른 모델을"), ("늘고 있다면", "비슷한 목적의"), ("하나로 묶을 수", "하나로 묶을"), ("질문은 계속", "회사가 커지는")],
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
