#!/usr/bin/env python3
"""터미널 녹화(실제 출력)를 위에 그대로 두고, 아래 코드에서 그 출력을 만든 줄을 밝히는 클립. term-<이름>.mp4 를 쓴다
(terminal.py 와 같은 이름·크기라 build.py/sfx.py/timing.py 는 바뀌지 않는다). 터미널 글자·시각은 terminal.py 의 events/warp 를 재사용.

    python3 trace2.py                 # SPECS 전부
    python3 trace2.py l1-chat l4-agent

코드 줄은 터미널에 찍히는 글자를 보고 정한다(SPECS[*]["rules"]):
  on="prefix"  지금 치는 줄이 정규식과 꼭 맞는 순간(예: "assistant>")
  on="line"    줄이 끝났을 때 정규식이 보이면(예: "you> …")
  seq=[(지연초, 코드 줄 글자|None), …]  차례로 밝힌다. None 은 '발췌 안에 실행 중인 줄 없음'(전부 보통 밝기)
  after=정규식  같은 턴(마지막 you> 이후) 안에 그 글자가 이미 찍혔을 때만 / nth=n  이 규칙이 n번째로 맞을 때만
발췌는 (시작, 끝) 범위 여러 개를 '⋯' 줄로 이어 붙인다 — 긴 로그 화면은 코드를 6-8줄만 두고 터미널을 크게.
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make  # noqa: E402
import terminal as T  # noqa: E402

W, H, FPS = T.W, T.H, T.FPS
TPAD, TLH, TBAR, TCOLS = 28, 50, 48, 88            # 2026-10-28: 화면에서 글자가 작다는 의견 → 30px → 38px
SPLIT, CLH = 520, 44                             # 위 터미널 / 아래 코드 경계, 코드 줄 높이(넘치면 지금 줄을 따라 스크롤)
FT = ImageFont.truetype(str(Path.home() / "Library/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc"), 38, index=0)
FT_B = ImageFont.truetype(str(Path.home() / "Library/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc"), 38, index=1)
FT_T = ImageFont.truetype(str(Path.home() / "Library/Fonts/NanumGothic-Regular.ttf"), 22)
FC = ImageFont.truetype(str(Path.home() / "Library/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc"), 34, index=0)
FC_B = ImageFont.truetype(str(Path.home() / "Library/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc"), 34, index=1)
CODE_BG, CODE_NUM, CUR_BAR, DOTS = "#1B1D21", "#6B6F76", "#8FB4DC", "#4A4F58"
L1, L3, L4, L5, L6, L6B = make.l1, make.l3, make.l4, make.l5, make.l6, make.l6b

# 수업 1·2: 한 턴 = append(user) → call_llm → append(assistant) → print → [array]
CHAT_RULES = [
    dict(on="prefix", pat=r"you> ?", seq=[(0, 'input("')]),
    dict(on="line", pat=r"^you> /clear$", seq=[(0, "messages = []")]),
    dict(on="line", pat=r"^you> (?!/clear$|/quit$).+", seq=[(0, 'append({"role": "user"'), (0.5, "reply = call_llm")]),
    dict(on="prefix", pat=r"assistant>", seq=[(0, 'append({"role": "assistant"'), (0.5, 'print(f"\\nassistant>')]),
    dict(on="prefix", pat=r"\[array\]", seq=[(0, "[array]")]),
]
# 수업 4·5·6 루프: 도구 호출 뒤 결과를 붙이고 다시 부른다
LOOP_RULES = [
    dict(on="line", pat=r"^you> (?!/quit$).+", seq=[(0, "reply = call_llm")]),
    dict(on="prefix", pat=r"assistant>", seq=[(0, '"role": "assistant"'), (0.5, "assistant> {block")]),
    dict(on="prefix", pat=r"\[tool\]", seq=[(0, "[tool]"), (0.7, '"content": results'), (1.4, "reply = call_llm")]),
    dict(on="prefix", pat=r"you> ?", after=r"assistant>", seq=[(0, 'stop_reason')]),
]
# 수업 5 execute_tool 발췌: 어느 분기가 돌았나. write_file 첫 번째는 읽기 전용이라 except 로 간다
TOOL_RULES = [
    dict(on="prefix", pat=r"\[tool\] read_file", seq=[(0, 'name == "read_file"'), (0.4, "open(args")]),
    dict(on="prefix", pat=r"\[tool\] run_command", seq=[(0, 'name == "run_command"'), (0.4, "subprocess.run")]),
    dict(on="prefix", pat=r"\[tool\] write_file", nth=1, seq=[(0, 'name == "write_file"'), (0.4, "f.write"), (1.0, "except Exception"), (1.5, "EXC_RET")]),
    dict(on="prefix", pat=r"\[tool\] write_file", nth=2, seq=[(0, 'name == "write_file"'), (0.4, "f.write"), (1.0, 'return f"wrote')]),
    dict(on="prefix", pat=r"assistant>", seq=[(0, None)]),
    dict(on="prefix", pat=r"you> ?", seq=[(0, None)]),
]
# 수업 6 call_llm 발췌: 사본 → 움직이는 캐시 지점 → 고정 캐시 지점(시스템) → [usage]
CACHE_SEQ = [(0, "msgs = json.loads"), (0.5, 'last["content"][-1]["cache_control"]'), (1.0, '"cache_control": {"type": "ephemeral"}}],')]
CACHE_RULES = [
    dict(on="line", pat=r"^you> (?!/quit$).+", seq=CACHE_SEQ),
    dict(on="prefix", pat=r"\[tool\]", seq=[(0, None)] + [(d + 0.8, s) for d, s in CACHE_SEQ]),
    dict(on="prefix", pat=r"\[usage\]", seq=[(0, 'u = reply.get("usage"'), (0.4, "cache_read=")]),
    dict(on="prefix", pat=r"assistant>", seq=[(0, None)]),
]
BUST_SEQ = [(0, "msgs = json.loads"), (0.5, 'last["content"][-1]["cache_control"]'), (1.0, "Current time"), (1.5, '"cache_control": {"type": "ephemeral"}}],')]
BUST_RULES = [dict(CACHE_RULES[0], seq=BUST_SEQ), dict(CACHE_RULES[1], seq=[(0, None)] + [(d + 0.8, s) for d, s in BUST_SEQ])] + CACHE_RULES[2:]

SPECS = {
    "l1-chat":      dict(file=L1, ranges=[(34, 46)], split=500, rules=CHAT_RULES),
    "l2-session":   dict(file=L1, ranges=[(31, 32), (40, 48)], split=420,
                         rules=[dict(on="line", pat=r"^\$ python3", seq=[(0, "json.load(open(session))")])] + CHAT_RULES[2:4] + [dict(on="prefix", pat=r"\[array\]", seq=[(0, "[array]"), (0.6, "json.dump(messages")])]),
    "l3-tools":     dict(file=L3, ranges=[(65, 66), (68, 75), (77, 78), (82, 82)], split=440, rules=[
        dict(on="line", pat=r"^you> (?!/quit$).+", seq=[(0, "reply = call_llm(messages)")]),
        dict(on="prefix", pat=r"assistant>", seq=[(0, 'print(f"\\nassistant> {block')]),
        dict(on="prefix", pat=r"assistant>", after=r"\[tool\]", seq=[(0, "assistant> {b2")]),
        dict(on="prefix", pat=r"\[tool\]", seq=[(0, "[tool]"), (0.6, "result = execute_tool"), (1.2, '"type": "tool_result"'), (1.8, "reply2 = call_llm")]),
        dict(on="prefix", pat=r"Traceback", seq=[(0, "reply = call_llm(messages)")]),
        dict(on="prefix", pat=r"you> ?", seq=[(0, None)]),
    ]),
    "l4-agent":     dict(file=L4, ranges=[(70, 72), (75, 75), (77, 78), (83, 83), (89, 89)], split=600, rules=LOOP_RULES),
    "l5-honest":    dict(file=L4, ranges=[(51, 51), (53, 54), (55, 58), (59, 60), (64, 65)], split=550, rules=TOOL_RULES, exc_ret='return f"ERROR: {e}"'),
    "l5-silent":    dict(file=L5, ranges=[(51, 51), (53, 54), (55, 58), (59, 60), (64, 65)], split=550, rules=TOOL_RULES, exc_ret='return ""'),
    "l6-cache":     dict(file=L6, ranges=[(41, 41), (45, 45), (47, 48), (58, 60)], split=600, rules=CACHE_RULES),
    "l6-cachebust": dict(file=L6B, ranges=[(17, 17), (41, 41), (45, 45), (47, 48), (58, 60)], split=580, rules=BUST_RULES),
}

# ------------------------------------------------------------------ 2편 (수업 7-10)
LAB = make.LAB / "lessons"
L7B, L7T, L8, L9, L10 = (LAB / f for f in ("l7_budget.py", "l7_truncate.py", "l8_subagents.py", "l9_reminders.py", "l10_background.py"))


def R(path, a, b=None):
    """줄 번호 대신 글자로 고르는 발췌 범위(코드가 바뀌어도 따라간다)."""
    return (make.find_line(path, a), make.find_line(path, b) if b else make.find_line(path, a))


NONE = [(0, None)]
SPECS.update({
    "l7-whole": dict(cols=96, file=L7B, split=560, ranges=[R(L7B, 'if name == "read_file"', 'return open(args["path"]).read()'),
                                                  R(L7B, 'print(f"  [array]', 'if reply is None'),
                                                  R(L7B, 'except urllib.error.HTTPError', 'return None')], rules=[
        dict(on="prefix", pat=r"\[tool\] read_file", seq=[(0, 'name == "read_file"'), (0.4, 'return open(args')]),
        dict(on="prefix", pat=r"\[array\]", seq=[(0, '[array]'), (0.5, 'reply = call_llm')]),
        dict(on="prefix", pat=r"\[harness\] HTTP", seq=[(0, 'except urllib.error.HTTPError'), (0.4, 'print(f"\\n[harness]'), (0.9, 'return None')]),
    ]),
    "l7-truncate": dict(cols=96, file=L7T, split=440, ranges=[R(L7T, 'off, lim =', 'return truncate("".join'),
                                                     R(L7T, 'if len(text) <= MAX', 'keep = MAX'),
                                                     R(L7T, 'os.makedirs', 'return text[:keep] + note'),
                                                     R(L7T, 'return truncate(out.stdout')], rules=[
        dict(on="prefix", pat=r"\[tool\] read_file", seq=[(0, 'off, lim ='), (0.4, 'return truncate("".join'), (0.9, 'if len(text) <= MAX'),
                                                          (1.3, 'os.makedirs'), (1.7, 'note = ('), (2.2, 'return text[:keep] + note')]),
        dict(on="prefix", pat=r"\[tool\] run_command", seq=[(0, 'return truncate(out.stdout')]),
        dict(on="prefix", pat=r"assistant>", seq=NONE),
    ]),
    "l7-silent": dict(cols=96, file=L7T, split=600, ranges=[R(L7T, 'off, lim =', 'return truncate("".join'),
                                                   R(L7T, 'if len(text) <= MAX', 'return text[:keep] + text[-keep:]')], rules=[
        dict(on="prefix", pat=r"\[tool\] read_file", seq=[(0, 'off, lim ='), (0.4, 'return truncate("".join'), (0.9, 'if len(text) <= MAX'),
                                                          (1.3, 'if SILENT'), (1.7, 'return text[:keep] + text[-keep:]')]),
        dict(on="prefix", pat=r"assistant>", seq=NONE),
    ]),
    "l8-noagent": dict(cols=96, file=L8, split=430, ranges=[R(L8, 'reply = call_llm(messages, tools, system, who)'),
                                                   R(L8, 'print(f"\\nassistant>'),
                                                   R(L8, 'tag = "    [sub]"', 'allow_agent),'),
                                                   R(L8, 'messages.append({"role": "user", "content": results})'),
                                                   R(L8, 'print(f"\\n  [array] parent', 'print(f"  [tokens]')], rules=[
        dict(on="line", pat=r"^you> (?!/quit$).+", seq=[(0, 'reply = call_llm')]),
        dict(on="prefix", pat=r"assistant>", seq=[(0, 'print(f"\\nassistant>')]),
        dict(on="prefix", pat=r"\[tool\]", seq=[(0, 'print(f"{tag}'), (0.6, '"content": execute_tool'), (1.2, '"content": results'), (1.8, 'reply = call_llm')]),
        dict(on="prefix", pat=r"\[array\] parent", seq=[(0, '[array] parent')]),
        dict(on="prefix", pat=r"\[tokens\]", seq=[(0, '[tokens]')]),
    ]),
    "l8-agent": dict(cols=96, file=L8, split=460, ranges=[R(L8, 'if name == "agent"', 'return run_subagent'),
                                                 R(L8, 'tag = "    [sub]"', 'print(f"{tag}'),
                                                 R(L8, 'sub_messages = [', 'return final_text or'),
                                                 R(L8, 'print(f"\\n  [array] parent', 'print(f"  [tokens]')], rules=[
        dict(on="prefix", pat=r"\[tool\] agent", seq=[(0, 'print(f"{tag}'), (0.5, 'if name == "agent"'), (1.0, 'return run_subagent'),
                                                      (1.5, 'sub_messages = ['), (2.0, 'final_text = run_loop(sub_messages')]),
        dict(on="prefix", pat=r"\[sub\] (?!d)\w", seq=[(0, 'tag = "    [sub]"')]),
        dict(on="prefix", pat=r"\[sub\] done", seq=[(0, '[sub] done'), (0.6, 'return final_text or')]),
        dict(on="prefix", pat=r"\[tool\] (?!a)\w", seq=[(0, 'print(f"{tag}')]),
        dict(on="prefix", pat=r"assistant>", seq=NONE),
        dict(on="prefix", pat=r"\[array\] parent", seq=[(0, '[array] parent')]),
        dict(on="prefix", pat=r"\[tokens\]", seq=[(0, '[tokens]')]),
    ]),
})
_L9_RANGES = [R(L9, 'READ_STATE[os.path.normpath(args["path"])] = os.stat(args["path"]).st_mtime_ns   # 수업 9\n'.strip(), 'human_edits(os.path'),
              R(L9, 'print(f"  [human]'),
              R(L9, 'def watch_files', 'remind(f"{path} changed'),
              R(L9, '        watch_files()', 'drain_reminders_into(results)')]
_L9_RULES = [
    dict(on="prefix", pat=r"\[tool\] read_file", seq=[(0, 'READ_STATE[os.path.normpath'), (0.4, 'human_edits(os.path')]),
    dict(on="prefix", pat=r"\[human\]", seq=[(0, '[human]')]),
    dict(on="prefix", pat=r"\[tool\] (?!r)\w", seq=NONE),
    dict(on="prefix", pat=r"assistant>", seq=NONE),
]
SPECS.update({
    "l9-noreminder": dict(cols=96, file=L9, split=430, ranges=_L9_RANGES, rules=_L9_RULES + [
        dict(on="prefix", pat=r"\[array\] 5", seq=[(0, '        watch_files()'), (0.5, 'st_mtime_ns != seen'), (1.0, 'if REMIND:')]),
    ]),
    "l9-reminder": dict(cols=96, file=L9, split=430, ranges=_L9_RANGES, rules=_L9_RULES + [
        dict(on="prefix", pat=r"\[reminder\]", seq=[(0, 'st_mtime_ns != seen'), (0.4, '[reminder]'), (0.8, 'remind(f"{path}'), (1.3, 'drain_reminders_into(results)')]),
    ]),
    "l9-todo": dict(cols=96, file=L9, split=520, ranges=[R(L9, 'if name == "todo_write"', 'remind("Your current todo'),
                                                R(L9, 'def drain_reminders_into', 'return blocks'),
                                                R(L9, '        watch_files()', 'drain_reminders_into(results)')], rules=[
        dict(on="prefix", pat=r"\[tool\] todo_write", seq=[(0, 'if name == "todo_write"'), (0.4, 'marks = {'), (0.8, 'print("  [todo]'),
                                                           (1.3, 'remind("Your current'), (1.8, 'drain_reminders_into(results)')]),
        dict(on="prefix", pat=r"\[tool\] (?!t)\w", seq=NONE),
        dict(on="prefix", pat=r"assistant>", seq=NONE),
    ]),
    "l10-background": dict(cols=96, file=L10, split=420, ranges=[R(L10, 'proc = subprocess.Popen', 'stdout=subprocess.PIPE'),
                                                        R(L10, 'code = proc.wait()'),
                                                        R(L10, 'print(f"\\n  [bg]', 'f"Use task_output'),
                                                        R(L10, 'if args.get("background")', 'return start_background'),
                                                        R(L10, 'while not select.select', '                run_turn(messages)')], rules=[
        dict(on="prefix", pat=r"you> ?", seq=[(0, 'while not select.select')]),
        dict(on="prefix", pat=r"\[tool\] run_command", seq=[(0, 'if args.get("background")'), (0.4, 'return start_background')]),
        dict(on="prefix", pat=r"\[bg\] started", seq=[(0, 'proc = subprocess.Popen'), (0.5, 'return start_background')]),
        dict(on="prefix", pat=r"\[bg\] b\d finished", seq=[(0, 'code = proc.wait()'), (0.4, 'print(f"\\n  [bg]'), (0.8, 'remind(f"Background task')]),
        dict(on="prefix", pat=r"\[harness\] notice", seq=[(0, 'if REMINDERS:'), (0.4, 'notice arrived'), (0.8, 'drain_reminders_into([])'), (1.2, 'run_turn(messages)')]),
        dict(on="prefix", pat=r"\[tool\] (?!r)\w", seq=NONE),
        dict(on="prefix", pat=r"assistant>", seq=NONE),
    ]),
})


def code_rows(spec):
    rows = []
    for k, (a, z) in enumerate(spec["ranges"]):
        if k:
            rows.append((None, "⋯", False))
        rows += [r for r in make.code_rows(spec["file"], a, z, cols=spec.get("cols", 80)) if not r[1].strip().startswith("# 수업")]
    return rows


def line_marks(ev, spec, rows):
    """터미널 글자 흐름 → (시각, 코드 줄 index|-1) 표."""
    def row_of(sub):
        if sub is None:
            return -1
        if sub == "EXC_RET":
            sub = spec["exc_ret"]
        return next(i for i, (_, txt, _) in enumerate(rows) if sub in txt)
    marks, buf, turn, fired, counts = [], "", "", set(), {}

    def add(t, seq):
        base = min(max(t, (marks[-1][0] + 0.3) if marks else t), t + 1.5)
        marks.extend((base + d, row_of(x)) for d, x in seq)
    for t, ch in ev:
        if ch == "\n":
            line = buf.strip()
            for i, r in enumerate(spec["rules"]):
                if r["on"] == "line" and re.search(r["pat"], line):
                    add(t, r["seq"])
            if line.startswith("you>"):
                turn = ""
            turn += line + "\n"; buf = ""; fired = set()
            continue
        buf += ch
        s = buf.lstrip()
        for i, r in enumerate(spec["rules"]):
            if r["on"] != "prefix" or i in fired or not re.fullmatch(r["pat"], s):
                continue
            if r.get("after") and not re.search(r["after"], turn):
                continue
            counts[i] = counts.get(i, 0) + 1
            if r.get("nth") and counts[i] != r["nth"]:
                fired.add(i); continue
            fired.add(i)
            add(t, r["seq"])
    return sorted(marks)


def wrap(line, cols):
    out, cur, w = [], "", 0
    for ch in line:
        cw = T.width(ch)
        if w + cw > cols:
            out.append(cur); cur, w = "", 0
        cur += ch; w += cw
    out.append(cur)
    return out


def render(name):
    spec = SPECS[name]
    rows = code_rows(spec)
    split, clh = SPLIT, CLH
    vis = (H - split - 16) // clh                   # 한 번에 보이는 코드 줄 수
    ev, total = T.events(name, 1.0)
    ev, total = T.warp(ev, total, name)
    marks = line_marks(ev, spec, rows)
    assert marks, name
    title = f"lab — {Path(spec['file']).name} — zsh"
    frames = int(total * FPS)
    trows = (split - TBAR - 2 * TPAD) // TLH
    out = HERE / f"term-{name}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
                            stdin=subprocess.PIPE)
    text, k, shots = "", 0, []
    sheet_at = {int(frames * f) for f in (0.15, 0.4, 0.7, 0.97)}
    for i in range(frames):
        t = i / FPS
        while k < len(ev) and ev[k][0] <= t:
            text += ev[k][1]; k += 1
        im = Image.new("RGB", (W, H), "#F4F4F1")
        d = ImageDraw.Draw(im, "RGBA")
        # ---- 위: 터미널(실제 출력 그대로)
        d.rectangle([0, 0, W, split], fill=T.BG)
        d.rectangle([0, 0, W, TBAR], fill="#2A2D33")
        for j, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
            d.ellipse([22 + j * 30, TBAR // 2 - 9, 40 + j * 30, TBAR // 2 + 9], fill=c)
        d.text((W // 2, TBAR // 2), title, fill="#B8BBC2", font=FT_T, anchor="mm")
        lines = [w for ln in text.split("\n") for w in wrap(ln, TCOLS)]
        shown = lines[-trows:]
        top = TBAR + TPAD
        for r, ln in enumerate(shown):
            col, font = T.color_of(ln)
            d.text((TPAD, top + r * TLH), ln, fill=col, font=FT_B if font is T.FONT_B else FT)
        if int(t * 2) % 2 == 0 and shown:
            x = TPAD + sum(T.width(c) for c in shown[-1]) * FT.getlength("a")
            d.rectangle([x + 3, top + (len(shown) - 1) * TLH + 6, x + 21, top + (len(shown) - 1) * TLH + 44], fill=T.FG)
        # ---- 아래: 코드 발췌, 지금 출력을 만든 줄만 밝게
        cur_row = next((ln for mt, ln in reversed(marks) if mt <= t), -1)
        d.rectangle([0, split + 8, W, H], fill=CODE_BG)
        first = min(max(0, cur_row - vis // 2), max(0, len(rows) - vis))   # 지금 줄이 가운데 오게
        ctop = split + 16 + max(0, (H - split - 16 - min(vis, len(rows)) * clh) // 2)
        for r, (no, txt, _) in enumerate(rows):
            if not first <= r < first + vis:
                continue
            y = ctop + (r - first) * clh
            if txt == "⋯":
                d.text((TPAD + 100, y - 4), "⋯", fill=DOTS, font=FC)
                continue
            if r == cur_row:
                d.rectangle([12, y - 2, W - 12, y + clh - 4], fill=(0x8F, 0xB4, 0xDC, 56))
                d.rectangle([12, y - 2, 20, y + clh - 4], fill=CUR_BAR)
            dim = cur_row >= 0 and r != cur_row
            if no is not None:
                d.text((TPAD, y), f"{no:3d}", fill=CODE_NUM if dim else "#E6E6E3", font=FC)
            x0 = x = TPAD + 100
            done = ""
            for tok, col in make.tokens(txt):
                c = tuple(int(int(col[j:j + 2], 16) * 0.45) for j in (1, 3, 5)) if dim else col
                d.text((x, y), tok, fill=c, font=FC_B if r == cur_row else FC)
                done += tok; x = x0 + d.textlength(done, font=FC)
        proc.stdin.write(im.tobytes())
        if i in sheet_at:
            shots.append(im.copy())
    proc.stdin.close(); proc.wait()
    assert proc.returncode == 0
    sheet = Image.new("RGB", (W, H), T.BG)
    for j, s in enumerate(shots[:4]):
        sheet.paste(s.resize((W // 2, H // 2)), ((j % 2) * W // 2, (j // 2) * H // 2))
    sheet.save(HERE / f"term-{name}-sheet.png")
    print(f"{out.name}: {frames} 프레임, {total:.1f}초, 코드 {len(rows)}줄(행간 {clh}), 줄 표시 {len(marks)}번")


if __name__ == "__main__":
    for n in [a for a in sys.argv[1:] if not a.startswith("--")] or list(SPECS):
        render(n)
