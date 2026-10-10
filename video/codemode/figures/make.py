#!/usr/bin/env python3
"""Codemode 화면용 다이어그램을 SVG 로 그린다(원문·공식 문서의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT = "#1F5F7A", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, title, lines=(), accent=False, size=34):
    out = [rect(x, y, w, h, INK if accent else LINE, sw=4 if accent else 3),
           text(x + 26, y + 54, title, size, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 26, y + 106 + i * 50, ln, 28, GRAY))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label="", color=INK, lx=None, ly=None, anchor="start"):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text(lx if lx is not None else (x1 + x2) / 2 + 16, ly if ly is not None else (y1 + y2) / 2 + 10, label, 25, GRAY, anchor))
    return "\n".join(out)


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def stack(items, gap=52, top=0):
    """세로로 쌓은 상자들 + 사이 화살표. items: (title, lines, accent)"""
    y, out = top, []
    for i, (t, ls, acc) in enumerate(items):
        h = 84 + 50 * len(ls) + (14 if ls else 0)
        out.append(box(0, y, W, h, t, ls, acc))
        y += h
        if i < len(items) - 1:
            out.append(arrow(W / 2, y + 4, W / 2, y + gap - 4)); y += gap
    return y, "\n".join(out)


figs = {}

# ---------- 용어 그림 ----------
# 도구 호출
h, b = stack([("① 하니스가 도구 정의를 건넨다", ["이름·설명·인자 형식이 매 요청마다 실린다"], False),
              ("② 모델이 호출을 요청한다", ["예: 이슈 목록 도구를 state=open 으로"], False),
              ("③ 하니스가 실행하고 결과를 돌려준다", ["결과는 컨텍스트에 쌓이고, 모델이 다음을 정한다"], True)])
figs["t-tool"] = svg(h, b)

# 하니스
b = [rect(0, 0, W, 470, INK, sw=4),
     text(28, 54, "하니스 (harness) = 모델에 채우는 마구", 32, INK, weight="bold"),
     rect(294, 170, 300, 130, TXT, SOFT, 4), text(444, 228, "모델", 36, TXT, "middle", "bold"), text(444, 270, "(LLM)", 26, GRAY, "middle")]
for (x, y, t) in [(28, 96, "도구 정의·실행"), (560, 96, "샌드박스"), (28, 340, "세션·기록"), (560, 340, "권한·설정")]:
    b += [rect(x, y, 300, 70, LINE), text(x + 150, y + 46, t, 28, TXT, "middle")]
b += [text(28, 446, "예: Pi, Claude Code, Codex CLI — 모델을 에이전트로 만드는 실행기", 24, GRAY)]
figs["t-harness"] = svg(470, "\n".join(b))

# MCP
b = [box(0, 110, 300, 200, "에이전트", ["(하니스)"], True)]
for i, name in enumerate(["GitHub", "Sentry", "Cloudflare"]):
    y = 40 + i * 130
    b += [rect(468, y, 420, 100, LINE), text(494, y + 44, f"{name} MCP 서버", 30, TXT, weight="bold"), text(494, y + 82, "도구 목록 + 실행", 24, GRAY),
          arrow(304, 210, 462, y + 50)]
b += [text(330, 30, "같은 규격으로 연결", 25, INK),
      text(0, 460, "서비스마다 따로 붙이지 않고, 한 가지 꽂는 방식으로", 28, TXT),
      text(0, 500, "도구를 찾고 부른다 (Anthropic, 2024 공개)", 28, GRAY)]
figs["t-mcp"] = svg(520, "\n".join(b))

# ---------- 비유·예시 ----------
# 심부름
b = [box(0, 0, 420, 360, "전화로 하나씩", ["“우유 샀어. 다음은?”", "“계란 샀어. 다음은?”", "“빵 샀어. 다음은?”", "… 통화 100번"]),
     box(468, 0, 420, 360, "쪽지 한 장", ["“목록대로 사고,", "제일 싼 것만 골라서,", "영수증 요약만 줘.”", "→ 통화 2번"], True),
     text(0, 420, "모델은 계획을 쪽지로 쓰고, 노동은 코드가 한다", 29, TXT)]
figs["ex-errand"] = svg(440, "\n".join(b))

# 왕복 비교 (핵심 그림)
b = [text(0, 36, "보통의 도구 호출", 32, TXT, weight="bold"), text(468, 36, "Codemode", 32, INK, weight="bold")]
# 왼쪽: 모델 ↔ 도구 수직 레인
for x, lab in [(70, "모델"), (350, "도구")]:
    b += [rect(x - 60, 60, 120, 54, LINE, SOFT), text(x, 97, lab, 26, TXT, "middle", "bold"),
          f'<line x1="{x}" y1="114" x2="{x}" y2="500" stroke="{LINE}" stroke-width="3" stroke-dasharray="8 8"/>']
for k in range(3):
    y = 150 + k * 100
    b += [arrow(74, y, 344, y, f"호출 {k + 1}", lx=210, ly=y - 10, anchor="middle"),
          f'<line x1="346" y1="{y + 44}" x2="76" y2="{y + 44}" stroke="{GRAY}" stroke-width="3" marker-end="url(#a)"/>',
          text(210, y + 36, f"결과 {k + 1}", 22, GRAY, "middle")]
b += [text(210, 470, "⋮  100번 왕복", 28, INK, "middle", "bold")]
# 오른쪽: 모델 → 런타임 → 모델
b += [rect(478, 60, 120, 54, LINE, SOFT), text(538, 97, "모델", 26, TXT, "middle", "bold"),
      f'<line x1="538" y1="114" x2="538" y2="500" stroke="{LINE}" stroke-width="3" stroke-dasharray="8 8"/>',
      rect(690, 60, 194, 440, INK, sw=4), text(787, 94, "하니스 런타임", 24, INK, "middle", "bold"),
      arrow(542, 150, 684, 150, "스크립트 1편", lx=613, ly=136, anchor="middle")]
for i in range(60):
    cx, cy = 714 + (i % 6) * 29, 140 + (i // 6) * 28
    b.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{INK}" opacity="0.55"/>')
b += [text(787, 438, "도구 호출 100번", 22, TXT, "middle"), text(787, 466, "(병렬, 안에서만)", 22, GRAY, "middle"),
      f'<line x1="686" y1="484" x2="544" y2="484" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>',
      text(613, 474, "12줄", 24, INK, "middle", "bold")]
# 아래: 컨텍스트 막대
b += [text(0, 560, "컨텍스트에 쌓이는 것", 26, GRAY),
      rect(0, 580, 420, 44, LINE, INK, 0, 8), text(16, 611, "결과 100개 전부", 24, FILL, weight="bold"),
      rect(468, 580, 420, 44, LINE, SOFT, 0, 8), rect(468, 580, 60, 44, LINE, INK, 0, 8), text(544, 611, "반환값 12줄만", 24, INK, weight="bold"),
      text(0, 680, "모델 추론 101번", 30, TXT, weight="bold"), text(468, 680, "모델 추론 2번", 30, INK, weight="bold")]
figs["roundtrip"] = svg(700, "\n".join(b))

# 이슈 100개 → 12개
b = [text(0, 34, "열린 GitHub 이슈 100개", 28, TXT, weight="bold")]
for i in range(100):
    x, y = (i % 10) * 34, 56 + (i // 10) * 34
    b.append(f'<rect x="{x}" y="{y}" width="26" height="26" rx="4" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>')
b += [arrow(352, 226, 470, 226, "분류기", lx=411, ly=210, anchor="middle"), text(411, 262, "동시 4개씩", 22, GRAY, "middle"),
      text(500, 34, "좌절 점수 상위 12개", 28, INK, weight="bold")]
for i in range(12):
    x, y = 500 + (i % 4) * 46, 56 + (i // 4) * 46
    b.append(f'<rect x="{x}" y="{y}" width="38" height="38" rx="5" fill="{INK}"/>')
b += [text(500, 240, "#번호 (점수/10) 제목", 24, GRAY), text(500, 274, "이 12줄만 모델에게", 24, INK, weight="bold"),
      text(0, 430, "이슈 본문 100개와 분류 결과 100개는", 28, TXT),
      text(0, 470, "런타임 안에서만 오가고 사라진다", 28, TXT)]
figs["ex-issues"] = svg(490, "\n".join(b))

# 코드 카드
code = ["// 모델이 쓴 스크립트 (요약)",
        "const issues = await tools.github.list_issues(",
        "    { state: \"open\" });",
        "const scored = await Promise.all(issues.map(i =>",
        "    models.classify({ text: i.body },",
        "        { question: \"좌절 점수 0-10\" })));",
        "const top = scored.sort(byScore).slice(0, 12);",
        "store(\"frustrated_issues\", top);",
        "return top;   // 이 값만 모델에게"]
b = [rect(0, 0, W, 60 + 46 * len(code), "#2A2A28", "#1E1E1C", 0, 14)]
for i, ln in enumerate(code):
    b.append(text(28, 56 + i * 46, ln, 26, "#9FC6D6" if ln.lstrip().startswith("//") or "//" in ln and i == len(code) - 1 else "#F4F4F1", mono=True))
figs["ex-code"] = svg(60 + 46 * len(code), "\n".join(b))

# 샌드박스
b = [rect(0, 0, W, 500, LINE, SOFT, 3), text(26, 46, "하니스(뇌) 안", 28, GRAY, weight="bold"),
     rect(40, 70, 500, 400, INK, FILL, 4), text(66, 120, "QuickJS · WASM 런타임", 30, INK, weight="bold"),
     text(66, 160, "메모리 256MB", 26, GRAY)]
for i, t in enumerate(["네트워크", "파일시스템", "타이머", "Node API"]):
    y = 214 + i * 60
    b += [text(66, y, "✗", 30, "#A23B3B", weight="bold"), text(106, y, t + " 없음", 28, TXT)]
b += [arrow(544, 200, 690, 200), rect(694, 160, 170, 80, INK, FILL, 3), text(779, 210, "tools.*", 28, INK, "middle", "bold", True),
      arrow(544, 330, 690, 330), rect(694, 290, 170, 80, INK, FILL, 3), text(779, 340, "models.*", 28, INK, "middle", "bold", True),
      text(570, 420, "바깥으로 나가는 길은", 24, GRAY), text(570, 452, "이 둘뿐", 24, INK, weight="bold")]
figs["t-sandbox"] = svg(500, "\n".join(b))

# 뇌와 손
b = [box(0, 0, 420, 400, "뇌 = 하니스", ["신뢰하는 쪽", "모델 프로토콜을 직접 다룬다", "이미지 읽기, 하위 에이전트", "Codemode 런타임도 여기"], True),
     box(468, 0, 420, 400, "손 = 실행 환경", ["격리할 수 있는 쪽", "bash, 파일, 프로그램 실행", "예: Gondolin 샌드박스", "(뇌는 가두지 못한다)"]),
     text(0, 460, "같은 기계일 수도 있지만 파일시스템과 신뢰 수준이 다르다", 27, TXT)]
figs["brain-hands"] = svg(480, "\n".join(b))

# 점진적 발견
b = [text(0, 34, "목록 통째로 싣기", 30, TXT, weight="bold"), text(468, 34, "필요할 때 찾기", 30, INK, weight="bold"),
     rect(0, 56, 420, 400, LINE)]
for i in range(14):
    b.append(f'<rect x="20" y="{74 + i * 27}" width="{380 - (i * 37) % 140}" height="16" rx="4" fill="{LINE}"/>')
b += [rect(468, 56, 420, 400, INK, sw=4),
      text(490, 108, "searchTools(\"sentry\")", 24, INK, weight="bold", mono=True),
      arrow(678, 128, 678, 186),
      rect(490, 196, 376, 56, LINE), text(508, 233, "sentry.list_orgs", 24, TXT, mono=True),
      rect(490, 266, 376, 56, LINE), text(508, 303, "sentry.list_projects", 24, TXT, mono=True),
      text(490, 380, "도구 설명 길이는", 26, GRAY), text(490, 416, "서버가 늘어도 그대로", 26, INK, weight="bold"),
      text(0, 500, "MCP 서버마다 도구 수십 개 → 매 요청 컨텍스트에", 26, GRAY)]
figs["ex-discovery"] = svg(520, "\n".join(b))

# Codemode 안의 Codemode
b = [rect(0, 0, W, 300, INK, FILL, 4), text(26, 50, "Pi Codemode (바깥 스크립트)", 30, INK, weight="bold"),
     rect(40, 80, 808, 190, LINE, SOFT, 3), text(66, 126, "MCP 서버 자체의 Code Mode (안쪽 스크립트)", 28, TXT, weight="bold"),
     text(66, 176, "코드를 문자열로 넘기고, 결과도 문자열 안의 JSON", 25, GRAY),
     text(66, 226, '"{\\"result\\": \\"{\\\\\\"id\\\\\\": 1}\\"}"', 25, "#A23B3B", mono=True)]
for i, t in enumerate(["JSON 이 두 번 이스케이프된다", "작은 모델은 헷갈린다", "안쪽 코드는 바깥 도구를 부를 수 없다"]):
    b.append(text(0, 360 + i * 50, "· " + t, 28, TXT))
figs["ex-nested"] = svg(480, "\n".join(b))

# 결과 형태가 배치 크기에 따라 바뀌는 서버 (지어낸 예시)
b = [box(0, 0, 420, 230, "탐색: 3개 요청", []), text(26, 120, "[ {…}, {…}, {…} ]", 26, TXT, mono=True), text(26, 180, "✓ 스크립트 통과", 26, INK, weight="bold"),
     box(468, 0, 420, 230, "본 실행: 100개 요청", [], True), text(494, 120, "{ \"page\": 1,", 26, TXT, mono=True),
     text(494, 156, "  \"items\": […] }", 26, TXT, mono=True), text(494, 206, "✗ 같은 코드가 깨진다", 26, "#A23B3B", weight="bold"),
     text(0, 290, "(지어낸 예시) 출력 모양이 늘 같아야 코드가 믿고 쓴다", 26, GRAY)]
figs["ex-shape"] = svg(310, "\n".join(b))

# 조합이 일어나는 자리
b = [box(0, 0, 420, 270, "CLI", ["손(실행 환경)에서 조합", "grep | sort | head"]),
     box(468, 0, 420, 270, "Codemode", ["뇌(하니스) 안의", "격리된 방에서 조합", "tools + models"], True),
     text(0, 330, "같은 생각: 선택지를 늘리지 말고 조합의 힘을 줘라", 28, TXT, weight="bold")]
figs["compose"] = svg(350, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
