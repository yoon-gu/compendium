#!/usr/bin/env python3
"""에이전트 평가 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#1F5C4A", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, title, lines=(), accent=False, size=34, color=None):
    out = [rect(x, y, w, h, INK if accent else LINE, sw=4 if accent else 3),
           text(x + 26, y + 54, title, size, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 26, y + 106 + i * 50, ln, 28, color or GRAY))
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


def bar(x, y, w, h, frac, color=INK, back=SOFT):
    return rect(x, y, w, h, back, back, 0, 6) + rect(x, y, max(w * frac, 4), h, color, color, 0, 6)


figs = {}
OK = INK


def row(y, label, value, color=TXT, h=70, accent=False):
    return (rect(0, y, W, h, INK if accent else LINE, FILL, 4 if accent else 3) + text(26, y + h / 2 + 10, label, 28, TXT)
            + text(W - 26, y + h / 2 + 10, value, 28, color, "end", "bold"))


# ---------- 배경: LLM이 채점한다 ----------
h, b = stack([("트레이스", ["도구 호출 · 인자 · 중간 결과 · 최종 답"], False),
              ("채점 LLM", ["기준: 환불 전에 계정 ID를 확인했나?"], True),
              ("판정", ["예 / 아니요 + 한 줄 이유"], False)])
figs["judge"] = svg(h, b)

# ---------- 문제: 숨은 실패가 비용이 된다 ----------
b = [text(0, 34, "최종 답만 보면 안 보이는 것들", 28, TXT, weight="bold")]
for i, (t, sub) in enumerate([("청구서가 불어난다", "클라우드 · 토큰 비용"), ("할당량이 바닥난다", "API 호출 한도"),
                              ("사용자가 기다린다", "돌기만 하는 로딩 화면"), ("같은 일이 두 번", "중복 실행되는 작업"),
                              ("신뢰를 잃는다", "결국 사용자가 떠난다")]):
    y = 60 + i * 104
    b += [rect(0, y, W, 90, BAD if i == 4 else LINE, FILL, 4 if i == 4 else 3), text(28, y + 40, t, 28, TXT, weight="bold"),
          text(28, y + 76, sub, 22, GRAY)]
figs["costs"] = svg(580, "\n".join(b))

# ---------- 시뮬레이션 사용자 ----------
b = [box(0, 0, 400, 300, "시뮬레이션 사용자", ["LLM이 연기한다", "첫 메시지", "이뤄야 할 목표", "페르소나(선택)"], True),
     box(488, 0, 400, 300, "에이전트", ["시험 대상", "되묻고, 도구를 쓰고", "답한다"])]
for k, (y, lab) in enumerate([(70, "말 건다"), (150, "되묻는다"), (230, "알아서 답한다")]):
    if k % 2 == 0:
        b.append(arrow(404, y, 482, y))
    else:
        b.append(arrow(482, y, 406, y))
b += [text(444, 340, "대본 대신 목표만 준다 (즉흥 연기)", 26, GRAY, "middle"),
      rect(0, 380, W, 90, INK, SOFT, 3), text(444, 436, "실제 사용자가 생기면 → 운영 트레이스로 교체", 26, INK, "middle", "bold")]
figs["sim"] = svg(480, "\n".join(b))

# ---------- 네 층의 검사 ----------
b = []
for i, (t, sub, w) in enumerate([("통합 테스트", "여정 전체를 끝까지 돌린다", 520), ("LLM 판정", "예/아니요 루브릭", 640),
                                 ("결정론적 지표", "도구 인자·기준값을 코드로 대조", 760), ("단위 테스트", "도구 하나하나가 제대로 도는가", 888)]):
    y, x = i * 104, (W - w) / 2
    b += [rect(x, y, w, 90, INK if i == 1 else LINE, SOFT if i != 1 else FILL, 4 if i == 1 else 3),
          text(444, y + 40, t, 28, INK if i == 1 else TXT, "middle", "bold"), text(444, y + 76, sub, 22, GRAY, "middle")]
b += [text(444, 470, "코드로 잴 수 있는 것은 코드로", 28, INK, "middle", "bold"),
      text(444, 516, "사람의 판단이 필요한 것만 채점 LLM에게", 24, GRAY, "middle")]
figs["layers"] = svg(530, "\n".join(b))

# ---------- 함정 2: 1-5점 vs 예/아니요 ----------
b = [box(0, 0, 420, 420, "1-5점으로 물으면", ["얼마나 도움이 됐나?"]),
     box(468, 0, 420, 420, "예/아니요로 물으면", ["계정 ID를 먼저 확인했나?"], True)]
for k, (day, v) in enumerate([("어제", 4), ("오늘", 3)]):
    y = 190 + k * 100
    b += [text(26, y + 26, day, 26, GRAY), bar(110, y, 240, 34, v / 5, BAD), text(394, y + 28, f"{v}점", 28, BAD, "end", "bold")]
    b += [text(494, y + 26, day, 26, GRAY), rect(580, y - 6, 120, 46, INK, INK, 0, 23), text(640, y + 26, "예", 28, FILL, "middle", "bold")]
b += [text(26, 400, "같은 답인데 점수가 흔들린다", 22, BAD), text(494, 400, "판정이 흔들릴 틈이 좁다", 22, INK),
      text(0, 470, "점수는 설명을 위한 예시 값", 22, GRAY)]
figs["score"] = svg(490, "\n".join(b))

# ---------- 함정 3: 청구서 ----------
b = [text(0, 34, "같은 답의 운영 청구서", 28, TXT, weight="bold"),
     row(60, "품질 검사", "전부 통과", INK, accent=True),
     row(150, "지연 (목표 30초)", "40초", BAD), row(240, "도구 호출", "12번 (쓸데없이)", BAD),
     row(330, "질의 하나당 비용", "60센트", BAD),
     rect(0, 440, W, 90, BAD, FILL, 4), text(444, 497, "운영 판정: 불합격", 34, BAD, "middle", "bold")]
figs["bill"] = svg(540, "\n".join(b))

# ---------- Day 0: 빨간 펜 ----------
steps = [("1", "search_trades(id=\"T-8812\")", ""),
         ("2", "생각: 음… 다시 확인해 볼까", "머뭇거림"),
         ("3", "ledger_lookup(account=\"ACC-0000\")", "지어낸 인자"),
         ("4", "send_email(to=\"broker\")", "잘못 고른 도구"),
         ("5", "최종 답: 확인 결과를 길게 늘어놓음…", "말이 길어짐")]
b = [text(0, 34, "트레이스 한 건을 처음부터 끝까지 읽는다", 28, TXT, weight="bold")]
for i, (n, s, mark) in enumerate(steps):
    y = 64 + i * 96
    b += [rect(0, y, W, 80, BAD if mark else LINE, FILL, 3), text(22, y + 50, n, 26, GRAY, weight="bold"),
          text(62, y + 50, s, 25, TXT, mono=True)]
    if mark:
        b += [f'<line x1="62" y1="{y + 62}" x2="{62 + 14 * len(s)}" y2="{y + 64}" stroke="{BAD}" stroke-width="4" stroke-linecap="round"/>',
              text(W - 20, y + 30, mark, 22, BAD, "end", "bold")]
b += [text(0, 580, "이렇게 스무 개쯤 → 실패 유형이 보인다", 26, INK, weight="bold")]
figs["redpen"] = svg(600, "\n".join(b))

# ---------- Day 1: 몇 개 찍어 보기 vs 시험 묶음 전체 ----------
b = [box(0, 0, W, 130, "몇 개 찍어 보기", ["새 프롬프트가 더 똑똑해 보인다"]),
     text(0, 200, "시험 묶음 전체를 돌리자", 28, INK, weight="bold")]
for k, (lab, a, z, after) in enumerate([("지연", 0.4, 0.8, "두 배"), ("지어낸 인자", 0.4, 0.55, "+15%")]):
    y = 240 + k * 150
    b += [text(0, y + 26, lab, 28, TXT, weight="bold"),
          text(0, y + 72, "전", 22, GRAY), bar(60, y + 48, 640, 30, a, LINE),
          text(0, y + 116, "후", 22, GRAY), bar(60, y + 92, 640, 30, z, BAD), text(W, y + 116, after, 28, BAD, "end", "bold")]
b += [text(0, 560, "감으로는 나아졌는데 숫자로는 나빠졌다", 26, BAD, weight="bold"),
      text(0, 604, "막대 길이는 비율만 보여 주는 그림", 22, GRAY)]
figs["tuning"] = svg(620, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
