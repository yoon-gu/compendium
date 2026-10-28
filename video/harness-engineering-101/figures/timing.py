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
sys.argv = ["build.py", SLUG, "--wide"] + [a for a in sys.argv[1:] if a.startswith(("--voice=", "--script="))]
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", HERE.parent.parent / "build.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

ANIMS = ["array-grow", "loop", "cache", "errors", "pile", "subagent", "events"]
# 코드 타이핑 클립: 나레이션의 단어가 들릴 때 어느 줄까지 쳐져 있어야 하는지. (단어 후보, 줄에 들어 있는 글자)
CODE_RULES = {
    "code-l1": [(("빈 리스트", "리스트가"), "messages = json.load"), (("사용자가 치면", "치면"), "input("), (("리스트에 붙이고", "붙이고"), 'messages.append({"role": "user"'),
                (("통째로",), "reply = call_llm"), (("답이 오면", "또 붙"), 'messages.append({"role": "assistant"'), (("파란",), "[array]"), (("파일로 저장", "저장합니다"), "json.dump(messages")],
    "code-l3-tools": [(("도구 목록", "덩어리는"), "TOOLS = ["), (("리드 파일", "read_file"), '"read_file"'), (("런 커맨드", "run_command"), '"run_command"'), (("인자 스키마", "스키마가"), '"input_schema"')],
    "code-l3-dispatch": [(("디스패치", "디스페치"), "def execute_tool"), (("리드 파일이면", "리드 파일", "read_file"), 'name == "read_file"'), (("런 커맨드면", "런 커맨드", "run_command"), 'name == "run_command"'),
                         (("마지막 줄", "예외가"), "except Exception"), (("오류 문자열",), 'return f"ERROR: {e}"')],
    "code-l4-loop": [(("포 루프", "포로프", "for 루프"), "for _ in range"), (("먼저 모델을", "모델을 부르고"), "reply = call_llm"),
                     (("돌아온 답", "답을 배열에"), '"role": "assistant"'), (("멈춤 이유를 봅니다", "툴 유즈가 아니면"), "stop_reason"),
                     (("빠짐없이", "하나도"), 'block["type"] == "tool_use"'), (("하나로 묶어", "묶어"), '"role": "user", "content": results')],
    "code-l5": [(("예외를 잡아서", "예외를"), "except Exception"), (("빈 문자열", "빗문자열", "빈문자열", "돌려주게"), 'return ""')],
    "code-l6": [(("코드는 이렇게", "고쳤습니다"), "msgs = json.loads"), (("마지막 메시지", "메시지에도"), 'last["content"][-1]["cache_control"]'), (("뒤로 움직", "움직입니다", "옮겨갑니다", "옮겨"), '"cache_control": {"type": "ephemeral"}}],')],
    "code-l6-usage": [(("유시지", "usage"), 'u = reply.get("usage"'), (("캐시 리드", "cache_read"), "cache_read=")],
    "code-l6-bust": [(("현재 시각", "시각"), "Current time")],
    "code-l7-truncate": [(("이만 자",), "MAX_RESULT_CHARS = 20_000"), (("트렁케이트",), "def truncate"), (("머리 만 자", "꼬리"), "keep = MAX_RESULT_CHARS"),
                         (("저장", "파일로"), 'with open(path, "w")'), (("경로를", "통째로 읽지"), "note = ("), (("오프셋", "리밋"), "off, lim =")],
    "code-l8-agent": [(("에이전트라는 도구", "도구를 하나"), "AGENT_TOOL = {"), (("배경을 다", "근거로"), "include all necessary background"),
                      (("손자",), "SUB_TOOLS = BASE_TOOLS"), (("디스패치 표",), 'if name == "agent"'), (("런 서브에이전트",), "def run_subagent"),
                      (("새 배열",), "sub_messages = ["), (("마지막 글만",), "return final_text or")],
    "code-l9-queue": [(("리마인더스", "Us라는", "빈 리스트"), "REMINDERS = []"), (("리마인드 함수", "함수로", "알릴게"), "def remind"), (("드레인",), "while REMINDERS"),
                      (("파일 감시", "수정 시각"), "def watch_files"), (("달라졌으면", "다시 읽으라고"), 'remind(f"{path} changed'), (("바퀴가 끝나", "도구 결과를 붙일"), "        watch_files()")],
    "code-l10-bg": [(("백그라운드 플래그",), "def start_background"), (("띄워 놓고", "비 원"), "proc = subprocess.Popen"), (("스레드", "쓰레드", "출력을 모으", "뒤에서는"), "def pump"),
                    (("리마인드를",), 'remind(f"Background task'), (("태스크 아웃풋", "태스크아웃풋", "들여다볼", "아웃풋"), 'return f"started background'), (("슬립",), 'if args.get("background")'),
                    (("입력을 기다리는",), "while not select.select"), (("몸이 먼저",), "                run_turn(messages)")],
}
# 터미널 클립: 나레이션의 단어가 들릴 때 기록의 어느 줄이 찍혀 있어야 하는지. (단어 후보, 출력 정규식, n번째 일치)
TERM_RULES = {
    "l1-chat": [(("듣는편람", "듣는 편남", "편남", "이름을 듣는"), r"하니스 공부 중입니다\.", 1), (("물어봅니다", "물어봅"), r"제 이름이 뭐라고 했죠\?", 1),
                (("이천오백팔십구", "이천오백", "2589", "2,589"), r"\[array\] 2 messages, 2589", 1), (("사천삼백육십이", "사천삼백", "4362", "4,362"), r"\[array\] 4 messages, 4362", 1),
                (("클리어", "clear"), r"/clear", 1), (("자기 이름", "자기", "클로드", "Claude"), r"저는 Claude", 1)],
    "l2-session": [(("묻습니다", "못 씁니다", "띄워서"), r"아는 걸 말해 봐요\.", 1), (("모델의 답", "보면"), r"assistant> 방금", 1)],
    "l3-tools": [(("달라고",), r"내용을 보여 줘\.", 1), (("파인드",), r"\[tool\] run_command", 1), (("멈춥니다", "멈춰"), r"다시 확인하겠습니다\.", 1),
                 (("다음 질문", "질문을"), r"이 폴더에 어떤 파일이 있어\?", 1), (("사백", "400", "405", "이번에는"), r"HTTP Error 400", 1)],
    "l4-agent": [(("고쳐 줘", "한 문장"), r"다시 돌려서 확인해\.", 1), (("파일 목록", "목록을"), r"\[tool\] run_command", 1), (("한 번에 읽", "리드미와"), r"\[tool\] run_command", 2),
                 (("그 방식으로", "직접 확인"), r"\[tool\] run_command", 3), (("진단이", "내림", "내립"), r"assistant> 원인은", 1), (("라이트 파일", "고친 코드"), r"\[tool\] write_file", 1),
                 (("다시 돌려", "세 개가 모두", "오케이인"), r"\[tool\] run_command", 4)],
    "l5-honest": [(("여섯", "6번째", "퍼미션", "Permission"), r"\[tool\] write_file", 1), (("권한을 추가", "거부"), r"읽기 전용이라", 1), (("씨에이치모드", "씨에이치", "chmod", "시모드", "CH 모드", "CH"), r"chmod u\+w", 1), (("아홉", "9번", "끝냅니다"), r"모두 통과", 1)],
    "l5-silent": [(("일곱", "7번째", "빈 문자열"), r"\[tool\] write_file", 1), (("여전히", "의심", "실패합니다"), r"오류 없이 끝났지만", 1), (("씨에이치모드", "씨에이치", "chmod", "시모드", "CH 모드", "CH"), r"chmod u\+w", 1),
                  (("다시 씁", "씁니다"), r"\[tool\] write_file", 2), (("열두", "12번", "12"), r"모두 성공", 1)],
    "l6-cache": [(("첫 바퀴", "첫", "0입니다"), r"\[usage\]", 1), (("육백삼십삼", "633"), r"cache_read=633", 1), (("천육십팔", "1068", "1,068"), r"cache_read=1068", 1),
                 (("천칠백육십팔", "1768", "1,768", "넷째"), r"cache_read=1768", 1), (("이천이백오십사", "2254", "2,254"), r"cache_read=2254", 1)],
    "l7-whole": [(("통째로 읽고", "읽고 왜"), r"\[tool\] read_file", 1), (("이백삼십삼만",), r"2,331,535 bytes", 1), (("거절", "사백"), r"HTTP 400", 1)],
    "l7-truncate": [(("이만 바이트",), r"20,873 bytes", 1), (("잘렸다", "잘렸"), r"assistant> 로그가", 1), (("그렙으로", "저장 파일에서"), r"\[tool\] run_command", 1),
                    (("원인을 찾아", "페이저 유틸즈"), r"assistant> 빌드가", 1)],
    "l7-silent": [(("머리와 꼬리는",), r"\[tool\] read_file", 1), (("특정할 수 없다", "결론"), r"assistant> 로그만으로는", 1)],
    "l8-noagent": [(("그렙으로 후보", "직접"), r"\[tool\] run_command", 1), (("잘리기도", "길어"), r"assistant> 출력이 길어서", 1),
                   (("오만 칠천",), r"\[array\] parent", 1)],
    "l8-agent": [(("한 번 부르", "부르자", "에이전트 도구를"), r"\[tool\] agent", 1), (("섭쥬들", "섭 줄", "지나갑니다"), r"\[sub\] run_command", 2),
                 (("14만", "십사만", "끝날 때"), r"\[sub\] done", 1), (("부모배열은", "삼만 팔천", "38"), r"\[array\] parent", 1)],
    "l9-noreminder": [(("휴먼 줄", "그 순간"), r"\[human\]", 1), (("통째로 다시",), r"\[tool\] write_file", 1), (("둘뿐", "둘 뿐", "찍어 보면", "목록을 찍"), r"13:def get_page", 1)],
    "l9-reminder": [(("함수를 더합니다", "더합니다"), r"\[human\]", 1), (("리마인더 줄", "바뀌었다"), r"\[reminder\]", 1),
                    (("다시 읽은",), r"\[tool\] read_file", 2), (("셋이 있습니다", "셋"), r"19:def page_range", 1)],
    "l9-todo": [(("목록을 쓰면",), r"\[todo\]", 1), (("체크 상자", "체크상자", "하나씩", "채워"), r"\[todo\]", 2), (("여기까지 확인",), r"\[todo\]", 3)],
    "l10-background": [(("파이썬이라는", "곧바로 실패"), r"b1 finished", 1), (("파이썬 쓰리로", "파이선 쓰리로", "쓰리로", "다시 띄웁니다", "바꿔"), r"\[bg\] started b2", 1),
                       (("차례를 끝냅니다", "구 초"), r"assistant> README 오타 수정은", 1), (("삼십육 초", "스스로"), r"\[harness\] notice", 1),
                       (("실패했다고",), r"assistant> 느린 테스트가", 1)],
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
                wav = b.voice(text, b.is_slow(frame))
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
    if name == "pile":         # 바퀴 다섯을 '바퀴'부터 말 끝까지 고르게
        t0 = first(words, "바퀴") or 1.0
        return spread(max(0.5, t0 - 0.3), speech_end - 1.0, 5)
    if name == "subagent":     # 부모가 부름 → 자식 배열 → 보고 → 버림 → 부모 계속
        ta = first(words, "문자열로", "건네면") or speech_end * 0.35
        tb = first(words, "빈 배열", "똑같이") or ta + 2.0
        tc = first(words, "마지막 답", "돌아오고") or tb + 3.0
        td = first(words, "버려집니다", "버려") or tc + 2.0
        te = first(words, "깨끗하게") or td + 2.0
        out = [round(max(0.4, ta - 0.3), 2)]
        for v in (tb, tc, td, te):
            out.append(round(max(v - 0.3, out[-1] + 0.6), 2))
        return out
    if name == "events":       # 사건 넷 → 지킬 것
        keys = [("엔터",), ("작업이 끝났을", "작업이"), ("파일이 바뀌었을", "파일이"), ("시각이", "알람")]
        out = []
        for k in keys:
            v = first(words, *k)
            v = v - 0.3 if v else (out[-1] + 2.0 if out else 0.8)
            out.append(round(max(v, out[-1] + 0.6) if out else max(v, 0.4), 2))
        tr = first(words, "돈이", "지킬") or speech_end * 0.8
        out.append(round(max(tr - 0.3, out[-1] + 0.6), 2))
        return out
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
