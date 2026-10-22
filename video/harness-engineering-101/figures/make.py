#!/usr/bin/env python3
"""하니스 101 핸즈온 회차 화면용 다이어그램을 SVG 로 그린다(책의 구조만 가져와 새로 그림, 가로판 904px 폭).  python3 make.py"""
import json
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD, OK = "#2F5D8A", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B", "#3C7A4A"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 904


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, title, lines=(), accent=False, size=34, color=None, mono=False):
    out = [rect(x, y, w, h, INK if accent else LINE, sw=4 if accent else 3),
           text(x + 26, y + 54, title, size, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 26, y + 106 + i * 50, ln, 28, color or GRAY, mono=mono))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label="", color=INK, lx=None, ly=None, anchor="start", size=25):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text(lx if lx is not None else (x1 + x2) / 2 + 16, ly if ly is not None else (y1 + y2) / 2 + 10, label, size, GRAY, anchor))
    return "\n".join(out)


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def stack(items, gap=52, top=0):
    y, out = top, []
    for i, (t, ls, acc) in enumerate(items):
        h = 84 + 50 * len(ls) + (14 if ls else 0)
        out.append(box(0, y, W, h, t, ls, acc))
        y += h
        if i < len(items) - 1:
            out.append(arrow(W / 2, y + 4, W / 2, y + gap - 4)); y += gap
    return y, "\n".join(out)


figs = {}

