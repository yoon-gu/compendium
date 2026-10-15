#!/usr/bin/env python3
"""해자 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#7A2E3A", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
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

WATER = "#8FB3C9"

# ---------- 배경 ----------
# 해자: 성과 물길, 예전의 다섯 해자
b = [f'<rect x="0" y="0" width="{W}" height="300" rx="20" fill="{WATER}" opacity="0.35"/>',
     rect(294, 50, 300, 200, INK, FILL, 4, 8)]
for i in range(5):
    b.append(f'<rect x="{304 + i * 60}" y="22" width="40" height="34" fill="{INK}"/>')
b += [text(444, 165, "성 = 회사", 32, INK, "middle", "bold"), text(80, 290, "해자 = 물길", 26, "#2F5A73", weight="bold"),
      text(0, 360, "소프트웨어 회사가 믿어 온 다섯 해자", 28, TXT, weight="bold")]
for i, m in enumerate(["쌓아 온 기능", "손에 익은 화면", "독자 파일 형식", "수많은 연동", "좌석 과금"]):
    x, y = (i % 3) * 296, 390 + (i // 3) * 74
    b += [rect(x, y, 276, 58, LINE, SOFT, 2, 10), text(x + 138, y + 38, m, 24, TXT, "middle")]
figs["t-moat"] = svg(540, "\n".join(b))

# PhotoCraft
b = [box(0, 0, 420, 250, "PhotoCraft", ["Rust로 다시 구현", "데스크톱 + 브라우저", "GitHub 별 수천 개 / 1주"], True),
     box(468, 0, 420, 250, "열린 문", ["PSD: 공개 명세로 파싱", "모든 명령: CLI·MCP", "→ 에이전트가 조작"]),
     text(0, 310, "Photoshop 대비 기능 수준(추정)", 26, TXT, weight="bold"),
     bar(0, 330, 760, 36, 0.47), text(W, 360, "절반 이하", 24, INK, "end", "bold"),
     text(0, 410, "형제 프로젝트: Premiere · Lightroom · InDesign · Word", 24, GRAY)]
figs["ex-photocraft"] = svg(430, "\n".join(b))

# 핵심 원리
h, b = stack([("① 사용자가 관찰한다", ["화면, 메뉴, 파일, 동작"], False),
              ("② 명세가 된다", ["공개 문서 + 관찰한 동작"], False),
              ("③ 다시 만들어진다", ["에이전트를 쓰는 작은 팀, 몇 주"], True)])
figs["t-principle"] = svg(h, b)

# 주가
b = [text(0, 34, "좌석 과금 소프트웨어 주가 (저자 인용)", 28, TXT, weight="bold")]
for i, (name, v, note_) in enumerate([("Thomson Reuters", 18, "하루"), ("Atlassian", 50, "4월까지, 연초 대비"), ("Adobe", 30, "연초 대비, 실적은 호조")]):
    y = 70 + i * 120
    b += [text(0, y + 30, name, 28, TXT, weight="bold"), text(W, y + 30, f"-{v}%" + ("+" if name == "Atlassian" else ""), 30, BAD, "end", "bold"),
          bar(0, y + 46, 700, 30, v / 60, BAD), text(0, y + 104, note_, 22, GRAY)]
b += [text(0, 450, "계기: 2월, 업무용 에이전트 플러그인 출시", 24, GRAY)]
figs["ex-stocks"] = svg(470, "\n".join(b))

# 버티는 해자
b = []
for i, (t, sub) in enumerate([("책임", "인가 · 감사 · 인증 · 보험"), ("살아 있는 데이터", "운영이 계속 만드는 데이터"),
                              ("신뢰와 유통", "보안 심사, 이미 회사 안에"), ("물리 세계", "창고 · 설치 · 차량")]):
    x, y = (i % 2) * 468, (i // 2) * 200
    b.append(box(x, y, 420, 170, t, [sub], i == 0))
b += [text(0, 450, "생태계·네트워크 효과도 버티지만 가장자리부터 깎인다", 24, GRAY)]
figs["ex-hold"] = svg(470, "\n".join(b))

# 창업자에게
b = []
for i, (t, sub) in enumerate([("화면 테스트", "가치가 다 보이면 복제된다고 가정"), ("얻기 어려운 자리", "규제 틈새, 운영이 무거운 사업"),
                              ("클라이언트는 오픈소스", "데이터·컴플라이언스·서비스는 지킨다"), ("과금 다시 보기", "좌석 → 끝낸 일, 회수한 돈"),
                              ("유통이 먼저", "좁은 시장의 깊은 신뢰")]):
    y = i * 104
    b += [rect(0, y, W, 90, INK if i == 0 else LINE, FILL, 4 if i == 0 else 3), text(28, y + 40, f"{i + 1}. {t}", 28, TXT, weight="bold"),
          text(28, y + 76, sub, 22, GRAY)]
figs["ex-founders"] = svg(520, "\n".join(b))

# Adobe
b = [text(0, 34, "Adobe 3분기 (저자 인용)", 28, TXT, weight="bold")]
for i, (lab, val) in enumerate([("매출", "67.6억 달러, +13%"), ("AI 연간 반복 매출", "6.5억 달러+, +150%+"), ("주가", "연초 대비 약 -30%")]):
    y = 60 + i * 80
    b += [rect(0, y, W, 66, BAD if i == 2 else LINE, FILL, 3), text(24, y + 43, lab, 26, TXT), text(860, y + 43, val, 26, BAD if i == 2 else INK, "end", "bold")]
b += [box(0, 320, 420, 170, "약한 곳", ["월 20-60달러 개인·소상공인"]),
      box(468, 320, 420, 170, "버티는 곳", ["기업 고객: 면책·지원"], True)]
figs["ex-adobe"] = svg(500, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
