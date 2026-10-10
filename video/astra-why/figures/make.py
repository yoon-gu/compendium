#!/usr/bin/env python3
"""astra-why 화면용 다이어그램을 SVG 로 그린다. 원문 코드는 옮기지 않고, 코드 그림은 모양만 보여 주려고 새로 지어낸 예시다.  python3 make.py"""
import html
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT = "#8C4A12", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{html.escape(s, quote=False)}</text>')


def rect(x, y, w, h, accent=False, fill=FILL, rx=14):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK if accent else LINE}" stroke-width="{4 if accent else 3}"/>'


def box(x, y, w, h, title, lines=(), accent=False, size=30):
    out = [rect(x, y, w, h, accent), text(x + 28, y + 58, title, 36, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 28, y + 110 + i * 50, ln, size, GRAY))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label="", dx=16):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + 10, label, 26, GRAY))
    return "\n".join(out)


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def code(x, y, w, lines, title, accent=False, size=25, lh=40):
    h = 76 + lh * len(lines) + 20
    out = [rect(x, y, w, h, accent), text(x + 24, y + 48, title, 28, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 24, y + 100 + i * lh, ln, size, TXT, mono=True))
    return h, "\n".join(out)


figs = {}

# 1. 내권(内卷) — 투입은 늘고 산출은 제자리
b = [text(0, 40, "내권 (内卷, involution)", 36, INK, weight="bold"),
     text(0, 82, "모두가 더 많이 일하는데, 아무도 나아지지 않는 상태", 27, GRAY),
     f'<line x1="70" y1="440" x2="{W - 10}" y2="440" stroke="{LINE}" stroke-width="3"/>',
     f'<line x1="70" y1="120" x2="70" y2="440" stroke="{LINE}" stroke-width="3"/>',
     text(W / 2 + 30, 484, "시간 →", 26, GRAY, "middle")]
pts_in = " ".join(f"{70 + i * 40},{430 - (i ** 1.6) * 2.3:.0f}" for i in range(21))
pts_out = " ".join(f"{70 + i * 40},{372 - (4 if i > 3 else i):.0f}" for i in range(21))
b += [f'<polyline points="{pts_in}" fill="none" stroke="{INK}" stroke-width="6"/>',
      f'<polyline points="{pts_out}" fill="none" stroke="{GRAY}" stroke-width="6" stroke-dasharray="14 8"/>',
      text(W - 14, 170, "들어가는 토큰·시간", 28, INK, "end", "bold"),
      text(W - 14, 352, "나오는 소프트웨어의 질", 28, GRAY, "end", "bold"),
      text(0, 540, "원래는 농업을 두고 쓴 인류학 개념 → 중국 인터넷의 '소모적 경쟁'", 26, TXT),
      text(0, 590, "저자: 지금의 AI 엔지니어링이 이 모양이다", 26, TXT)]
figs["t-involution"] = svg(610, "\n".join(b))

# 2. 소프트웨어 공장
h, b = 0, []
items = [("사람 · 프롬프트 한 번", ["‘가상 스레드와 어휘적 범위가 있는 파이썬 포크’"], False),
         ("주 에이전트 (GPT 6 Astra)", ["작업 흐름을 스스로 정하고, 자기 컨텍스트를 관리"], True),
         ("agent-notes 폴더 · 하위 에이전트들", ["메모를 남기고, 일을 쪼개 하위 에이전트에게"], True),
         ("커밋 → 다시 계획 → 다시 커밋 …", ["사람이 중간에 들여다보지 않는 채로 주말 내내"], False)]
y = 0
for i, (t, ls, acc) in enumerate(items):
    hh = 92 + 50 * len(ls) + 18
    b.append(box(0, y, W, hh, t, ls, acc, size=28)); y += hh
    if i < len(items) - 1:
        b.append(arrow(W / 2, y + 4, W / 2, y + 48)); y += 52
figs["t-factory"] = svg(y, "\n".join(b))

# 3. 하위 에이전트
b = [text(0, 40, "하위 에이전트 (sub-agent)", 36, INK, weight="bold"),
     text(0, 82, "주 에이전트가 일을 떼어 맡기는 또 다른 에이전트", 27, GRAY),
     box(234, 110, 420, 130, "주 에이전트", ["결과 요약만 받는다"], True)]
