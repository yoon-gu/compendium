#!/usr/bin/env python3
"""마케팅 엔지니어 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#2B4C7E", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
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

# ---------- 배경: 코딩 에이전트 + MCP ----------
b = [rect(0, 0, 420, 330, INK, FILL, 4), text(26, 54, "내 폴더", 34, INK, weight="bold"),
     text(26, 110, "코딩 에이전트", 30, TXT, weight="bold"),
     text(26, 160, "파일을 읽고 쓴다", 26, GRAY), text(26, 206, "코드를 돌린다", 26, GRAY), text(26, 252, "예약해 두면 밤에도", 26, GRAY),
     text(26, 296, "= 아주 빠른 신입", 26, INK, weight="bold")]
for i, t in enumerate(["CRM", "결제·매출", "슬랙", "광고 관리자"]):
    y = 10 + i * 82
    b += [rect(560, y, 328, 66, LINE, SOFT, 3), text(724, y + 43, t, 28, TXT, "middle"),
          f'<line x1="424" y1="{165}" x2="556" y2="{y + 33}" stroke="{INK}" stroke-width="3"/>']
b += [rect(450, 140, 84, 50, INK, INK, 0, 25), text(492, 174, "MCP", 22, FILL, "middle", "bold"),
      text(444, 380, "MCP = 에이전트에 도구를 꽂는 만능 플러그", 26, GRAY, "middle")]
figs["agent"] = svg(400, "\n".join(b))

# ---------- 배경: 캠페인 ID ----------
b = [text(0, 34, "같은 ID를 모든 곳에", 28, TXT, weight="bold")]
for i, (k, v) in enumerate([("광고 링크", "?utm_campaign=BK014"), ("광고 이름", "BK014_dinner-angle_v2"),
                            ("이메일 이름", "BK014_followup"), ("CRM 거래", "campaign: BK014")]):
    y = 60 + i * 74
    b += [rect(0, y, W, 60, LINE, FILL, 3), text(22, y + 39, k, 26, TXT), text(W - 22, y + 39, v, 24, INK, "end", mono=True)]
b += [arrow(444, 362, 444, 412)]
cols = ["ID", "지출", "리드", "거래", "매출", "이탈"]
vals = ["BK014", "$2,000", "41", "6", "$18,000", "0"]
for j, (c, v) in enumerate(zip(cols, vals)):
    x = j * 148
    b += [rect(x, 420, 140, 50, INK, SOFT, 2, 6), text(x + 70, 453, c, 22, INK, "middle", "bold"),
          rect(x, 474, 140, 50, LINE, FILL, 2, 6), text(x + 70, 507, v, 22, TXT, "middle")]
b += [text(0, 570, "한 줄에 놓이면: 어떤 마케팅이 남는 고객을 데려왔나?", 25, INK, weight="bold"),
      text(0, 610, "표의 숫자는 설명을 위한 예시 값", 22, GRAY)]
figs["campaign-id"] = svg(625, "\n".join(b))

# ---------- 회사의 금더미 ----------
b = []
for i, (t, s) in enumerate([("영업", "매주 듣는 반론 다섯 가지"), ("고객 지원", "환불로 이어지는 약속"),
                            ("창업자", "업계에 대한 강한 의견"), ("분석 도구", "오래 남는 고객이 오는 페이지")]):
    x, y = (i % 2) * 468, (i // 2) * 160
    b.append(box(x, y, 420, 140, t, [s]))
b += [rect(0, 350, W, 90, BAD, FILL, 3), text(444, 405, "흩어져 있어서 캠페인에는 분기에 한 번", 28, BAD, "middle", "bold"),
      arrow(444, 448, 444, 500), rect(0, 506, W, 90, INK, SOFT, 4),
      text(444, 561, "마케팅 엔지니어: 오후 한나절에 캠페인으로", 28, INK, "middle", "bold")]
figs["gold"] = svg(600, "\n".join(b))

# ---------- 고객의 말 vs 기능 이름 ----------
b = [box(0, 0, W, 170, "기능 이름으로 쓴 광고", ["\"자동 예약 시스템\""]),
     box(0, 210, W, 210, "고객의 말로 쓴 광고", ["\"저녁 먹다가 전화 받는 거, 이제 그만\"", "영업 통화에서 사장들이 자꾸 하던 말"], True),
     text(0, 480, "고객 언어 에이전트: 통화 20-50개에서 이런 말을 뽑는다", 25, GRAY)]
figs["dinner"] = svg(500, "\n".join(b))

# ---------- 안전장치 ----------
b = [box(0, 0, W, 150, "프롬프트 속 문장", ["\"보내기 전에 꼭 물어봐\" → 공손한 제안일 뿐"]),
     text(0, 200, "도구에 박은 안전장치", 28, INK, weight="bold")]
for i, (t, s) in enumerate([("메일", "초안 쓰기 권한만"), ("광고", "일시정지 상태로만 올린다, 켜는 건 사람"),
                            ("예산", "사람이 쥔다"), ("정확한 규칙", "지출 상한·수신 거부·중복 제거 = 평범한 코드"),
                            ("판단", "맞는 고객인가, 우리 말투인가 = 모델")]):
    y = 224 + i * 80
    b += [rect(0, y, W, 66, INK if i < 3 else LINE, FILL, 3), text(24, y + 43, t, 26, TXT, weight="bold"),
          text(W - 24, y + 43, s, 24, GRAY, "end")]
figs["guard"] = svg(630, "\n".join(b))

# ---------- 주간 루프 ----------
b = []
for i, (d, s) in enumerate([("월", "성과 메모 읽고 유지·중단·변경"), ("화·수", "만들고, 약했던 워크플로 고치고, 새 시험"),
                            ("목", "영업·고객 지원 통화에 들어간다"), ("금", "에이전트가 만든 것 검토, 파일 고치기")]):
    y = i * 104
    b += [rect(0, y, 140, 90, INK, INK, 0), text(70, y + 56, d, 32, FILL, "middle", "bold"),
          rect(156, y, W - 156, 90, LINE, FILL, 3), text(180, y + 56, s, 26, TXT)]
b += [text(0, 470, "하루 종일 결과물을 고치고 있다면? 문제는 위쪽", 26, BAD, weight="bold"),
      text(0, 512, "거의 언제나 두뇌 아니면 지시문", 24, GRAY)]
figs["loop"] = svg(530, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
