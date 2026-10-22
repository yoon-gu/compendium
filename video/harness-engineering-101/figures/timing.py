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
# 코드 타이핑 클립: 나레이션의 단어가 들릴 때 어느 줄까지 쳐져 있어야 하는지. (단어 후보, 줄에 들어 있는 글자)
CODE_RULES = {
    "code-l1": [(("빈 리스트", "리스트가"), "messages = json.load"), (("사용자가 치면", "치면"), "input("), (("리스트에 붙이고", "붙이고"), 'messages.append({"role": "user"'),
                (("통째로",), "reply = call_llm"), (("답이 오면", "또 붙"), 'messages.append({"role": "assistant"'), (("파란",), "[array]"), (("파일로 저장", "저장합니다"), "json.dump(messages")],
    "code-l3-tools": [(("도구 목록", "덩어리는"), "TOOLS = ["), (("리드 파일", "read_file"), '"read_file"'), (("런 커맨드", "run_command"), '"run_command"'), (("인자 스키마", "스키마가"), '"input_schema"')],
    "code-l3-dispatch": [(("디스패치",), "def execute_tool"), (("리드 파일이면", "리드 파일", "read_file"), 'name == "read_file"'), (("런 커맨드면", "런 커맨드", "run_command"), 'name == "run_command"'),
                         (("마지막 줄", "예외가"), "except Exception"), (("오류 문자열",), 'return f"ERROR: {e}"')],
    "code-l4-loop": [(("포 루프", "for 루프", "루프 하나"), "for _ in range"), (("모델을 부르고", "부르고"), "reply = call_llm"), (("답을 붙이고",), '"role": "assistant"'),
                     (("툴 유즈가 아니면", "아니면 끝", "tool_use"), "stop_reason"), (("전부 돌리고", "전부"), 'block["type"] == "tool_use"'), (("하나로 붙여서", "붙여서"), '"role": "user", "content": results')],
    "code-l5": [(("예외를 잡아서", "예외를"), "except Exception"), (("빈 문자열",), 'return ""')],
    "code-l6": [(("코드는 이렇게", "고쳤습니다"), "msgs = json.loads"), (("마지막 메시지", "메시지에도"), 'last["content"][-1]["cache_control"]'), (("뒤로 움직", "움직입니다"), '"cache_control": {"type": "ephemeral"}}],')],
    "code-l6-usage": [(("유시지", "usage"), 'u = reply.get("usage"'), (("캐시 리드", "cache_read"), "cache_read=")],
    "code-l6-bust": [(("현재 시각", "시각"), "Current time")],
}
# 터미널 클립: 나레이션의 단어가 들릴 때 기록의 어느 줄이 찍혀 있어야 하는지. (단어 후보, 출력 정규식, n번째 일치)
TERM_RULES = {
    "l1-chat": [(("듣는편람",), r"하니스 공부 중입니다\.", 1), (("물어봅니다", "물어봅"), r"제 이름이 뭐라고 했죠\?", 1),
                (("이천오백팔십구", "이천오백", "2589", "2,589"), r"\[array\] 2 messages, 2589", 1), (("사천삼백육십이", "사천삼백", "4362", "4,362"), r"\[array\] 4 messages, 4362", 1),
                (("클리어", "clear"), r"/clear", 1), (("자기 이름", "자기", "클로드", "Claude"), r"저는 Claude", 1)],
    "l2-session": [(("묻습니다",), r"아는 걸 말해 봐요\.", 1), (("모델의 답", "보면"), r"assistant> 방금", 1)],
    "l3-tools": [(("달라고",), r"내용을 보여 줘\.", 1), (("파인드",), r"\[tool\] run_command", 1), (("멈춥니다", "멈춰"), r"다시 확인하겠습니다\.", 1),
                 (("다음 질문", "질문을"), r"이 폴더에 어떤 파일이 있어\?", 1), (("사백", "400"), r"HTTP Error 400", 1)],
    "l4-agent": [(("고쳐 줘", "실패해"), r"다시 돌려서 확인해\.", 1), (("파일 목록", "목록"), r"\[tool\] run_command", 1), (("리드미",), r"\[tool\] run_command", 2),
                 (("테스트를 돌려", "테스트를", "실패를"), r"\[tool\] run_command", 3), (("내림",), r"assistant> 원인은", 1), (("올림",), r"\[tool\] write_file", 1),
                 (("세 개 통과", "통과", "3개"), r"\[tool\] run_command", 4)],
    "l5-honest": [(("여섯", "6번째", "퍼미션", "Permission"), r"\[tool\] write_file", 1), (("권한을 추가", "거부"), r"읽기 전용이라", 1), (("씨에이치모드", "씨에이치", "chmod", "시모드"), r"chmod u\+w", 1), (("아홉", "9번", "끝냅니다"), r"모두 통과", 1)],
    "l5-silent": [(("일곱", "7번째", "빈 문자열"), r"\[tool\] write_file", 1), (("여전히", "의심", "실패합니다"), r"오류 없이 끝났지만", 1), (("씨에이치모드", "씨에이치", "chmod", "시모드"), r"chmod u\+w", 1),
                  (("다시 씁", "씁니다"), r"\[tool\] write_file", 2), (("열두", "12번", "12"), r"모두 성공", 1)],
    "l6-cache": [(("첫 바퀴", "첫", "0입니다"), r"\[usage\]", 1), (("육백삼십삼", "633"), r"cache_read=633", 1), (("천육십팔", "1068", "1,068"), r"cache_read=1068", 1),
                 (("천칠백육십팔", "1768", "1,768"), r"cache_read=1768", 1), (("이천이백오십사", "2254", "2,254"), r"cache_read=2254", 1)],
    "l6-cachebust": [(("끝까지",), r"\[usage\]", 1), (("육백사십사", "644"), r"cache_write=644", 1), (("천백사십육", "1146", "1,146"), r"cache_write=1146", 1),
                     (("천오백오십오", "1555", "1,555"), r"cache_write=1555", 1), (("이천백오", "2105", "2110", "2,105"), r"cache_write=2105", 1), (("이천육백사십팔", "2648", "2,648"), r"cache_write=2648", 1)],
}


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
    """단어 후보 중 하나가 처음 나오는 시각. 띄어쓰기가 든 후보("리드 파일")도 whisper 단어들을 이어 붙인 글에서 찾는다."""
    joined, spans, pos = "", [], 0
    for w, s in words:
        joined += w + " "; spans.append((pos, pos + len(w), s)); pos += len(w) + 1
    flat = joined.replace(" ", "")
    for k in keys:
        i = joined.find(k)
        if i < 0 and " " in k:
            j = flat.find(k.replace(" ", ""))
            if j >= 0:   # 띄어쓰기 무시하고 맞춘 자리 → 원래 글자 위치로
                cnt, i = 0, 0
                while i < len(joined) and cnt < j:
                    if joined[i] != " ": cnt += 1
                    i += 1
        if i >= 0:
            for a, z, t in spans:
                if a <= i < z or i < a:
                    return t
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
    b.PAD_TO_CLIP = False   # 지난 빌드의 클립 길이에 화면이 맞춰져 클립이 매번 길어지는 되먹임을 끊는다
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
            for name, rules in CODE_RULES.items():
                if any(ln.strip() == f"![](figures/{name}.mp4)" for ln in frame["slide"]):
                    words, pauses, speech_end = frame_words(frame)
                    marks, last = [], 0.0
                    for keys, line in rules:
                        tk = first(words, *keys)
                        if tk is None:
                            print(f"   (못 찾음) {keys[0]!r}"); continue
                        if tk - 0.3 <= last:
                            continue
                        last = round(tk - 0.3, 2); marks.append({"t": last, "line": line})
                    (HERE / f"{name}-timing.json").write_text(json.dumps({"duration": round(dur, 2), "marks": marks}, ensure_ascii=False))
                    print(f"{name}: 화면 {dur:.1f}초, 표시 {[m['t'] for m in marks]} / 규칙 {len(rules)}개 중 {len(marks)}개 잡힘")
            for name, rules in TERM_RULES.items():
                if any(ln.strip() == f"![](figures/term-{name}.mp4)" for ln in frame["slide"]):
                    words, pauses, speech_end = frame_words(frame)
                    marks, last = [], 0.0
                    for keys, pat, nth in rules:
                        t = first(words, *keys)
                        if t is None:
                            print(f"   (못 찾음) {keys[0]!r} — 들린 말: {' '.join(w for w, _ in words)[:120]}…"); continue
                        if t - 0.2 <= last:
                            print(f"   (순서 역전) {keys[0]!r} {t:.1f}s"); continue
                        last = round(t - 0.2, 2); marks.append({"t": last, "pat": pat, "nth": nth})
                    (HERE / f"term-{name}-timing.json").write_text(json.dumps({"duration": round(dur, 2), "marks": marks}, ensure_ascii=False))
                    print(f"term-{name}: 화면 {dur:.1f}초, 표시 {[m['t'] for m in marks]} / 규칙 {len(rules)}개 중 {len(marks)}개 잡힘")


if __name__ == "__main__":
    main()