for i, lab in enumerate(["빌드·테스트", "C 소스 수정", "소켓 실험"]):
    x = i * 304
    b.append(arrow(444, 244, x + 140, 330))
    b.append(box(x, 334, 280, 130, lab, ["도구 호출 수십 번"], size=26))
b += [f'<rect x="0" y="494" width="{W}" height="120" rx="14" fill="{SOFT}"/>',
      text(24, 544, "중간의 도구 호출은 사람도, 주 에이전트도 거의 안 본다", 28, TXT),
      text(24, 590, "→ 아무도 안 볼 때 더 이상해진다", 28, INK, weight="bold")]
figs["t-subagent"] = svg(620, "\n".join(b))

# 4. 코드골프란 (지어낸 예시)
h1, c1 = code(0, 100, W, ["total = 0", "for n in range(1, 101):", "    if n % 2 == 0:", "        total += n", "print(total)"],
              "사람이 읽기 좋게 · 5줄")
h2, c2 = code(0, 100 + h1 + 40, W, ["print(sum(range(2,101,2)))"], "코드골프 · 26글자", accent=True)
b = [text(0, 40, "코드골프 (code golf)", 36, INK, weight="bold"),
     text(0, 82, "같은 일을 하는 프로그램을 가장 적은 글자로 쓰는 놀이", 27, GRAY), c1, c2,
     text(0, 100 + h1 + 40 + h2 + 50, "둘 다 1부터 100까지 짝수의 합 · 지어낸 예시", 26, GRAY)]
figs["t-codegolf"] = svg(100 + h1 + 40 + h2 + 70, "\n".join(b))

# 5. 코드골프식 도구 호출 다섯 가지
b = [text(0, 40, "저자가 본 코드골프식 도구 호출", 34, INK, weight="bold")]
rows = [("C 소스를 파이썬 문자열로", "패치 도구 대신 잘라 붙이기, 빌드·테스트까지"),
        ("소켓 코드골프", "파일 디스크립터 전달을 압축 스크립트로 시험"),
        ("메모 고치기", "정규식 치환 한 줄 + 바로 git 명령"),
        ("파이썬으로 Node.js", "가상 머신 속 윈도우에서 클립보드 시험"),
        ("Bash → Python → Node → PowerShell", "명령 하나가 네 겹의 사슬로")]
for i, (t, d) in enumerate(rows):
    y = 70 + i * 128
    b += [rect(0, y, W, 112, accent=(i == 4)), text(24, y + 48, t, 30, INK if i == 4 else TXT, weight="bold"), text(24, y + 92, d, 26, GRAY)]
figs["ex-toolcalls"] = svg(70 + 5 * 128, "\n".join(b))

# 6. 도구 호출 사슬
b = [text(0, 40, "명령 하나를 실행하려고 거친 길", 30, GRAY)]
for i, lab in enumerate(["Bash", "Python", "Node.js", "PowerShell"]):
    y = 70 + i * 150
    b.append(rect(160, y, 568, 100, accent=(i == 3)))
    b.append(text(W / 2, y + 64, lab, 36, INK if i == 3 else TXT, "middle", "bold"))
    if i < 3:
        b.append(arrow(W / 2, y + 104, W / 2, y + 146))
b.append(text(W / 2, 70 + 4 * 150 + 10, "사람이 따라가며 읽기에는 너무 먼 길", 28, TXT, "middle"))
figs["ex-chain"] = svg(70 + 4 * 150 + 30, "\n".join(b))

# 7. 커밋으로 새는 코드골프 (지어낸 예시)
h1, c1 = code(0, 0, W, ["MAX_RETRIES = 3", "TIMEOUT_SEC = 5", "", "def fetch_with_retry(url):",
                        "    for attempt in range(MAX_RETRIES):", "        try:",
                        "            return fetch(url, timeout=TIMEOUT_SEC)", "        except TimeoutError:",
                        "            log(f\"retry {attempt + 1}\")", "    raise FetchFailed(url)"],
              "사람이 쓰는 모양 · 이름 붙인 상수, 들여쓰기", size=24, lh=38)
