#!/usr/bin/env python3
"""AI 시대의 커리어 조언 화면용 다이어그램을 SVG 로 그린다. 수치는 모두 설명용 예시(원문 데이터 아님).  python3 make.py"""
import math
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, PALE = "#B0472D", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" {F}>{s}</text>'


def box(x, y, w, h, title, lines=(), accent=False, size=30, tsize=36):
    stroke = INK if accent else LINE
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{FILL}" stroke="{stroke}" stroke-width="{4 if accent else 3}"/>',
           text(x + 26, y + 56, title, tsize, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 26, y + 108 + i * 50, ln, size, GRAY))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label=""):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text((x1 + x2) / 2 + 16, (y1 + y2) / 2 + 10, label, 26, GRAY))
    return "\n".join(out)


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def stack(items, gap=52, top=0):
    """세로로 쌓은 상자들 + 사이 화살표. items: (title, lines, accent)"""
    y, out = top, []
    for i, (t, ls, acc) in enumerate(items):
        h = 92 + 50 * len(ls) + (18 if ls else 0)
        out.append(box(0, y, W, h, t, ls, acc))
        y += h
        if i < len(items) - 1:
            out.append(arrow(W / 2, y + 4, W / 2, y + gap - 4)); y += gap
    return y, "\n".join(out)


figs = {}

# 1. 손실 함수: 채점할 수 있는 일 / 없는 일
b = [text(0, 40, "손실 함수 (loss function)", 36, INK, weight="bold"),
     text(0, 82, "모델의 답이 얼마나 틀렸는지 숫자로 매기는 채점표", 28, GRAY),
     box(0, 112, 420, 330, "채점할 수 있는 일", ["정답이 있는 시험", "코딩 테스트 문제", "기준이 정해진 과제"], size=28),
     text(26, 410, "→ 모델이 따라잡는다", 28, TXT, weight="bold"),
     box(468, 112, 420, 330, "채점할 수 없는 일", ["무엇을 풀지 고르기", "시간·토큰 배분", "관계와 평판"], True, size=28),
     text(494, 410, "→ 사람에게 남는 일", 28, INK, weight="bold"),
     text(0, 500, "단, '훈련 중에는' 채점할 수 없다는 뜻 — 채점표가 생기면 왼쪽으로 옮겨 간다", 25, GRAY)]
figs["t-loss"] = svg(520, "\n".join(b))

# 2. 에이전트 네이티브 회사
b = [text(0, 40, "에이전트 네이티브 (agent-native) 회사", 36, INK, weight="bold")]
h, s = stack([("사람: 무엇을 맡길지 정한다", ["풀 문제를 고르고, 시간과 토큰을 어디에 쓸지 배분"], True),
              ("코딩 에이전트 여럿", ["코드는 에이전트가 쓴다 · 손으로 쓰는 코드는 0줄"], False),
              ("결과를 보고 다음 문제로", ["무엇이 통했는지 판단해 다시 배분"], False)], top=70)
figs["t-agent-native"] = svg(h + 10, "\n".join(b) + s)

# 3. 저자의 경력과 거절한 오퍼
b = [text(0, 40, "필 첸의 6년", 36, INK, weight="bold"), text(240, 40, "직원 15명 회사부터 10만 명 넘는 회사까지", 26, GRAY)]
steps = [("Helm AI", "자율주행 스타트업, 직원 15명"), ("Scale AI", "퀀트 오퍼 대신 선택"), ("Google DeepMind", "프런티어 모델 추론·훈련"),
         ("OpenAI", ""), ("창업", "에이전트 네이티브 스타트업")]
for i, (t, sub) in enumerate(steps):
    y = 90 + i * 110
    b.append(f'<circle cx="24" cy="{y + 20}" r="14" fill="{INK if i == 4 else FILL}" stroke="{INK}" stroke-width="4"/>')
    if i < len(steps) - 1:
        b.append(f'<line x1="24" y1="{y + 36}" x2="24" y2="{y + 104}" stroke="{LINE}" stroke-width="4"/>')
    b.append(text(60, y + 30, t, 32, TXT, weight="bold"))
    if sub:
        b.append(text(60, y + 70, sub, 25, GRAY))