# ---------- 수업 하나의 틀 ----------
steps = ["코드 같이 쓰기", "실행해 보기", "방금 일어난 일", "자주 막히는 곳", "체크포인트"]
b = []
for i, s in enumerate(steps):
    x = (i % 3) * 300; y = (i // 3) * 150
    b.append(rect(x, y, 288, 120, INK if i in (0, 1) else LINE, sw=4 if i in (0, 1) else 3))
    b.append(text(x + 24, y + 48, f"{i + 1}", 30, INK, weight="bold"))
    b.append(text(x + 20, y + 92, s, 30, TXT, weight="bold"))
figs["lesson-flow"] = svg(280, "\n".join(b))

# ---------- 준비물 ----------
h, b = stack([("Python 3.10 이상", ["설치할 패키지 없음 — urllib 만 쓴다"], False),
              ("저장소 받기", ["git clone … harness-engineering-101", "src/harness/ 에 v1-v4, harness.py"], False),
              ("API 키", ["export ANTHROPIC_API_KEY=…", "지출 한도를 낮게 걸어 둔다"], True),
              ("모델 한 줄", ["MODEL = \"claude-haiku-5-5\"", "실습은 싼 모델로"], False)])
figs["setup"] = svg(h, b)

# ---------- 도구 계약: JSON 세 조각 ----------
b = [box(0, 0, W, 170, "① 요청에 넣는 메뉴", ['{"name": "read_file", "input_schema": {…}}'], False, mono=True),
     arrow(W / 2, 176, W / 2, 218),
     box(0, 224, W, 170, "② 모델의 답: tool_use 블록", ['{"type": "tool_use", "id": "toolu_01A",', ' "name": "read_file", "input": {"path": "main.py"}}'], True, mono=True),
     arrow(W / 2, 400, W / 2, 442),
     box(0, 448, W, 170, "③ 다음 user 메시지: tool_result 블록", ['{"type": "tool_result", "tool_use_id": "toolu_01A",', ' "content": "import sys…"}'], False, mono=True)]
figs["tool-contract"] = svg(620, "\n".join(b))

# ---------- 매달린 tool_use (400 오류) ----------
rows = [("user", "가장 큰 파일을 읽어 줘", LINE), ("assistant", "tool_use: run_command(find …)", LINE),
        ("user", "tool_result: (빈 결과)", LINE), ("assistant", "tool_use: run_command(ls …)  ← 답을 못 받음", BAD),
        ("user", "이 폴더에 어떤 파일이 있어?  ← 여기서 400", BAD)]
b = []
for i, (role, s, c) in enumerate(rows):
    y = i * 92
    b.append(rect(0, y, W, 78, c, FILL if c == LINE else "#FBEFEF", 4 if c == BAD else 3))
    b.append(text(24, y + 50, role, 28, INK, weight="bold", mono=True))
    b.append(text(200, y + 50, s, 28, BAD if c == BAD else TXT, mono=True))
figs["dangling"] = svg(5 * 92 - 14, "\n".join(b))

# ---------- stop_reason 표 ----------
rows = [("tool_use", "도구를 돌려 달라", "실행 → 결과 붙임 → 다시 호출", True),
        ("end_turn", "다 했다", "루프를 나가 사용자에게", True),
        ("max_tokens", "길이 한도에 잘림", "늘리거나 이어 받기", False),
        ("refusal", "거절", "루프를 나가 메시지 표시", False)]
b = [text(0, 34, "stop_reason", 28, GRAY, weight="bold", mono=True), text(300, 34, "뜻", 28, GRAY, weight="bold"), text(600, 34, "루프가 할 일", 28, GRAY, weight="bold")]
for i, (k, m, a, acc) in enumerate(rows):
    y = 60 + i * 96
    b.append(rect(0, y, W, 84, INK if acc else LINE, sw=4 if acc else 3))
    b.append(text(24, y + 52, k, 30, INK if acc else TXT, weight="bold", mono=True))
    b.append(text(300, y + 52, m, 28, TXT)); b.append(text(600, y + 52, a, 26, GRAY))
figs["stop-reason"] = svg(60 + 4 * 96 - 12, "\n".join(b))

# ---------- 오류 두 경로 (실측) ----------
b = [box(0, 0, 440, 330, "오류를 그대로", ["write_file → ERROR: Permission denied", "→ 바로 chmod, 다시 쓰기", "도구 호출 9번 · 23초"], True),
     box(464, 0, 440, 330, "오류를 삼키면", ["write_file → \"\" (성공처럼 보임)", "→ 테스트 여전히 실패 → 탐정 놀이", "도구 호출 12번 · 18초"], False),
     rect(0, 370, W, 90, INK, SOFT, 3), text(W / 2, 426, "오류 문자열은 모델의 연료다 — 던지지도, 뭉개지도 말 것", 30, INK, "middle", "bold")]
figs["errors"] = svg(470, "\n".join(b))

# ---------- 캐시: 앞부분이 같아야 한다 ----------
segs = [("tools", 150, INK), ("system", 170, INK), ("지난 대화", 360, INK), ("이번 바퀴", 200, GRAY)]
b = [text(0, 34, "배열 (앞 → 뒤)", 28, GRAY, weight="bold")]
x = 0
for name, w, c in segs:
    b.append(rect(x, 60, w - 8, 90, c, "#E7EEF5" if c == INK else SOFT, 3, 8))
    b.append(text(x + (w - 8) / 2, 115, name, 28, c, "middle", "bold"))
    x += w
b.append(text(0, 200, "같은 바이트 = 캐시 적중 (값의 10%)", 28, INK, weight="bold"))
b.append(text(0, 246, "새 바이트 = 제값", 28, GRAY, weight="bold"))
b.append(rect(0, 290, W, 160, BAD, "#FBEFEF", 3))
b.append(text(24, 340, "맨 위에 'Current time: 09:52:17' 한 줄을 넣으면", 28, BAD))
b.append(text(24, 390, "요청마다 첫 바이트부터 달라진다 → 전부 제값 → cache_read=0", 28, BAD))
figs["prefix"] = svg(460, "\n".join(b))

# ---------- 뇌와 몸 (정지판) ----------
b = [box(0, 60, 300, 260, "뇌 = 모델", ["글자를 받아", "글자를 낸다", "그뿐"], False),
     box(604, 60, 300, 260, "몸 = 하니스", ["배열을 짠다", "도구를 돌린다", "결과를 붙인다"], True),
     rect(330, 150, 244, 80, INK, "#E7EEF5", 3, 8), text(452, 200, "JSON 배열", 30, INK, "middle", "bold"),
     arrow(300, 170, 330, 170), arrow(574, 210, 604, 210),
     text(W / 2, 30, "둘 사이를 오가는 것은 배열 하나뿐", 30, GRAY, "middle")]
figs["body-brain"] = svg(340, "\n".join(b))

HERE = Path(__file__).resolve().parent
if __name__ == "__main__":
    for name, s in figs.items():
        (HERE / f"{name}.svg").write_text(s, encoding="utf-8")
        print(name)


# ---------- 코드 화면: 실습 파일에서 줄 범위를 잘라 와 그린다 (수업 N 표시가 있는 줄은 잉크색) ----------
LAB = HERE.parent / "lab"


KW = {"def","if","elif","else","return","try","except","for","in","while","import","from","as","lambda","with","not","and","or",
      "True","False","None","break","continue","pass","is","yield","class","raise"}
C_KW, C_STR, C_CMT, C_NUM, C_FN, C_TXT = "#C792EA", "#C3E88D", "#7C8089", "#F78C6C", "#82AAFF", "#E6E6E3"


def tokens(line):
    """파이썬 한 줄을 (글자, 색) 조각으로 — 주석·문자열·키워드·숫자·함수 이름만 구분하는 단순 규칙."""
    import re as _re
    out, i = [], 0
    pat = _re.compile(r'(#.*$)|("""|\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_]\w*\b)')
    for m in pat.finditer(line):
        if m.start() > i:
            out.append((line[i:m.start()], C_TXT))
        g = m.group(0)
        if m.group(1): col = C_CMT
        elif m.group(2): col = C_STR
        elif m.group(3): col = C_NUM
        else:
            prev = line[:m.start()].rstrip()
            col = C_KW if g in KW else (C_FN if prev.endswith("def") or line[m.end():m.end() + 1] == "(" else C_TXT)
        out.append((g, col)); i = m.end()
    if i < len(line):
        out.append((line[i:], C_TXT))
    return out


def code_rows(path, start, end, hl_substr=("# 수업", "# NEW"), cols=72):
    """(줄 번호|None, 글자, 수업 표시 여부) 목록. 긴 줄은 접고 뒤 주석은 아래 줄로. SVG 와 타이핑 클립이 같이 쓴다."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()[start - 1:end]
    rows = []
    for i, ln in enumerate(lines):
        ln = ln.rstrip().replace("\t", "    ")
        hl = any(h in ln for h in hl_substr)
        indent = len(ln) - len(ln.lstrip())
        # 긴 줄: 뒤에 붙은 주석(#…)은 코드 줄 아래 같은 들여쓰기로 내리고, 코드가 그래도 길면 띄어쓰기 자리에서 접는다
        code_part, cmt = ln, ""
        if len(ln) > cols and "#" in ln and not ln.lstrip().startswith("#"):
            k = ln.rfind("  #")
            if k > 0:
                code_part, cmt = ln[:k].rstrip(), ln[k:].strip()
        segs, cur = [], code_part
        while len(cur) > cols:
            cut = cur.rfind(" ", indent + 8, cols)
            if cut <= indent:
                cut = cols
            segs.append(cur[:cut].rstrip()); cur = " " * (indent + 8) + cur[cut:].lstrip()
        segs.append(cur)
        if cmt:
            segs.append(" " * indent + cmt)
        for j, seg in enumerate(segs):
            rows.append((start + i if j == 0 else None, seg, hl))
    return rows


def code(path, start, end, hl_substr=("# 수업", "# NEW"), size=22, lh=32, cols=72):
    """줄 번호 + 구문 강조 코드 SVG."""
    rows = code_rows(path, start, end, hl_substr, cols)
    body = [rect(0, 0, W, lh * len(rows) + 36, LINE, "#1B1D21", 0, 12)]
    for r, (no, txt, hl) in enumerate(rows):
        y = 50 + r * lh
        if hl:
            body.append(f'<rect x="8" y="{y - 24}" width="{W - 16}" height="{lh}" rx="4" fill="#2F5D8A" fill-opacity="0.35"/>')
        if no is not None:
            body.append(text(18, y, f"{no:3d}", 20, "#6B6F76", mono=True))
        spans = "".join(f'<tspan fill="{c}">{escape(t, quote=False)}</tspan>' for t, c in tokens(txt))
        body.append(f'<text x="76" y="{y}" font-size="{size}" {MONO} xml:space="preserve">{spans}</text>')
    return svg(lh * len(rows) + 36, "\n".join(body))


def find_line(path, needle):
    for i, ln in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if needle in ln:
            return i
    raise KeyError(needle)


l1 = LAB / "lessons/l1_chat.py"; l3 = LAB / "lessons/l3_tools.py"; l4 = LAB / "lessons/l4_agent.py"
l5 = LAB / "lessons/l5_agent_silent.py"; l6 = LAB / "lessons/l6_agent_cache.py"; l6b = LAB / "lessons/l6_agent_cachebust.py"
CODE_SPECS = {   # 이름: (파일, 시작 줄, 끝 줄) — SVG(make.py)와 타이핑 클립(codeanim.py)이 같은 범위를 쓴다
    "code-l1": (l1, find_line(l1, "def main"), find_line(l1, "json.dump(messages")),
    "code-l3-tools": (l3, find_line(l3, "TOOLS = ["), find_line(l3, "TOOLS = [") + 11),
    "code-l3-dispatch": (l3, find_line(l3, "def execute_tool"), find_line(l3, 'return f"ERROR: {e}"')),
    "code-l4-loop": (l4, find_line(l4, "for _ in range(MAX_ROUNDS)"), find_line(l4, 'messages.append({"role": "user", "content": results})')),
    "code-l5": (l5, find_line(l5, "def execute_tool"), find_line(l5, "# 수업 5")),
    "code-l6": (l6, find_line(l6, "msgs = json.loads"), find_line(l6, '"messages": msgs, "tools": TOOLS}')),
    "code-l6-usage": (l6, find_line(l6, "u = reply.get"), find_line(l6, "return reply")),
    "code-l6-bust": (l6b, find_line(l6b, "SYSTEM_TEXT"), find_line(l6b, "SYSTEM_TEXT")),
}
for name, (path, a, z) in CODE_SPECS.items():
    figs[name] = code(path, a, z)
sj = LAB / "runs/l1-session-edited.json"
# 수업 1 앞: 실제 요청·응답 한 쌍(하이쿠). 응답은 핵심 키만 추려 짧게
_req = json.load(open(LAB / "runs/l1-request.json", encoding="utf-8")); _res = json.load(open(LAB / "runs/l1-response.json", encoding="utf-8"))
_txt = next(b["text"] for b in _res["content"] if b.get("type") == "text")
_res_short = {"role": _res["role"], "content": [{"type": "text", "text": _txt[:26] + "…"}],
              "stop_reason": _res["stop_reason"], "usage": {k: _res["usage"][k] for k in ("input_tokens", "output_tokens")}}
_pair = LAB / "runs/l1-request-response.txt"
_pair.write_text("# 요청 (POST /v1/messages)\n" + json.dumps(_req, ensure_ascii=False, indent=2) + "\n\n# 응답\n" + json.dumps(_res_short, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
figs["request-response"] = code(_pair, 1, len(_pair.read_text(encoding="utf-8").splitlines()), hl_substr=('"role"', '"stop_reason"', '"usage"'), cols=60)
figs["session-json"] = code(sj, 1, len(sj.read_text(encoding="utf-8").splitlines()), hl_substr=("홍길동",), cols=60)
if __name__ == "__main__":
    for name in list(CODE_SPECS) + ["session-json", "request-response"]:
        (HERE / f"{name}.svg").write_text(figs[name], encoding="utf-8")
        print(name)