h2, c2 = code(0, h1 + 36, W, ["def f(u):", " for i in range(3):", "  try:return g(u,timeout=5)", "  except TimeoutError:p(i+1)",
                              " raise E(u)"], "코드골프식 · 매직 넘버, 들여쓰기 최소", accent=True, size=24, lh=38)
b = [c1, c2, text(0, h1 + 36 + h2 + 50, "같은 동작 · 지어낸 예시 (원문 코드 아님)", 26, GRAY)]
figs["ex-leak"] = svg(h1 + 36 + h2 + 70, "\n".join(b))

# 8. 토큰 10% 절약
b = [text(0, 36, "같은 테스트 코드의 토큰 수", 28, GRAY),
     f'<rect x="0" y="60" width="{W}" height="70" rx="10" fill="{LINE}"/>', text(20, 106, "ruff format 을 돌린 뒤 · 100", 30, FILL, weight="bold"),
     f'<rect x="0" y="160" width="{int(W * 0.9)}" height="70" rx="10" fill="{INK}"/>', text(20, 206, "모델이 쓴 그대로 · 약 90", 30, FILL, weight="bold"),
     text(0, 290, "아낀 것은 약 10% · 잃은 것은 사람이 읽을 수 있는 모양", 28, TXT)]
figs["ex-tokens"] = svg(310, "\n".join(b))

# 9. 순환 복잡도
b = [text(0, 40, "순환 복잡도 (cyclomatic complexity)", 34, INK, weight="bold"),
     text(0, 82, "코드 안의 독립된 실행 경로 수 · 낮을수록 단순하다고 본다", 27, GRAY)]