for y, t1, t2 in [(312, "2023 · Anthropic(약 50명)", "Cursor(직원 2명) 오퍼 거절"), (422, "2024 · 두 곳을", "다시 거절")]:
    b.append(f'<rect x="470" y="{y - 40}" width="418" height="96" rx="12" fill="{FILL}" stroke="{INK}" stroke-width="3" stroke-dasharray="10 8"/>')
    b.append(text(490, y, t1, 25, INK, weight="bold")); b.append(text(490, y + 38, t2, 25, INK))
figs["ex-career"] = svg(620, "\n".join(b))

# 4. 정말 희소한 자원
b = [text(0, 40, "무엇이 흔해지고, 무엇이 귀해졌나", 36, INK, weight="bold")]
tiles = [("자본", "어느 때보다 구하기 쉽다", False), ("시간", "사람의 진짜 시간", True), ("관계", "끈끈한 관계", True), ("평판", "이미 보여 준 탁월함", True)]
for i, (big, small, acc) in enumerate(tiles):
    x, y = (i % 2) * (W / 2 + 12), 70 + (i // 2) * 180
    b.append(f'<rect x="{x}" y="{y}" width="{W / 2 - 12}" height="160" rx="14" fill="{FILL if acc else PALE}" stroke="{INK if acc else LINE}" stroke-width="3"/>')
    b.append(text(x + 24, y + 80, big, 56, INK if acc else GRAY, weight="bold"))
    b.append(text(x + 24, y + 128, small, 26, GRAY))
    if not acc:
        b.append(f'<line x1="{x + 20}" y1="{y + 62}" x2="{x + 150}" y2="{y + 62}" stroke="{GRAY}" stroke-width="5"/>')
b.append(text(0, 470, "퀀트 연봉 차이보다 Scale의 네트워크와 배움이 더 컸다는 저자의 회고", 25, GRAY))
figs["ex-scarce"] = svg(490, "\n".join(b))

# 5. 면접의 변화
b = [text(0, 40, "에이전트 시대의 면접", 36, INK, weight="bold"),
     box(0, 70, 420, 300, "예전 면접", ["리트코드 문제", "시스템 설계 질문"], size=28),
     f'<line x1="26" y1="168" x2="220" y2="168" stroke="{GRAY}" stroke-width="4"/>',
     f'<line x1="26" y1="218" x2="250" y2="218" stroke="{GRAY}" stroke-width="4"/>',
     text(26, 330, "실제 성과와 상관이 없다", 26, GRAY),
     box(468, 70, 420, 300, "지금 면접", ["① 낯선 환경 빨리 이해", "② 풀 가치 있는 문제 찾기", "③ 제약 안에서 실제로 풀기"], True, size=28)]
figs["ex-interview"] = svg(390, "\n".join(b))

# 6. 같은 문제, 다른 비용 (예시)
b = [text(0, 40, "같은 문제, 다른 비용", 36, INK, weight="bold"), text(340, 40, "답에 이르는 시간과 토큰 (예시)", 26, GRAY)]
rows = [("지원자 A", 0.28, "직관 + 바깥 맥락"), ("지원자 B", 0.55, ""), ("지원자 C", 0.78, ""), ("지원자 D", 1.0, "에이전트에게 통째로")]
for i, (lab, v, note) in enumerate(rows):
    y = 80 + i * 92
    b.append(text(0, y + 40, lab, 28, TXT))
    b.append(f'<rect x="150" y="{y + 10}" width="{W - 150}" height="44" rx="8" fill="{PALE}"/>')
    b.append(f'<rect x="150" y="{y + 10}" width="{int((W - 150) * v)}" height="44" rx="8" fill="{INK if i == 0 else LINE}"/>')
    if note:
        b.append(text(150 + int((W - 150) * v) + 14 if v < 0.6 else 166, y + 42, note, 24, GRAY if v < 0.6 else FILL, weight="bold"))
b.append(text(0, 470, "에이전트가 같아도 문제를 어떻게 나눠 맡기느냐에서 차이가 난다", 26, TXT))
figs["ex-tokens"] = svg(490, "\n".join(b))

# 7. 쓴 교훈 (개형)
x0, y0, xw, yh = 70, 420, W - 80, 340
b = [text(0, 36, "쓴 교훈 (The Bitter Lesson)", 36, INK, weight="bold"),
     f'<line x1="{x0}" y1="{y0}" x2="{W}" y2="{y0}" stroke="{LINE}" stroke-width="3"/>', f'<line x1="{x0}" y1="70" x2="{x0}" y2="{y0}" stroke="{LINE}" stroke-width="3"/>',
     text(x0 + xw / 2, y0 + 44, "계산 규모 →", 27, GRAY, "middle"), text(0, 96, "성능", 27, GRAY)]
gen = " ".join(f"{x0 + t * xw:.0f},{y0 - (0.08 + 0.85 * t ** 1.6) * yh:.0f}" for t in [i / 30 for i in range(31)])
spec = " ".join(f"{x0 + t * xw:.0f},{y0 - (0.32 + 0.2 * (1 - math.exp(-6 * t))) * yh:.0f}" for t in [i / 30 for i in range(31)])
b += [f'<polyline points="{spec}" fill="none" stroke="{GRAY}" stroke-width="4"/>',
      f'<polyline points="{gen}" fill="none" stroke="{INK}" stroke-width="6"/>',
      text(W - 6, y0 - 0.52 * yh + 40, "과제별로 공들인 방법", 25, GRAY, "end"),
      text(W - 250, 90, "범용 방법을 키우기", 26, INK, "end", "bold"),
      text(0, y0 + 96, "리치 서튼, 2019 · 개형만 그린 그림", 24, GRAY)]
figs["t-bitter"] = svg(y0 + 110, "\n".join(b))

# 8. 멱법칙 분포 (예시)
b = [text(0, 36, "멱법칙 (power law)", 36, INK, weight="bold"), text(330, 36, "소수가 대부분을 가져가는 분포 (예시)", 26, GRAY)]
n, base, top = 20, 400, 300
vals = [1 / (k + 1) ** 1.3 for k in range(n)]
bw = (W - 20) / n
for k, v in enumerate(vals):
    hgt = v * top
    b.append(f'<rect x="{10 + k * bw:.0f}" y="{base - hgt:.0f}" width="{bw - 8:.0f}" height="{hgt:.0f}" rx="4" fill="{INK if k < 2 else LINE}"/>')
share = sum(vals[:2]) / sum(vals)
b += [f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{LINE}" stroke-width="3"/>',
      text(10 + 2 * bw + 20, base - vals[1] * top + 10, f"상위 10%가 전체의 약 {share * 100:.0f}%", 28, INK, weight="bold"),
      text(0, base + 44, "회사·커리어의 결과 순위 →", 26, GRAY),
      text(0, base + 96, "AI로 단순한 것은 누구나 만들게 되면서 쏠림이 더 가팔라졌다", 26, TXT)]
figs["ex-powerlaw"] = svg(base + 116, "\n".join(b))

# 9. 마지막 10%
b = [text(0, 40, "마지막 10%가 일의 90%, 보상의 90%", 36, INK, weight="bold")]
rows = [("진척", 0.9, "처음 90%", "마지막 10%"), ("드는 노력", 0.1, "", "90%"), ("보상", 0.1, "", "90%")]
for i, (lab, cut, l1, l2) in enumerate(rows):
    y = 90 + i * 120
    b.append(text(0, y, lab, 28, TXT, weight="bold"))
    b.append(f'<rect x="0" y="{y + 16}" width="{int(W * cut) - 4}" height="56" rx="8" fill="{LINE}"/>')
    b.append(f'<rect x="{int(W * cut)}" y="{y + 16}" width="{W - int(W * cut)}" height="56" rx="8" fill="{INK}"/>')
    if l1:
        b.append(text(20, y + 54, l1, 26, TXT, weight="bold"))
    if cut < 0.5:
        b.append(text(int(W * cut) + 14, y + 54, l2, 26, FILL, weight="bold"))
    else:
        b.append(text(W, y, l2 + " ↓", 26, INK, "end", "bold"))
b += [text(0, 470, "처음 90%까지는 이제 에이전트가 거의 공짜로 데려다준다", 27, TXT),
      text(0, 512, "앨프리드 린, 〈The Last 10%〉", 24, GRAY)]
figs["ex-last10"] = svg(532, "\n".join(b))

# 10. 중간값이 된 결과물
x0, base, wid = 0, 360, W
pts = []
for i in range(81):
    t = i / 80
    v = math.exp(-((math.log(t * 6 + 0.05) - 0.9) ** 2) / 0.35)
    pts.append((x0 + t * wid, base - v * 250))
poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
tail = [(x, y) for x, y in pts if x >= 0.72 * W]
tailpoly = " ".join(f"{x:.0f},{y:.0f}" for x, y in [(tail[0][0], base)] + tail + [(tail[-1][0], base)])
med = 0.38 * W
b = [text(0, 40, "대충 쓴 프롬프트의 결과 = 중간값", 36, INK, weight="bold"),
     f'<polygon points="{tailpoly}" fill="{INK}" opacity="0.85"/>',
     f'<polyline points="{poly}" fill="none" stroke="{TXT}" stroke-width="4"/>',
     f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{LINE}" stroke-width="3"/>',
     f'<line x1="{med}" y1="80" x2="{med}" y2="{base}" stroke="{GRAY}" stroke-width="3" stroke-dasharray="10 8"/>',
     text(med + 14, 100, "누구나 받는 결과", 26, GRAY),
     text(W - 4, base - 210, "고유한 관점", 27, INK, "end", "bold"), text(W - 4, base - 172, "세부에 대한 집요함", 27, INK, "end", "bold"),
     text(0, base + 44, "결과물의 품질 →", 26, GRAY),
     text(0, base + 96, "가치는 중간값이 아니라 오른쪽 꼬리에서 나온다 (개형)", 26, TXT)]
figs["ex-median"] = svg(base + 116, "\n".join(b))

# 11. xG 슈팅 지도 (예시 경기)
s = 12.5                                          # px per m
gx = W / 2
b = [text(0, 40, "xG: 기회 하나하나가 골이 될 확률", 36, INK, weight="bold")]
py = 80
pitch_h = 30 * s
box_w, box_d, ga_w, ga_d, goal_w = 40.3 * s, 16.5 * s, 18.32 * s, 5.5 * s, 7.32 * s
b += [f'<rect x="20" y="{py}" width="{W - 40}" height="{pitch_h}" fill="#EEF2EA" stroke="{LINE}" stroke-width="3"/>',
      f'<rect x="{gx - box_w / 2}" y="{py}" width="{box_w}" height="{box_d}" fill="none" stroke="{GRAY}" stroke-width="3"/>',
      f'<rect x="{gx - ga_w / 2}" y="{py}" width="{ga_w}" height="{ga_d}" fill="none" stroke="{GRAY}" stroke-width="3"/>',
      f'<rect x="{gx - goal_w / 2}" y="{py - 16}" width="{goal_w}" height="16" fill="{TXT}"/>',
      f'<circle cx="{gx}" cy="{py + 11 * s}" r="4" fill="{GRAY}"/>']
shots = [(0, 11, 0.76, True, "페널티킥 0.76", "end"), (-7, 2.5, 0.45, True, "골문 앞 0.45", "below"), (9, 7, 0.20, False, "헤더 0.20", "below"),
         (-17, 19, 0.08, False, "측면 0.08", "start"), (10, 23, 0.03, False, "중거리 0.03", "start")]
for dx, dy, xg, goal, lab, anchor in shots:
    cx, cy = gx + dx * s, py + dy * s
    r = 12 + 30 * math.sqrt(xg)
    b.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{INK if goal else FILL}" stroke="{INK}" stroke-width="3" opacity="{0.9 if goal else 1}"/>')
    lx = cx + r + 10 if anchor == "start" else cx - r - 10
    if anchor == "below":
        b.append(text(f"{cx:.0f}", f"{cy + r + 30:.0f}", lab, 24, TXT, "middle")); continue
    b.append(text(f"{lx:.0f}", f"{cy + 9:.0f}", lab, 24, TXT, anchor))
total = sum(x[2] for x in shots)
y2 = py + pitch_h + 56
b += [f'<circle cx="34" cy="{y2 - 9}" r="14" fill="{INK}"/>', text(58, y2, "골", 26, TXT),
      f'<circle cx="124" cy="{y2 - 9}" r="14" fill="{FILL}" stroke="{INK}" stroke-width="3"/>', text(148, y2, "실패", 26, TXT),
      text(0, y2 + 54, f"기대 득점 xG = 0.76 + 0.45 + 0.20 + 0.08 + 0.03 = {total:.2f}", 27, TXT, weight="bold"),
      text(0, y2 + 100, f"실제 2골 → 결정력: 기대({total:.2f})보다 많이 넣었다", 27, INK, weight="bold"),
      text(0, y2 + 144, "예시 경기 · 수치는 설명용", 24, GRAY)]
figs["t-xg"] = svg(y2 + 164, "\n".join(b))

# 12. xG와 결정력을 커리어로
b = [text(0, 40, "커리어로 옮기면", 36, INK, weight="bold"),
     box(0, 70, 420, 270, "xG 높이기", ["기회가 보이는 자리에 서기", "← 평판", "← 관심 문제에 쏟은 시간"], size=27),
     box(468, 70, 420, 270, "결정력 높이기", ["온 기회를 골로 바꾸기", "← 판단의 질", "← 결정 전 데이터 모으기"], True, size=27),
     text(0, 396, "저자의 반성은 오른쪽: 데이터를 더 모았으면 좋았겠다", 27, TXT)]
figs["t-xg-career"] = svg(416, "\n".join(b))

# 13. 직관을 평가로 증류
h, s2 = stack([("모델을 직접 써 보며 생긴 직관", ["\"이 모델은 이런 문제에서 자꾸 틀린다\""], False),
               ("평가 (eval)로 증류", ["문제 묶음 + 채점 기준 = 숫자로 잴 수 있게"], True),
               ("채점할 수 있게 된 일", ["이제 모델이 배울 수 있다 — 경계를 사람이 먼저 옮긴다"], False)], top=70)
figs["t-eval"] = svg(h + 10, text(0, 40, "직관을 평가로 증류한다", 36, INK, weight="bold") + s2)

# 14. 연구자의 일
b = [text(0, 40, "연구자는 직업이 아니라 태도", 36, INK, weight="bold")]
tiles = [("호기심", "새 아이디어 탐색"), ("인프라 씨름", "아이디어를 실제로 구현"), ("디버깅", "전체 시스템을 세밀히 이해"), ("설득", "컴퓨트를 따내려 가치 설명")]
for i, (big, small) in enumerate(tiles):
    x, y = (i % 2) * (W / 2 + 12), 70 + (i // 2) * 180
    b.append(f'<rect x="{x}" y="{y}" width="{W / 2 - 12}" height="160" rx="14" fill="{FILL}" stroke="{INK if i == 0 else LINE}" stroke-width="3"/>')
    b.append(text(x + 24, y + 76, big, 46, INK, weight="bold"))
    b.append(text(x + 24, y + 126, small, 26, GRAY))
b.append(text(0, 470, "넷 다 프런티어 랩 밖에서도 할 수 있다", 27, TXT))
figs["t-research"] = svg(490, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
