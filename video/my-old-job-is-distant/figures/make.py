#!/usr/bin/env python3
"""예전의 내 일 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#6B4E2E", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
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

# ---------- 탭 완성 vs 에이전트 코딩 ----------
b = [box(0, 0, 420, 330, "탭 완성", ["다음 한두 줄", "회색 글씨로 제안", "탭 키로 받는다", "주도권: 개발자"]),
     box(468, 0, 420, 330, "에이전트 코딩", ["기능 하나, 파일 여러 개", "말로 맡긴다", "읽고·고치고·테스트", "개발자: 맡기고 검토"], True),
     rect(0, 370, W, 90, INK, SOFT, 3), text(444, 426, "쓰는 사람 → 맡기고 검토하는 사람", 30, INK, "middle", "bold")]
figs["tab-vs-agent"] = svg(470, "\n".join(b))

# ---------- 배우면서 만들기 ----------
h, b = stack([("묻는다", ["파이썬 컴퓨터 비전을 몰랐다"], False),
              ("배우면서 만든다", ["노트북에서 바로 돌려 본다"], False),
              ("엉뚱한 답", ["= 모델의 지식이 끝나는 경계"], True)])
b += text(444, h + 50, "통제권을 내준 때가 아니라, 오염된 검색과 부실한 문서를 건너뛴 때", 23, GRAY, "middle")
figs["cv"] = svg(h + 70, b)

# ---------- 리뷰: 훑기 vs 정독 ----------
b = [text(0, 34, "생산성 약 3배 → 읽을 코드도 3배", 28, BAD, weight="bold"),
     box(0, 70, 420, 300, "훑는다", ["표준 라이브러리", "컴포넌트", "익숙한 패턴", "(틀려도 피해가 작다)"]),
     box(468, 70, 420, 300, "정독한다", ["회사만의 규칙", "고객 데이터", "DB 변경 · 암호화", "(되돌리기 어렵다)"], True)]
figs["review"] = svg(380, "\n".join(b))

# ---------- 갈아탔다 돌아오다 ----------
b = []
for i, (t, s1, s2, acc) in enumerate([("Opus 5", "고칠 일은 줄었다", "대신 비용↑ · 말이 많아짐", False),
                                      ("ChatGPT로", "코딩 실력은 비슷", "더 싸고 덜 장황", False),
                                      ("다시 Claude로", "모델이 다시 비슷하거나 더 나음", "OpenAI 불신은 숨기지 않는 편향", True)]):
    y = i * 150
    b += [rect(0, y, W, 130, INK if acc else LINE, FILL, 4 if acc else 3), text(26, y + 46, t, 30, INK, weight="bold"),
          text(26, y + 88, s1, 24, TXT), text(26, y + 120, s2, 22, GRAY)]
    if i < 2:
        b.append(arrow(444, y + 132, 444, y + 148))
figs["switch"] = svg(440, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
