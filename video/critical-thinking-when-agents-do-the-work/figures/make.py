#!/usr/bin/env python3
"""비판적 사고 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD, OK = "#3F7A66", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#C0605A", "#4E8F76"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False, opacity=1):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" opacity="{opacity}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, title, lines=(), accent=False, size=32, color=None):
    out = [rect(x, y, w, h, INK if accent else LINE, sw=4 if accent else 3),
           text(x + 24, y + 52, title, size, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 24, y + 102 + i * 50, ln, 26, color or GRAY))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, color=INK, sw=4):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#a)"/>'


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


figs = {}

# 생각할 틈: 예전(긴 틈) vs 지금(몇 초)
b = [text(0, 34, "예전", 30, TXT, weight="bold"),
     rect(0, 56, 150, 70, LINE, SOFT, 2, 12), text(75, 100, "질문", 26, TXT, "middle"),
     rect(738, 56, 150, 70, LINE, SOFT, 2, 12), text(813, 100, "답", 26, TXT, "middle"),
     rect(170, 56, 548, 70, INK, FILL, 3, 12, "10 8"), text(444, 100, "따지고 · 고르고 · 다듬는 틈", 26, INK, "middle", "bold"),
     text(0, 214, "지금", 30, TXT, weight="bold"),
     rect(0, 236, 150, 70, LINE, SOFT, 2, 12), text(75, 280, "질문", 26, TXT, "middle"),
     rect(190, 236, 150, 70, INK, INK, 2, 12), text(265, 280, "답", 26, FILL, "middle", "bold"),
     text(170, 340, "몇 초", 26, BAD, "middle", "bold"),
     text(380, 268, "잘 쓰였고, 대체로 맞다", 26, GRAY), text(380, 306, "→ 다시 볼 이유가 사라진다", 26, INK, weight="bold")]
figs["gap"] = svg(360, "\n".join(b))

# 에이전트 여럿, 눈은 한 쌍
b = []
for i in range(8):
    x, y = (i % 4) * 222, (i // 4) * 120
    b += [rect(x, y, 200, 96, LINE, FILL, 3, 14), text(x + 100, y + 44, f"에이전트 {i + 1}", 24, TXT, "middle", "bold"),
          text(x + 100, y + 78, "결과 도착", 22, OK, "middle")]
for i in range(8):
    x = (i % 4) * 222 + 100
    b.append(f'<line x1="{x}" y1="{(i // 4) * 120 + 96}" x2="444" y2="330" stroke="{LINE}" stroke-width="2"/>')
b += [f'<ellipse cx="404" cy="370" rx="34" ry="22" fill="{FILL}" stroke="{INK}" stroke-width="4"/>',
      f'<ellipse cx="484" cy="370" rx="34" ry="22" fill="{FILL}" stroke="{INK}" stroke-width="4"/>',
      f'<circle cx="404" cy="370" r="10" fill="{INK}"/>', f'<circle cx="484" cy="370" r="10" fill="{INK}"/>',
      text(444, 440, "보는 눈은 한 쌍뿐", 30, INK, "middle", "bold")]
figs["eyes"] = svg(460, "\n".join(b))

# 한 걸음씩 미끄러진다(계단)
steps = [("꼼꼼히 읽는다", "괜찮았다", OK), ("훑어본다", "이번에도 괜찮겠지", GRAY), ("뼈대만 본다", "구조만 맞으면", GRAY),
         ("설명하지 못한다", "에이전트 도움으로도", BAD)]
b = []
for i, (t, s, c) in enumerate(steps):
    x, y = i * 160, i * 118
    b += [rect(x, y, 408, 96, BAD if i == 3 else LINE, FILL, 4 if i == 3 else 3, 14),
          text(x + 22, y + 42, t, 28, BAD if i == 3 else TXT, weight="bold"), text(x + 22, y + 80, s, 22, c)]
    if i < 3:
        b.append(arrow(x + 300, y + 98, x + 340, y + 116, GRAY, 3))
b.append(text(0, 520, "걸음마다 그럴듯해서, 넘어가는 순간이 안 보인다", 26, GRAY))
figs["stairs"] = svg(540, "\n".join(b))

# 세 가지 빚
b = []
for i, (t, who, s) in enumerate([("이해 부채", "제러미 트웨이", "코드는 멀쩡한데 아무도 설명 못 한다"),
                                 ("인지 부채", "마거릿앤 스토리", "팀이 공유하던 이해가 사라진다"),
                                 ("의도 부채", "애디 오스마니", "목표·제약·이유가 산출물 속에 숨는다")]):
    y = i * 160
    b += [rect(0, y, W, 136, INK if i == 0 else LINE, FILL, 4 if i == 0 else 3, 14),
          text(24, y + 52, t, 32, INK if i == 0 else TXT, weight="bold"), text(864, y + 52, who, 22, GRAY, "end"),
          text(24, y + 104, s, 26, GRAY)]
b.append(text(0, 500, "그 순간엔 안 보인다: 코드는 깔끔하고 테스트는 통과", 26, BAD, weight="bold"))
figs["debts"] = svg(520, "\n".join(b))

# 틀려도 싼 일 vs 남이 뒷감당할 일
b = [box(0, 0, 420, 330, "통째로 넘긴다", ["녹화할 호텔 고르기", "평점 비슷한 세 곳", "틀려도 싸다"], False),
     box(468, 0, 420, 330, "추론은 쥐고 있다", ["돈을 어디에 넣을지", "아이 진로 조언", "무엇을 출시할지"], True),
     text(444, 400, "기준: 틀렸을 때 누가 뒷감당하나", 28, INK, "middle", "bold")]
figs["stakes"] = svg(420, "\n".join(b))

# 사각지대 점검: 아는 것 / 모르는 것 2x2
cells = [("아는 줄 아는 것", "모델에게 다 준다", False), ("모르는 줄 아는 것", "질문할 수 있다", False),
         ("아는 줄 모르는 것", "잊고 있던 지식", False), ("모르는 줄 모르는 것", "모델에게 찾게 한다", True)]
b = []
for i, (t, s, acc) in enumerate(cells):
    x, y = (i % 2) * 456, (i // 2) * 190
    b += [rect(x, y, 432, 166, INK if acc else LINE, INK if acc else FILL, 4 if acc else 3, 16),
          text(x + 216, y + 70, t, 30, FILL if acc else TXT, "middle", "bold"), text(x + 216, y + 120, s, 26, FILL if acc else GRAY, "middle")]
b.append(text(444, 420, "사각지대 점검(blind spot pass)", 28, INK, "middle", "bold"))
figs["blindspot"] = svg(440, "\n".join(b))

# 검증 고리
nodes = [("고친다", 444, 60), ("검사한다", 790, 230), ("결과를 읽는다", 444, 400), ("다시 시도", 98, 230)]
b = [f'<circle cx="444" cy="230" r="120" fill="{SOFT}" stroke="none"/>', text(444, 222, "사람은", 26, GRAY, "middle"),
     text(444, 262, "증거를 본다", 28, INK, "middle", "bold")]
for i, (t, x, y) in enumerate(nodes):
    b += [rect(x - 98, y - 40, 196, 80, INK, FILL, 4, 40), text(x, y + 10, t, 26, INK, "middle", "bold")]
b += [arrow(560, 80, 720, 180), arrow(720, 290, 560, 380), arrow(330, 380, 170, 290), arrow(170, 180, 330, 80),
      text(444, 500, "에이전트에게 자기 일을 확인할 방법을 준다", 26, GRAY, "middle")]
figs["loop"] = svg(520, "\n".join(b))

# 600줄 PR: 훑은 곳 vs 숨은 변경
b = [rect(0, 0, 560, 520, LINE, FILL, 3, 12), text(24, 44, "PR #128  +600줄", 26, TXT, weight="bold", mono=True)]
for k in range(16):
    y = 74 + k * 27
    hot = k in (7, 11)
    w = 300 + (k * 53) % 200
    b.append(rect(24, y, w, 14, BAD if hot else LINE, BAD if hot else SOFT, 0, 4))
b += [rect(10, 64, 540, 80, INK, "none", 3, 8, "8 6"), text(600, 104, "훑어본 곳", 26, INK, weight="bold"),
      text(600, 140, "구조 · 변수 이름 · 테스트", 22, GRAY),
      arrow(600, 270, 340, 270, BAD, 3), text(600, 262, "트랜잭션 순서", 24, BAD, weight="bold"),
      arrow(600, 382, 440, 382, BAD, 3), text(600, 374, "뒤집힌 기본값", 24, BAD, weight="bold"),
      text(0, 570, "찾을 줄 알던 것만 찾았다", 28, BAD, weight="bold")]
figs["pr"] = svg(590, "\n".join(b))

# 사람의 머리는 앞과 뒤로
b = [box(0, 0, 260, 250, "앞", ["과제 설명", "맥락 · 범위"], True),
     rect(300, 70, 288, 110, LINE, SOFT, 2, 14), text(444, 136, "에이전트", 30, GRAY, "middle", "bold"),
     box(628, 0, 260, 250, "뒤", ["결과 검토", "증거 확인"], True),
     arrow(262, 125, 296, 125), arrow(592, 125, 624, 125),
     text(444, 320, "가운데를 맡기는 대신, 앞과 뒤가 더 무거워졌다", 26, GRAY, "middle"),
     text(444, 370, "프롬프트 = 내가 문제를 얼마나 이해했나", 28, INK, "middle", "bold")]
figs["frontback"] = svg(390, "\n".join(b))

# 요약의 요약
b = [rect(0, 40, 160, 200, INK, FILL, 4, 10), text(80, 120, "원문", 30, INK, "middle", "bold"), text(80, 170, "50쪽", 24, GRAY, "middle")]
for i, (t, lines) in enumerate([("에이전트 1", "요약 5쪽"), ("에이전트 2", "요약의 요약"), ("에이전트 3", "원문은 못 봄")]):
    x = 196 + i * 236
    hh = 200 - i * 50
    b += [arrow(x - 30, 140, x - 4, 140), rect(x, 140 - hh / 2, 200, hh, BAD if i == 2 else LINE, FILL, 4 if i == 2 else 3, 10),
          text(x + 100, 130, t, 24, BAD if i == 2 else TXT, "middle", "bold"), text(x + 100, 168, lines, 22, GRAY, "middle")]
b.append(text(444, 320, "세 번째 에이전트는 원문을 한 번도 읽지 않았다", 26, BAD, "middle", "bold"))
figs["relay"] = svg(340, "\n".join(b))

# 감독의 역설
b = [rect(0, 60, 380, 160, INK, FILL, 4, 16), text(190, 128, "클로드를 감독하려면", 26, GRAY, "middle"),
     text(190, 178, "코딩 실력이 필요", 32, INK, "middle", "bold"),
     rect(508, 60, 380, 160, BAD, FILL, 4, 16), text(698, 128, "AI를 과하게 쓰면", 26, GRAY, "middle"),
     text(698, 178, "그 실력이 녹슨다", 32, BAD, "middle", "bold"),
     '<path d="M384 110 C 444 40, 444 40, 504 110" fill="none" stroke="#3F7A66" stroke-width="4" marker-end="url(#a)"/>',
     '<path d="M504 170 C 444 240, 444 240, 384 170" fill="none" stroke="#3F7A66" stroke-width="4" marker-end="url(#a)"/>',
     text(444, 310, "감독의 역설(paradox of supervision)", 28, INK, "middle", "bold"),
     text(444, 356, "Anthropic, 자사 엔지니어·연구자 조사", 24, GRAY, "middle")]
figs["paradox"] = svg(380, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
