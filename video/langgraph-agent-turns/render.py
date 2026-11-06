#!/usr/bin/env python3
"""trace.json(실제 실행 기록) + agent.py → 4:3(8:6) 모션 그래픽(1440x1080, 25fps).

왼쪽: 지금 실행 중인 agent.py 줄을 밝힌다. 오른쪽: 그래프에서 켜진 노드와 state["messages"]가 한 턴씩 쌓이는 모습.
    python3 render.py            → out/langgraph-turns.mp4 + out/sheet.png(장면별 마지막 프레임)
    python3 render.py --sheet    → 시트만(빠른 확인)
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments.lexers import PythonLexer
from pygments.token import Token

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
W, H, FPS = 1440, 1080, 25
F = Path.home() / "Library/Fonts"
CODE = ImageFont.truetype(str(F / "D2Coding-Ver1.3.2-20180524-all.ttc"), 18)
def kr(size, w="Regular"): return ImageFont.truetype(str(F / f"NanumGothic-{w}.ttf"), size)
TITLE, SUB, BODY, SMALL, TINY = kr(40, "ExtraBold"), kr(28, "Bold"), kr(24), kr(21), kr(18)
MONO_S = ImageFont.truetype(str(F / "D2Coding-Ver1.3.2-20180524-all.ttc"), 17)

# 차분한 숲 팔레트
PAPER, INK, TXT, GRAY, LINE, SOFT = "#F4F4F1", "#3F7A66", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF"
OK, OK_BG, WARN, WARN_BG, BAD = "#4E8F76", "#EAF3EE", "#C9963A", "#F8F0E0", "#C0605A"
CBG, CNUM = "#1B1D21", "#6B6F76"
SYN = {Token.Keyword: "#8FC4AE", Token.Name.Builtin: "#8FC4AE", Token.Literal.String: "#D9BE8C",
       Token.Literal.Number: "#E0A082", Token.Name.Function: "#9CC4E4", Token.Name.Class: "#9CC4E4",
       Token.Name.Decorator: "#C9963A", Token.Comment: "#6B6F76", Token.Operator: "#B0B0AA"}
DEF = "#D8D8D2"

SRC = (HERE / "agent.py").read_text().splitlines()
TRACE = json.loads((HERE / "trace.json").read_text())
UPD = [e for e in TRACE if e["kind"] == "update"]


def color(tok):
    while tok not in SYN and tok.parent is not None:
        tok = tok.parent
    return SYN.get(tok, DEF)


ROWS = []
for line in SRC:
    ROWS.append([(color(t), s) for t, s in PythonLexer().get_tokens(line) if s != "\n"])


def lines_of(fn):
    """trace 에서 그 함수가 실제로 지나간 줄 번호(순서대로)."""
    return [e["line"] for e in TRACE if e["kind"] == "line" and e["fn"] == fn]


def latency(n):
    """n번째 agent 호출에서 36행(llm.invoke) 시작 → 37행까지 걸린 실측 시간."""
    starts = [e["t"] for e in TRACE if e["kind"] == "line" and e["fn"] == "agent" and e["line"] == 36]
    ends = [e["t"] for e in TRACE if e["kind"] == "line" and e["fn"] == "agent" and e["line"] == 37]
    return ends[n] - starts[n]


def short(m):
    if m["type"] == "human":
        return "user", m["content"]
    if m["type"] == "ai" and m.get("tool_calls"):
        return "ai", "  ".join(f'{c["name"]}({", ".join(f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in c["args"].items())})'
                               for c in m["tool_calls"])
    if m["type"] == "ai":
        return "ai", m["content"].splitlines()[0]
    body = m["content"].replace("\n", " ")
    if m["name"] == "load_skill":
        body = "SKILL.md 본문: " + body.split("---")[-1].strip()
    return "tool", f'{m["name"]} → {body}'


MSGS = [("user", "다음 주 서울 여행 메모 써 줘")] + [short(m) for u in UPD for m in u["messages"]]
ROLE = {"user": (GRAY, SOFT), "ai": (INK, OK_BG)}
L1, L2, L3 = latency(0), latency(1), latency(2)

# 장면: 왼쪽에서 밝힐 줄(seq, 순서대로 지나감), 오른쪽 상태(그래프에 보이는 것, 켜진 노드, 메시지 수 등)
B = [
    dict(t=4.0, title="LangGraph 에이전트, 한 턴씩 따라가기", cap="왼쪽은 실제로 돌린 agent.py, 오른쪽은 그 순간 그래프와 state[\"messages\"]", seq=[], intro=True),
    dict(t=4.5, title="등록 1/5 · 스킬", cap="스킬 폴더를 훑어 이름만 사전에 담는다. 본문은 아직 읽지 않는다", seq=[10], reg={"skill"}),
    dict(t=6.0, title="등록 2/5 · 도구 셋", cap="@tool 데코레이터가 함수를 도구로 등록한다. 독스트링이 도구 설명이 된다", seq=[12, 13, 17, 18, 22, 23], reg={"skill", "tools"}),
    dict(t=6.0, title="등록 3/5 · 모델에 도구를 묶고, 스킬은 이름·설명만", cap="bind_tools: 도구 3개의 스키마가 매 호출에 실린다. 스킬은 시스템 프롬프트에 한 줄", seq=[27, 28, 29, 30], reg={"skill", "tools", "llm"}),
    dict(t=5.5, title="등록 4/5 · 상태와 노드 함수", cap="messages 는 add_messages 리듀서로 덮어쓰지 않고 이어 붙는다", seq=[32, 33, 35, 39], reg={"skill", "tools", "llm"}),
    dict(t=7.0, title="등록 5/5 · 그래프 배선", cap="START → agent → (route) → tools → agent … tool_calls 가 없으면 END", seq=[43, 44, 45, 46, 47, 48, 49], reg={"skill", "tools", "llm"}, graph=True),
    dict(t=5.0, title="실행 시작: invoke", cap="사용자 메시지 하나가 state[\"messages\"]의 첫 칸이 된다", seq=[52], graph=True, msgs=1, active="START", edge=("START", "agent")),
    dict(t=7.0, title="턴 1 · agent 노드", cap=f"LLM 입력: 시스템 + 메시지 1개 + 도구 스키마 3개 → 도구 두 개를 한꺼번에 요청 (실측 {L1:.2f}초)", seq=lines_of("agent")[0:2] + lines_of("route")[0:2], graph=True, msgs=2, active="agent", edge=("agent", "tools"), route="tools"),
    dict(t=7.0, title="턴 1 · tools 노드", cap="ToolNode 가 tool_calls 2개를 실행. 이제야 스킬 본문이 컨텍스트에 들어온다", seq=[15, 20], graph=True, msgs=4, active="tools", edge=("tools", "agent"), skill_loaded=True),
    dict(t=6.5, title="턴 2 · agent 노드", cap=f"LLM 입력: 메시지 4개. 스킬 규칙 '화씨는 c_to_f로'를 따른다 (실측 {L2:.2f}초)", seq=lines_of("agent")[2:4] + lines_of("route")[2:4], graph=True, msgs=5, active="agent", edge=("agent", "tools"), route="tools", skill_loaded=True),
    dict(t=5.5, title="턴 2 · tools 노드", cap="c_to_f(18) → 64.4. 계산은 모델이 아니라 파이썬이 한다", seq=[25], graph=True, msgs=6, active="tools", edge=("tools", "agent"), skill_loaded=True),
    dict(t=7.5, title="턴 3 · agent 노드 → END", cap=f"LLM 입력: 메시지 6개 → tool_calls 없음 → route 가 END 를 고른다 (실측 {L3:.2f}초)", seq=lines_of("agent")[4:6] + lines_of("route")[4:6], graph=True, msgs=7, active="agent", edge=("agent", "END"), route="END", skill_loaded=True),
    dict(t=8.0, title="최종 답", cap="out[\"messages\"][-1].content", seq=[53], graph=True, msgs=7, active="END", skill_loaded=True, final=True),
    dict(t=8.0, title="정리", cap="등록은 한 번, 실행은 턴마다 agent ⇄ tools", seq=[], summary=True),
]


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def text(d, xy, s, font, fill, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def sized(s, w, size, width):
    """한 줄에 들어가도록 글자 크기를 줄인다."""
    while size > 16 and kr(size, w).getlength(s) > width:
        size -= 1
    return kr(size, w)


def fit(s, font, width):
    if font.getlength(s) <= width:
        return s
    while s and font.getlength(s + "…") > width:
        s = s[:-1]
    return s + "…"


# ---------- 왼쪽: 코드 ----------
CX, CY, CW, CH = 24, 120, 818, 860
LH, VIS = 28, 29


def top_for(seq):
    if not seq:
        return 1
    mid = (min(seq) + max(seq)) / 2
    return max(1, min(len(SRC) - VIS + 1, round(mid - VIS / 2)))


def draw_code(im, b, u, top):
    full = im
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([CX, CY, CX + CW, CY + CH], 18, fill=CBG)
    text(d, (CX + 24, CY + 14), "agent.py", SMALL, "#9A9A94")
    y0 = CY + 50
    seq = b["seq"]
    k = min(len(seq) - 1, int(u * len(seq) * 1.15)) if seq else -1   # 지금 실행 중인 줄의 위치
    done = set(seq[:k])
    cur = seq[k] if seq else None
    first = int(top)
    for i in range(first - 1, min(len(SRC), first + VIS)):
        n = i + 1
        y = y0 + (n - top) * LH
        if y < y0 - 4 or y > CY + CH - LH:
            continue
        if n == cur:
            d.rectangle([CX + 8, y - 3, CX + CW - 8, y + LH - 5], fill=(63, 122, 102, 150))
            d.rectangle([CX + 8, y - 3, CX + 14, y + LH - 5], fill="#8FC4AE")
        elif n in done:
            d.rectangle([CX + 8, y - 3, CX + CW - 8, y + LH - 5], fill=(63, 122, 102, 55))
        text(d, (CX + 48, y), str(n), CODE, CNUM, "ra")
        x = CX + 64
        for c, s in ROWS[i]:
            d.text((x, y), s, font=CODE, fill=c)
            x += CODE.getlength(s)
    full.paste(im.crop((CX, CY, CX + CW, CY + CH)), (CX, CY))


# ---------- 오른쪽: 그래프 + 메시지 ----------
RX, RW = 862, 554
NODES = {"START": (RX + 70, 250), "agent": (RX + 280, 250), "tools": (RX + 280, 390), "END": (RX + 490, 250)}


def box(d, name, on, glow):
    x, y = NODES[name]
    small = name in ("START", "END")
    w, h = (100, 50) if small else (160, 64)
    fill, edge, fg = (INK, INK, "white") if on else ("white", LINE if small else INK, TXT)
    if glow:
        for r in range(4, 0, -1):
            d.rounded_rectangle([x - w / 2 - r * 5 * glow, y - h / 2 - r * 5 * glow, x + w / 2 + r * 5 * glow, y + h / 2 + r * 5 * glow],
                                40, fill=(63, 122, 102, int(22 * glow)))
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 35 if small else 16, fill=fill, outline=edge, width=3)
    text(d, (x, y), name, SUB if not small else SMALL, fg, "mm")


def arrow(d, a, b, col, width=3, dash=False):
    import math
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    if dash:
        s = 0
        while s < L - 14:
            e = min(s + 14, L - 14)
            d.line([x1 + ux * s, y1 + uy * s, x1 + ux * e, y1 + uy * e], fill=col, width=width)
            s += 24
    else:
        d.line([x1, y1, x2 - ux * 12, y2 - uy * 12], fill=col, width=width)
    px, py = -uy, ux
    d.polygon([(x2, y2), (x2 - ux * 18 + px * 9, y2 - uy * 18 + py * 9), (x2 - ux * 18 - px * 9, y2 - uy * 18 - py * 9)], fill=col)


EDGES = {("START", "agent"): ((RX + 120, 250), (RX + 200, 250)), ("agent", "END"): ((RX + 360, 250), (RX + 440, 250)),
         ("agent", "tools"): ((RX + 250, 282), (RX + 250, 358)), ("tools", "agent"): ((RX + 310, 358), (RX + 310, 282))}


def draw_graph(d, b, u):
    d.rounded_rectangle([RX, CY, RX + RW, CY + 350], 18, fill="white", outline=SOFT, width=2)
    text(d, (RX + 24, CY + 14), "graph (StateGraph)", SMALL, GRAY)
    reveal = ease(u * 1.3) if b.get("title", "").startswith("등록 5/5 ·") else 1.0
    for (a, c), (p, q) in EDGES.items():
        hot = b.get("edge") == (a, c)
        dash = (a, c) in (("agent", "tools"), ("agent", "END"))
        arrow(d, p, q, INK if hot else LINE, 4 if hot else 3, dash and not hot)
    text(d, (RX + 242, 320), "route()", TINY, WARN, "rm")
    for name in NODES:
        on = b.get("active") == name
        box(d, name, on, (0.5 + 0.5 * abs(((u * 2) % 2) - 1)) if on else 0)
    if b.get("edge"):   # 간선을 따라가는 점
        p, q = EDGES[b["edge"]]
        v = ease((u - 0.55) / 0.4)
        if 0 < v < 1:
            x, y = p[0] + (q[0] - p[0]) * v, p[1] + (q[1] - p[1]) * v
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=WARN)
    if b.get("route") and u > 0.5:
        lab = f'route → "{b["route"]}"'
        d.rounded_rectangle([RX + 370, 362, RX + RW - 16, 418], 12, fill=WARN_BG, outline=WARN, width=2)
        text(d, (RX + (370 + RW - 16) / 2, 390), lab, MONO_S, "#7A5A1E", "mm")
    if reveal < 1:   # 배선 장면: 그래프가 왼쪽에서 오른쪽으로 드러난다
        d.rectangle([RX + 40 + (RW - 60) * reveal, CY + 46, RX + RW - 4, CY + 346], fill="white")


def draw_registry(d, b, u, prev):
    d.rounded_rectangle([RX, CY, RX + RW, CY + CH], 18, fill="white", outline=SOFT, width=2)
    text(d, (RX + 24, CY + 14), "등록된 것", SMALL, GRAY)
    reg = b.get("reg", set())
    new = reg - prev.get("reg", set())
    y = CY + 70
    items = [("skill", "스킬", [("travel-memo", "이름·설명만 프롬프트에, 본문은 나중에")]),
             ("tools", "도구 (@tool)", [("load_skill(name)", "스킬 본문을 읽어 온다"),
                                        ("get_weather(city)", "도시의 현재 날씨(예시 데이터)"),
                                        ("c_to_f(celsius)", "섭씨를 화씨로 바꾼다")]),
             ("llm", "모델", [("ChatAnthropic.bind_tools(tools)", "도구 스키마 3개가 매 LLM 호출에 함께 간다")])]
    for key, head, rows in items:
        if key not in reg:
            continue
        a = ease(u * 2.5) if key in new else 1.0
        dy = (1 - a) * 30
        text(d, (RX + 30, y + dy), head, SUB, INK)
        y += 46
        for name, desc in rows:
            d.rounded_rectangle([RX + 30, y + dy, RX + RW - 30, y + 84 + dy], 14, fill=OK_BG if a == 1 else "#F2F7F4", outline=OK, width=2)
            text(d, (RX + 52, y + 14 + dy), name, MONO_S, TXT)
            text(d, (RX + 52, y + 48 + dy), fit(desc, SMALL, RW - 110), SMALL, GRAY)
            y += 98
        y += 18


def draw_msgs(d, b, u, prev):
    top = CY + 370
    d.rounded_rectangle([RX, top, RX + RW, CY + CH], 18, fill="white", outline=SOFT, width=2)
    text(d, (RX + 24, top + 14), 'state["messages"]', MONO_S, GRAY)
    n, pn = b.get("msgs", 0), prev.get("msgs", 0)
    text(d, (RX + RW - 24, top + 14), f"{n}개", SMALL, INK, "ra")
    y = top + 52
    for i in range(n):
        role, body = MSGS[i]
        fresh = i >= pn
        a = ease((u - 0.25) * 3) if fresh else 1.0
        if a <= 0:
            break
        fg, bg = ROLE.get(role, (WARN, WARN_BG))
        dx = (1 - a) * 60
        d.rounded_rectangle([RX + 20 + dx, y, RX + RW - 20 + dx, y + 56], 12, fill=bg, outline=fg if fresh else None, width=2)
        d.rounded_rectangle([RX + 30 + dx, y + 12, RX + 100 + dx, y + 44], 16, fill=fg)
        text(d, (RX + 65 + dx, y + 28), role, TINY, "white", "mm")
        text(d, (RX + 112 + dx, y + 18), fit(body, MONO_S, RW - 150), MONO_S, TXT)
        y += 66
    if b.get("skill_loaded") and not prev.get("skill_loaded") and u > 0.45:
        d.rounded_rectangle([RX + 190, top + 8, RX + RW - 70, top + 40], 14, fill=WARN_BG, outline=WARN, width=2)
        text(d, (RX + (190 + RW - 70) / 2, top + 24), "스킬 본문이 이제 컨텍스트에", TINY, "#7A5A1E", "mm")


def draw_final(d, u):
    a = ease(u * 2)
    x0, y0, x1, y1 = RX, CY, RX + RW, CY + 40 + (CH - 40) * a
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill="white", outline=INK, width=3)
    if a < 0.9:
        return
    text(d, (x0 + 28, y0 + 24), "최종 답 (Claude가 실제로 낸 문장)", SUB, INK)
    final = [m for u_ in UPD for m in u_["messages"]][-1]["content"].splitlines()
    y = y0 + 84
    for ln in final:
        for part in wrap(ln, BODY, x1 - x0 - 60):
            text(d, (x0 + 28, y), part, BODY, TXT)
            y += 38
        if not ln:
            y -= 14


def wrap(s, font, width):
    out, cur = [], ""
    for ch in s:
        if font.getlength(cur + ch) > width:
            out.append(cur); cur = ch
        else:
            cur += ch
    return out + [cur]


def draw_summary(im, u):
    d = ImageDraw.Draw(im, "RGBA")
    calls = sum(len(m.get("tool_calls", [])) for e in UPD for m in e["messages"])
    stats = [("LLM 호출", f"{sum(e['node'] == 'agent' for e in UPD)}번"), ("도구 실행", f"{calls}번"),
             ("메시지", f"{len(MSGS)}개"), ("LLM 대기 실측", f"{L1 + L2 + L3:.1f}초")]
    for i, (k, v) in enumerate(stats):
        a = ease(u * 3 - i * 0.35)
        x = 60 + i * 335
        d.rounded_rectangle([x, 200 + (1 - a) * 30, x + 300, 400 + (1 - a) * 30], 20, fill=OK_BG, outline=OK, width=2)
        text(d, (x + 150, 260 + (1 - a) * 30), k, SUB, GRAY, "mm")
        text(d, (x + 150, 340 + (1 - a) * 30), v, kr(64, "ExtraBold"), INK, "mm")
    pts = ["등록(한 번): 스킬 이름·설명, 도구 스키마, 노드, 간선 — compile() 로 굳힌다",
           "실행(턴마다): agent 가 LLM을 부르고 route 가 tool_calls 를 보고 tools 나 END 로 보낸다",
           "도구 결과는 ToolMessage 로 messages 에 붙고, 다음 턴 LLM 입력이 된다",
           "스킬은 처음엔 한 줄 소개뿐 — 본문은 모델이 load_skill 을 부를 때만 들어온다"]
    for i, p in enumerate(pts):
        a = ease(u * 3 - 1.2 - i * 0.3)
        if a > 0:
            d.ellipse([80, 486 + i * 110, 98, 504 + i * 110], fill=INK)
            for j, part in enumerate(wrap(p, BODY, W - 200)):
                text(d, (124 + (1 - a) * 30, 480 + i * 110 + j * 38), part, BODY, TXT)


def frame(bi, u):
    b = B[bi]
    prev = B[bi - 1] if bi else {}
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (40, 34), b["title"], sized(b["title"], "ExtraBold", 40, W - 320), TXT)
    turn = sum(1 for x in B[:bi + 1] if x["title"].startswith("턴") and "agent" in x["title"])
    chip = "등록 단계" if b.get("reg") else (f"턴 {turn}" if turn and not b.get("summary") and not b.get("final") else "")
    if chip:
        d.rounded_rectangle([W - 240, 30, W - 40, 82], 26, fill=INK if chip.startswith("턴") else SOFT)
        text(d, (W - 140, 56), chip, SUB, "white" if chip.startswith("턴") else INK, "mm")
    d.line([40, 100, 520, 100], fill=INK, width=4)
    if b.get("intro") or b.get("summary"):
        if b.get("intro"):
            text(d, (W / 2, 470), "에이전트 1개 · 스킬 1개 · 도구 3개", kr(56, "ExtraBold"), INK, "mm")
            text(d, (W / 2, 560), "Claude 로 실제로 한 번 돌리고, 줄 단위 실행 기록(sys.settrace)을 그대로 따라간다", BODY, GRAY, "mm")
        else:
            draw_summary(im, u)
    else:
        pt, ct = top_for(prev.get("seq")) if prev.get("seq") else top_for(b["seq"]), top_for(b["seq"])
        draw_code(im, b, u, pt + (ct - pt) * ease(u * 4))
        if b.get("final"):
            draw_graph(d, b, u); draw_final(d, u)
        elif b.get("graph"):
            draw_graph(d, b, u); draw_msgs(d, b, u, prev)
        else:
            draw_registry(d, b, u, prev)
    d.rounded_rectangle([40, 1000, W - 40, 1056], 14, fill="white")
    text(d, (64, 1028), b["cap"], sized(b["cap"], "Regular", 24, W - 140), TXT, "lm")
    return im


def main():
    OUT.mkdir(exist_ok=True)
    thumbs = [frame(i, 0.98).resize((W // 4, H // 4)) for i in range(len(B))]
    sheet = Image.new("RGB", (W // 4 * 4, H // 4 * ((len(B) + 3) // 4)), "white")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (i % 4 * (W // 4), i // 4 * (H // 4)))
    sheet.save(OUT / "sheet.png")
    if "--sheet" in sys.argv:
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                          str(OUT / "langgraph-turns.mp4")], stdin=subprocess.PIPE)
    for i, b in enumerate(B):
        n = int(b["t"] * FPS)
        for f in range(n):
            p.stdin.write(frame(i, f / (n - 1)).tobytes())
    p.stdin.close(); p.wait()
    print(OUT / "langgraph-turns.mp4", sum(b["t"] for b in B), "s")


if __name__ == "__main__":
    main()
