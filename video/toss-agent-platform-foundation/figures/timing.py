#!/usr/bin/env python3
"""녹음이 끝난 뒤, 모션 그래픽 화면의 나레이션에서 언급 시각을 whisper 로 잡아 <이름>-timing.json 을 쓴다.

    python3 timing.py --voice=진우 && sh render.sh && (cd ../.. && python3 build.py toss-agent-platform-foundation --voice=진우)

화면 길이는 build.py 의 scene_audio 계산, 단어 시각은 조각 wav 마다 whisper(small, ko). 표시 규칙은 RULES.
(토스 멀티태스크 회차의 timing.py 를 그대로 가져왔다. 컴포지션은 ../../remotion/src/agent/)
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
    "need": [("지난달과 같은 기준", "지난달과"), ("인터넷 환경", "나눠 운영"), ("밖으로 옮길", "옮길 수 없"), ("직접 코드를", "코드를 돌려"), ("전체를 열어", "열어 줄 수는"), ("조심하라고", "프롬프트로"), ("하나 더",)],
    "harness": [("글만",), ("프로세스를 띄우", "띄우거나"), ("부릅니다", "하니스라고"), ("오류가 나면", "오류를"), ("뇌라면", "몸인 셈"), ("자유로울", "너무 자유")],
    "layers": [("두 겹",), ("오픈샌드박스라는", "오픈샌드박스"), ("파드를 하나씩", "사용자마다 파드"), ("버블랩이라는", "버블랩"), ("에이전트마다 따로", "따로 가둡"), ("네임스페이스",)],
    "units": [("워크스페이스예요", "개인 작업 공간"), ("에이전트가", "여럿 있습"), ("세션입니다", "세션"), ("파드를 하나 만들어", "파드를 하나"), ("서버가",), ("러너가",), ("런타임이",), ("인증정보는", "데이터베이스")],
    "vm": [("가상 머신을 따로", "가상 머신을"), ("커널까지",), ("이미지와",), ("좁았",), ("버블랩을 골랐", "골랐습니다"), ("대가가",)],
    "fences": [("3가지", "세 가지"), ("첫째는 파일", "첫째는"), ("다른 에이전트의 폴더", "보이지 않습"), ("읽기 전용",), ("둘째는",), ("프록시로만", "프록시로"), ("셋째는",), ("케이퍼빌리티",), ("실패하면",), ("쓰기를 허락한", "잘못 지우는")],
    "sessions": [("작업 폴더를 따로", "따로 주면"), ("복사해야", "사본이"), ("다르게 다뤘",), ("함께 씁니다", "함께 씁"), ("비교 코드",), ("세션마다 따로", "세션마다"), ("조건을 알려", "알려 줘야"), ("그때 버전",), ("동시에",)],
    "proxy": [("전용 통로",), ("다른 길로", "다른 길"), ("두 단계",), ("이그레스",), ("남은 건 키", "남은 건"), ("환경", "환경변수에"), ("로그의", "로그에"), ("대체값을 헤더", "대체값"), ("바꿔 끼워", "바꿔")],
    "perms": [("숨겼다고",), ("그대로 쓸 수", "그대로"), ("게이트웨이가 봅", "게이트웨이가"), ("엠씨피", "MCP"), ("업무 서비스가 봅", "업무 서비스가"), ("문서 하나를", "문서 하나"), ("내보내는",)],
    "resume": [("언제든 바뀌", "언제든"), ("영속 볼륨",), ("다시 붙여",), ("돌아오지 않아", "메모리는"), ("무엇을 남겨",), ("질문과 답만", "모자랍"), ("어느 결과가", "어느 호출"), ("압축한",)],
    "state": [("처음엔",), ("변환 코드도", "변환 코드"), ("방향을 틀",), ("세션 아이디", "세션 ID"), ("경로만",), ("오류를 냅", "못 찾으면"), ("이어 간다고 해도", "멈춘 곳부터")],
    "records": [("보여 줄 때는", "화면에 보여"), ("저장 형식이 달라", "형식이 달라"), ("공통 형식",), ("오픈리스폰시스", "공개 규격"), ("다시 띄울",), ("넘길 때도",), ("요약해",), ("새 대화를 여는", "새 대화를"), ("사용자가 고르", "고르죠")],
    "takeaways": [("코드까지",), ("대화 상태를 남겼", "남겼습니다"), ("공통 기록으로",)],
    "limits": [("곳곳에",), ("검증하는",), ("권한을 줄이는",), ("되돌아가지",), ("못 막는지까지", "못 막는지")],
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