nodes = {"시작": (444, 140), "if 조건": (444, 250), "A": (250, 370), "B": (638, 370), "합류": (444, 490), "끝": (444, 600)}
edges = [("시작", "if 조건"), ("if 조건", "A"), ("if 조건", "B"), ("A", "합류"), ("B", "합류"), ("합류", "끝")]
for a, c in edges:
    (x1, y1), (x2, y2) = nodes[a], nodes[c]
    k = 38 / max(1, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    b.append(arrow(x1 + (x2 - x1) * k, y1 + (y2 - y1) * k, x2 - (x2 - x1) * k * 1.1, y2 - (y2 - y1) * k * 1.1))
for lab, (x, y) in nodes.items():
    acc = lab == "if 조건"
    b.append(f'<rect x="{x - 90}" y="{y - 32}" width="180" height="64" rx="32" fill="{FILL}" stroke="{INK if acc else LINE}" stroke-width="{4 if acc else 3}"/>')
    b.append(text(x, y + 10, lab, 28, INK if acc else TXT, "middle", "bold" if acc else "normal"))
b += [text(0, 700, "M = E − N + 2  →  6 − 6 + 2 = 2 (경로 둘)", 30, TXT, weight="bold"),
      text(0, 750, "분기를 숫자 표로 숨기면 M 은 1로 떨어진다", 27, GRAY),
      text(0, 794, "지표는 좋아지지만, 사람에게는 매직 넘버만 남는다", 27, GRAY)]
figs["t-cc"] = svg(820, "\n".join(b))

# 10. 저자가 추측한 훈련 보상
b = [text(0, 36, "저자의 추측 · 훈련이 무엇에 보상을 주는가", 28, GRAY)]
rows = [("긴 과제를 끝까지 완료", 0.95), ("토큰 효율", 0.75), ("단순한 지표 (순환 복잡도 등)", 0.6), ("사람이 읽기 좋은 코드", 0.06)]
for i, (lab, v) in enumerate(rows):
    y = 70 + i * 116
    b += [text(0, y + 30, lab, 28, TXT), f'<rect x="0" y="{y + 46}" width="{W}" height="42" rx="8" fill="{SOFT}"/>',
          f'<rect x="0" y="{y + 46}" width="{int(W * v)}" height="42" rx="8" fill="{INK if i < 3 else GRAY}"/>']
b.append(text(0, 70 + 4 * 116 + 20, "막대 길이는 개념 그림 · 실제 측정값 아님", 25, GRAY))
figs["reward"] = svg(70 + 4 * 116 + 40, "\n".join(b))

# 11. 안 보면 AGI다
b = [box(0, 0, 420, 400, "보고서만 보면", ["과제 완료", "테스트 통과", "커밋 79개", "실패율도 낮다"], True, size=28),
     box(468, 0, 420, 400, "들여다보면", ["매직 넘버투성이", "한 줄에 매크로 여럿", "아무 인덱스에 상태", "흉한 토크나이저"], size=28),
     f'<line x1="444" y1="20" x2="444" y2="380" stroke="{LINE}" stroke-width="3" stroke-dasharray="10 8"/>',
     text(0, 460, "사람이 덜 볼수록, 품질은 덜 중요해진다", 30, TXT, weight="bold")]
figs["ex-look"] = svg(480, "\n".join(b))

# 12. 실험 수치
tiles = [("약 35시간", "프롬프트 하나로"), ("약 10억", "토큰"), ("약 1,200달러", "API 원가"),
         ("75,000줄", "순증 코드"), ("79개", "커밋 · 하나에 약 15.50달러"), ("약 1,400개", "에이전트 간 메시지")]
b = []
for i, (big, small) in enumerate(tiles):
    x, y = (i % 2) * 468, (i // 2) * 196
    b += [rect(x, y, 420, 170, accent=(i == 4)), text(x + 28, y + 76, big, 46, INK, weight="bold"), text(x + 28, y + 130, small, 26, GRAY)]
b.append(text(0, 3 * 196 + 30, "쓸 만한 결과물: 없음", 34, TXT, weight="bold"))
figs["numbers"] = svg(3 * 196 + 50, "\n".join(b))

# 13. 무너진 과제 이름
b = [text(0, 36, "에이전트 메모 속 과제 이름의 변화", 28, GRAY)]
for i, n in enumerate(["1", "2", "3", "5", "5a"]):
    x = i * 112
    b += [rect(x, 64, 96, 72, rx=10), text(x + 48, 112, n, 30, TXT, "middle", "bold", mono=True)]
b += [text(600, 112, "…", 34, GRAY, "middle"), arrow(W / 2, 150, W / 2, 196),
      rect(0, 204, W, 80, accent=True, rx=10), text(W / 2, 256, "8b2c2b2b checkpoint1", 32, INK, "middle", "bold", mono=True),
      text(0, 340, "처음엔 번호, 나중엔 사람이 읽을 수 없는 문자열", 28, TXT)]
figs["ex-names"] = svg(360, "\n".join(b))

# 14. 버리는 코드와 커밋하는 코드
b = [box(0, 0, 420, 360, "버리는 코드", ["도구 호출, 일회용 스크립트", "모델만 읽는다", "빽빽해도 참을 만하다"], size=28),
     box(468, 0, 420, 360, "커밋하는 코드", ["테스트, 프로덕션 코드", "사람이 읽고 고친다", "모양이 곧 품질"], True, size=28),
     f'<line x1="444" y1="0" x2="444" y2="360" stroke="{INK}" stroke-width="6"/>',
     text(0, 420, "이 선을 긋지 않으면, 코드골프가 커밋이 된다", 30, TXT, weight="bold")]
figs["ex-line"] = svg(440, "\n".join(b))

# 15. 누구를 위한 모델인가
b = [box(0, 0, W, 170, "엔지니어", ["지금의 워크플로로 이미 검증된 이득 · 더 비싼 모델이 더 낫지 않다"], size=26)]
for i, lab in enumerate(["변호사", "3D 아티스트", "수학자", "컴퓨터 사용 자동화"]):
    x, y = (i % 2) * 468, 210 + (i // 2) * 130
    b += [rect(x, y, 420, 106, accent=True), text(x + 210, y + 66, lab, 32, INK, "middle", "bold")]
b.append(text(0, 210 + 2 * 130 + 40, "저자의 추측: 점점 이쪽을 위해 만들어지는 듯하다", 28, TXT))
figs["who"] = svg(210 + 2 * 130 + 60, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
