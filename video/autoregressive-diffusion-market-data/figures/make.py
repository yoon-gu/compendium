#!/usr/bin/env python3
"""자기회귀 확산으로 시장 데이터 생성하기 — 화면용 다이어그램을 SVG 로 직접 그린다.
원문(Jane Street) 그림은 가져오지 않았다. 원문 수치를 옮긴 그림에는 '원문 그림을 바탕으로 다시 그림'을, 지어낸 예시에는 그렇다고 적는다.

    python3 make.py
"""
import math
import random
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT = "#2F6B4F", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
WARN, ORANGE = "#A23B3B", "#C8742B"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, title, lines=(), accent=False, size=34, lsize=28):
    out = [rect(x, y, w, h, INK if accent else LINE, sw=4 if accent else 3),
           text(x + 26, y + 54, title, size, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 26, y + 106 + i * 50, ln, lsize, GRAY))
    return "\n".join(out)


def line(x1, y1, x2, y2, color=LINE, sw=3, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>'


def arrow(x1, y1, x2, y2, label="", color=INK, lx=None, ly=None, anchor="start"):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text(lx if lx is not None else (x1 + x2) / 2 + 16, ly if ly is not None else (y1 + y2) / 2 + 10, label, 25, GRAY, anchor))
    return "\n".join(out)


def poly(pts, color=INK, sw=4, fill="none", dash="", close=False):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    tag = "polygon" if close else "polyline"
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<{tag} points="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"{dd}/>'


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def npdf(z, mu=0.0, s=1.0):
    return math.exp(-0.5 * ((z - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


figs = {}

# ---------- 배경: 호가창 ----------
b = [text(0, 30, "한 종목의 호가창 (지어낸 예시)", 26, GRAY)]
rows = [("매도", "170.05", 200, False), ("매도", "170.04", 120, False), ("매도", "170.03", 300, True),
        ("매수", "170.01", 500, True), ("매수", "170.00", 260, False), ("매수", "169.99", 380, False)]
for i, (side, price, size, best) in enumerate(rows):
    y = 50 + i * 66 + (64 if i >= 3 else 0)
    b += [rect(0, y, 520, 56, INK if best else LINE, FILL if best else SOFT, 4 if best else 2, 8),
          text(18, y + 38, side, 24, GRAY), text(80, y + 39, price, 28, TXT, mono=True),
          f'<rect x="200" y="{y + 14}" width="{size * 0.5:.0f}" height="28" rx="4" fill="{INK if side == "매수" else WARN}" opacity="0.55"/>',
          text(210 + size * 0.5, y + 38, str(size), 24, GRAY)]
b += [text(260, 268, "스프레드 = 170.03 − 170.01 = 0.02", 24, INK, "middle", "bold"),
      text(530, 233, "최우선", 22, INK, weight="bold"), text(530, 370, "최우선", 22, INK, weight="bold")]
for i, (t, sub) in enumerate([("주문", "가격에 걸어 둔다"), ("취소", "걸어 둔 걸 뺀다"), ("체결", "사고팔 가격이 맞는다")]):
    y = 50 + i * 150
    b += [rect(612, y, 276, 124, LINE), text(636, y + 50, t, 32, TXT, weight="bold"), text(636, y + 96, sub, 24, GRAY)]
b += [text(0, 560, "BBO = 가장 높은 매수 호가 + 가장 낮은 매도 호가", 27, TXT)]
figs["t-orderbook"] = svg(580, "\n".join(b))

# ---------- 배경: 이벤트 기록 ----------
cols = [(20, "시각"), (330, "종류"), (550, "가격"), (730, "잔량")]
data = [("09:30:00.000118", "BBO 변화", "170.03", "300", True),
        ("09:30:00.000118", "BBO 변화", "170.01", "500", True),
        ("09:30:00.004270", "체결", "170.03", "100", False),
        ("09:30:00.004301", "주문", "170.02", "200", False),
        ("09:30:01.000002", "취소", "170.00", "400", False)]
b = [rect(0, 0, W, 64, LINE, SOFT, 0, 8)] + [text(x, 42, c, 26, GRAY, weight="bold") for x, c in cols]
for i, (t, k, p, s, hl) in enumerate(data):
    y = 64 + i * 66
    b += [line(0, y + 66, W, y + 66, LINE, 2),
          text(20, y + 44, t, 26, INK if hl else TXT, mono=True, weight="bold" if hl else "normal"),
          text(330, y + 44, k, 26), text(550, y + 44, p, 26, mono=True), text(730, y + 44, s, 26, mono=True)]
b += [text(0, 450, "같은 시각에 두 줄 → 직전 이벤트와의 간격 0초", 27, INK, weight="bold"),
      text(0, 494, "(지어낸 예시) 실제 데이터는 미국 주식 4년치", 25, GRAY)]
figs["ex-events"] = svg(510, "\n".join(b))

# ---------- 연속인가 이산인가 ----------
b = ['<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#1E1E1C"/><stop offset="1" stop-color="#F4F4F1"/></linearGradient></defs>']
for i, (t, acc) in enumerate([("영상", False), ("텍스트", False), ("시장 데이터", True)]):
    x = i * 304
    b += [rect(x, 0, 280, 400, INK if acc else LINE, sw=4 if acc else 3), text(x + 22, 52, t, 32, INK if acc else TXT, weight="bold")]
b += ['<rect x="22" y="90" width="236" height="90" rx="6" fill="url(#g)"/>',
      text(22, 230, "밝기·색이", 26, GRAY), text(22, 270, "매끈하게 이어진다", 26, GRAY), text(22, 360, "연속", 34, TXT, weight="bold")]
for j, tok in enumerate(["시장", "데이터", "는"]):
    b += [rect(326 + j * 80 - (0 if j < 2 else 0), 104, 72, 60, LINE, SOFT, 2, 6), text(362 + j * 80, 144, tok, 22, TXT, "middle")]
b += [text(326, 230, "토큰이 하나씩", 26, GRAY), text(326, 270, "이어진다", 26, GRAY), text(326, 360, "이산", 34, TXT, weight="bold")]
for j, (k, v) in enumerate([("행동", "이산"), ("가격", "거의 연속"), ("시각", "연속")]):
    b += [text(630, 120 + j * 56, k, 26, GRAY), text(700, 120 + j * 56, v, 26, TXT, weight="bold")]
b += [text(630, 360, "둘 다", 34, INK, weight="bold")]
figs["ex-video-text"] = svg(400, "\n".join(b))

# ---------- 뾰족한 분포 ----------
b = [text(0, 34, "가격 개선 폭", 30, TXT, weight="bold"), text(468, 34, "주문 도착 시각", 30, TXT, weight="bold")]
base = 360
for i, (lab, v) in enumerate([("1틱", 280), ("2틱", 64), ("3틱", 34), ("4틱", 20), ("5틱", 12)]):
    x = 10 + i * 82
    b += [f'<rect x="{x}" y="{base - v}" width="58" height="{v}" rx="4" fill="{INK if i == 0 else LINE}"/>', text(x + 29, base + 36, lab, 24, GRAY, "middle")]
b += [line(0, base, 420, base, TXT, 2), line(468, base, W, base, TXT, 2)]
pts = [(470 + k * 4, base - 24 - 10 * math.sin(k / 9)) for k in range(104)]
b.append(poly(pts + [(882, base), (470, base)], LINE, 2, SOFT, close=True))
for s, h in [(0, 270), (1, 150), (2, 120), (3, 100)]:
    x = 476 + s * 120
    b += [f'<rect x="{x - 7}" y="{base - h}" width="14" height="{h}" rx="3" fill="{INK}"/>', text(x, base + 36, f"{s}초", 24, GRAY, "middle")]
b += [text(0, 440, "한 점에 확률이 몰린다: 1틱 개선(pennying), 0초, 정수 초", 26, TXT),
      text(0, 480, "(경향을 보여 주려고 그린 예시)", 24, GRAY)]
figs["ex-spiky"] = svg(495, "\n".join(b))

# ---------- 확산 모델 ----------
b = []
alphas = [1.0, 0.55, 0.15, 0.0]
for i, a in enumerate(alphas):
    x0 = i * 228
    b.append(rect(x0, 70, 204, 230, INK if i in (0, 3) else LINE, FILL, 3, 10))
    pts = []
    for k in range(181):
        z = -3.2 + 6.4 * k / 180
        dens = 0.5 * npdf(z, math.sqrt(a) * -1.1, math.sqrt(a * 0.15 ** 2 + 1 - a)) + 0.5 * npdf(z, math.sqrt(a) * 1.0, math.sqrt(a * 0.3 ** 2 + 1 - a))
        pts.append((x0 + 12 + 180 * k / 180, 285 - min(dens, 1.4) * 140))
    b.append(poly(pts, INK if i == 0 else (TXT if i == 3 else GRAY), 4))
for i, lab in enumerate(["데이터", "", "", "순수 노이즈"]):
    if lab:
        b.append(text(i * 228 + 102, 340, lab, 26, TXT, "middle", "bold"))
b += [arrow(20, 30, 860, 30, color=GRAY), text(444, 22, "학습: 노이즈를 조금씩 섞는다", 26, GRAY, "middle"),
      f'<line x1="860" y1="380" x2="20" y2="380" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>',
      text(444, 424, "생성: 노이즈에서 출발해 조금씩 걷어 낸다", 28, INK, "middle", "bold")]
figs["t-diffusion"] = svg(440, "\n".join(b))

# ---------- 모델 구조 ----------
b = []
for i, t in enumerate(["이벤트 1", "이벤트 2", "이벤트 3", "…", "이벤트 t"]):
    x = i * 180
    b += [rect(x, 0, 156, 60, LINE, SOFT, 2, 8), text(x + 78, 40, t, 24, TXT, "middle")]
b += [arrow(444, 66, 444, 104), rect(0, 110, W, 96, TXT, FILL, 3, 12),
      text(444, 152, "트랜스포머 인코더", 32, TXT, "middle", "bold"), text(444, 190, "인과 마스크: 미래 이벤트는 보지 않는다", 24, GRAY, "middle"),
      arrow(444, 212, 444, 250), rect(304, 256, 280, 60, INK, SOFT, 3, 30), text(444, 296, "잠재 벡터 h", 28, INK, "middle", "bold"),
      arrow(330, 316, 210, 366), arrow(558, 316, 678, 366),
      box(0, 372, 400, 200, "이벤트 종류 헤드", ["범주로 뽑는다", "체결 / BBO 변화"], size=30, lsize=26),
      box(488, 372, 400, 200, "확산 헤드", ["가격, 경과 시간 …", "조건: h + 종류 (AdaLN)"], True, size=30, lsize=26),
      arrow(404, 520, 482, 520), text(443, 506, "종류", 22, GRAY, "middle")]
figs["ex-arch"] = svg(580, "\n".join(b))

# ---------- DDPM 오차 증폭 ----------
b = [text(0, 34, "노이즈 예측을 0.1 틀렸을 때 깨끗한 값 추정의 오차", 27, TXT, weight="bold"),
     box(0, 64, W, 160, "노이즈가 절반쯤 걷힌 단계", ["ᾱ = 0.25  →  √ᾱ = 0.5  →  배율 1.7"], size=30),
     text(860, 190, "0.17", 56, TXT, "end", "bold"),
     box(0, 252, W, 160, "노이즈가 거의 전부인 초반", ["ᾱ = 0.0001  →  √ᾱ = 0.01  →  배율 100"], True, size=30),
     text(860, 350, "10", 60, WARN, "end", "bold"), text(860, 392, "표준편차 10배", 22, WARN, "end"),
     text(0, 466, "배율 = √(1 − ᾱ) ÷ √ᾱ   (예시 값으로 계산)", 26, GRAY)]
figs["ex-amplify"] = svg(480, "\n".join(b))

# ---------- flow matching 한 걸음 ----------
X = lambda v: 60 + v * 320
b = [text(0, 34, "노이즈 0.3, 데이터 2.0  →  속도 v = 2.0 − 0.3 = 1.7", 28, TXT, weight="bold"),
     line(40, 180, 860, 180, TXT, 3)]
for v in [0, 0.5, 1, 1.5, 2]:
    b += [line(X(v), 172, X(v), 188, TXT, 2), text(X(v), 222, f"{v:g}", 22, GRAY, "middle")]
for a, c in [(0.3, 1.15), (1.15, 2.0)]:
    mx = (X(a) + X(c)) / 2
    b.append(f'<path d="M{X(a)} 166 Q{mx} 90 {X(c) - 6} 162" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>')
    b.append(text(mx, 98, "+0.5 × 1.7", 24, INK, "middle", "bold"))
b += [f'<circle cx="{X(0.3)}" cy="180" r="13" fill="{GRAY}"/>', f'<circle cx="{X(1.15)}" cy="180" r="11" fill="{INK}" opacity="0.6"/>',
      f'<circle cx="{X(2.0)}" cy="180" r="14" fill="{INK}"/>',
      text(X(0.3), 262, "0.3", 26, GRAY, "middle", "bold"), text(X(1.15), 262, "1.15", 26, INK, "middle", "bold"), text(X(2.0), 262, "2.0", 26, INK, "middle", "bold"),
      text(0, 320, "x ← x + Δt · v  (Δt = 0.5, 두 걸음)", 27, TXT, mono=True),
      text(0, 364, "나누는 곳이 없으니 오차가 부풀려질 곳도 없다", 27, INK, weight="bold")]
figs["ex-flowstep"] = svg(380, "\n".join(b))

# ---------- 8σ 밖 비율 ----------
rows = [("DDIM 100단계, η=0", 94.5), ("DDIM 100단계, η=1", 88.0), ("DDIM 1,000단계, η=0", 9.7),
        ("DDIM 1,000단계, η=1", 0.5), ("flow matching 50단계", 0.0)]
b = [text(0, 34, "매도 잔량을 생성할 때 8σ 밖으로 나간 비율", 28, TXT, weight="bold")]
for i, (lab, v) in enumerate(rows):
    y = 70 + i * 78
    fm = i == 4
    b += [text(0, y + 40, lab, 26, INK if fm else TXT, weight="bold" if fm else "normal"),
          rect(330, y + 10, 440, 44, LINE, SOFT, 0, 6)]
    if v > 0:
        b.append(f'<rect x="330" y="{y + 10}" width="{max(4, 4.4 * v):.0f}" height="44" rx="6" fill="{WARN if v > 50 else GRAY}"/>')
    b.append(text(330 + max(4, 4.4 * v) + 12 if v < 80 else 318 + 4.4 * v, y + 42, f"{v:.1f}%" if not fm else "0.00%", 26,
                  FILL if v >= 80 else (INK if fm else TXT), "end" if v >= 80 else "start", "bold"))
b += [text(0, 494, "ε 예측은 1,000단계에 무작위성(η=1)까지 더해야 0.5%", 25, GRAY),
      text(0, 532, "원문 그림을 바탕으로 다시 그림", 24, GRAY)]
figs["ex-overflow"] = svg(548, "\n".join(b))

# ---------- 칼날 같은 분포 ----------
b = [f'<rect x="560" y="8" width="26" height="22" fill="{LINE}"/>', text(596, 28, "실제", 24, TXT),
     line(670, 19, 712, 19, ORANGE, 4), text(722, 28, "모델", 24, TXT)]
panels = [("경과 시간", [(40, 120, "0초"), (120, 46, ""), (330, 60, "정수 초")], 0.18),
          ("매수 호가 변화율", [(420, 120, "85%가 정확히 0")], 0.30),
          ("매도 호가 변화율", [(420, 120, "")], 0.30)]
for r, (lab, spikes, sharp) in enumerate(panels):
    y0 = 60 + r * 200
    base = y0 + 180
    b += [text(0, y0 + 30, lab, 28, TXT, weight="bold"), line(0, base, W, base, TXT, 2)]
    pts = []
    for k in range(0, 121):
        xx = 20 + k * 7
        if r == 0:
            hgt = 40 * math.exp(-k / 40)
        else:
            hgt = 34 * math.exp(-((xx - 420) / 140) ** 2) * (abs(xx - 420) > 14)
        pts.append((xx, base - hgt))
    b.append(poly(pts + [(860, base), (20, base)], LINE, 1, SOFT, close=True))
    for sx, h, slab in spikes:
        b.append(f'<rect x="{sx - 8}" y="{base - h}" width="16" height="{h}" fill="{LINE}"/>')
        if slab:
            b.append(text(sx + 18, base - h + 22, slab, 24, INK, weight="bold"))
    mpts = []
    for k in range(0, 121):
        xx = 20 + k * 7
        if r == 0:
            hgt = 70 * math.exp(-k / 22) + 30 * math.exp(-k / 60)
        else:
            hgt = 74 * math.exp(-((xx - 420) / 80) ** 2)
        mpts.append((xx, base - hgt))
    b.append(poly(mpts, ORANGE, 4))
b += [text(0, 676, "모델은 칼날을 뭉툭하게 그린다 · 원문 그림을 바탕으로 다시 그림(모양만)", 24, GRAY)]
figs["ex-atoms"] = svg(690, "\n".join(b))

# ---------- 범주 20개 ----------
b = [text(0, 32, "처음: 범주 2개", 28, TXT, weight="bold"),
     f'<rect x="0" y="50" width="71" height="64" rx="6" fill="{WARN}"/>', f'<rect x="75" y="50" width="813" height="64" rx="6" fill="{LINE}"/>',
     text(12, 92, "8%", 24, FILL, weight="bold"), text(100, 92, "BBO 변화 92%   (체결은 8%뿐 → 체결을 과대 예측)", 24, TXT),
     arrow(444, 126, 444, 170), text(0, 210, "나중: 범주 20개", 28, INK, weight="bold")]
chips = ["체결", "잔량만 바뀜 (가격 그대로)", "매도 호가 상승", "매수 호가 하락", "경과 시간 = 0", "… 모두 20개"]
for i, c in enumerate(chips):
    x, y = (i % 2) * 456, 232 + (i // 2) * 76
    acc = i == 4
    b += [rect(x, y, 432, 60, INK if acc else LINE, FILL, 4 if acc else 2, 8), text(x + 20, y + 40, c, 26, INK if acc else TXT, weight="bold" if acc else "normal")]
b += [rect(0, 480, W, 110, INK, SOFT, 0, 12), text(24, 524, "확산이 맡는 일은 크기만", 28, INK, weight="bold"),
      text(24, 568, "0이 아닌 간격은 얼마나 컸나 · 호가가 얼마나 움직였나", 25, TXT)]
figs["ex-classes"] = svg(595, "\n".join(b))

# ---------- 허들 모형 ----------
b = [rect(244, 0, 400, 70, LINE, SOFT, 2, 10), text(444, 46, "하루 카드 결제액", 30, TXT, "middle", "bold"),
     arrow(444, 76, 444, 118), rect(304, 124, 280, 76, INK, FILL, 4, 38), text(444, 174, "0원인가?", 32, INK, "middle", "bold"),
     arrow(320, 200, 200, 266, "예", lx=232, ly=232), arrow(568, 200, 688, 266, "아니오", lx=640, ly=232),
     box(0, 272, 400, 230, "범주로", ["0원 (결제 없는 날)", "한 칸에 몰린 확률"], size=30, lsize=26),
     box(488, 272, 400, 230, "연속으로", ["금액의 크기"], True, size=30, lsize=26)]
pts = [(520 + k * 3.4, 486 - 90 * (k / 30) * math.exp(1 - k / 30)) for k in range(101)]
b += [poly(pts, INK, 4), f'<rect x="330" y="380" width="40" height="106" rx="4" fill="{INK}" opacity="0.5"/>',
      text(0, 556, "hurdle·zero-inflated 모형: 0인지 먼저 가르고, 아니면 크기 (지어낸 예시)", 24, GRAY)]
figs["t-hurdle"] = svg(570, "\n".join(b))

# ---------- 분위수 변환 ----------
def curve(x0, top, f, color, sw=4, dash="", zmin=-3.2, zmax=3.2, hscale=130, cut=None):
    pts = []
    for k in range(161):
        z = zmin + (zmax - zmin) * k / 160
        if cut and cut[0] < z < cut[1]:
            if pts:
                yield_pts = pts
                pts = []
                yield poly(yield_pts, color, sw, dash=dash)
            continue
        pts.append((x0 + 20 + 380 * k / 160, top - f(z) * hscale))
    if pts:
        yield poly(pts, color, sw, dash=dash)


b = [text(0, 34, "매끈한 데이터", 30, TXT, weight="bold"), text(468, 34, "84.9%가 정확히 0", 30, INK, weight="bold"),
     rect(0, 54, 420, 160, LINE), rect(468, 54, 420, 160, LINE)]
b += list(curve(0, 196, lambda z: 0.9 * ((z + 3.2) / 1.6) * math.exp(1 - (z + 3.2) / 1.6) / 2.2, GRAY))
b += [f'<rect x="672" y="70" width="10" height="126" fill="{INK}"/>', line(488, 196, 868, 196, GRAY, 2), text(692, 96, "0", 24, INK, weight="bold")]
b += [arrow(210, 226, 210, 282, "분위수 변환", lx=226, ly=262), arrow(678, 226, 678, 282, "분위수 변환", lx=694, ly=262),
      rect(0, 292, 420, 200, LINE), rect(468, 292, 420, 200, INK, sw=4)]
b += list(curve(0, 470, lambda z: npdf(z) * 1.8, INK))
b += list(curve(468, 470, lambda z: npdf(z) * 1.8, GRAY, 3, "8 8"))
b += [f'<rect x="671" y="308" width="10" height="162" fill="{INK}"/>', line(488, 470, 868, 470, GRAY, 2),
      text(694, 336, "z = −0.02 한 점에", 22, INK, weight="bold"), text(694, 362, "84.9%가 그대로", 22, INK, weight="bold"),
      text(30, 330, "종 모양이 된다", 24, INK, weight="bold"),
      text(0, 546, "순위가 같은 값은 같은 자리로 간다 · 원문 그림을 바탕으로 다시 그림", 24, GRAY)]
figs["t-quantile"] = svg(560, "\n".join(b))

# ---------- TV 예시 ----------
bins = [("음수", 0.075, 0.25), ("0", 0.85, 0.50), ("양수", 0.075, 0.25)]
base = 290
b = [f'<rect x="520" y="8" width="26" height="22" fill="{LINE}"/>', text(556, 28, "실제", 24, TXT),
     f'<rect x="630" y="8" width="26" height="22" fill="{INK}"/>', text(666, 28, "모델", 24, TXT), line(0, base, W, base, TXT, 2)]
for i, (lab, p, q) in enumerate(bins):
    x = 60 + i * 290
    b += [f'<rect x="{x}" y="{base - p * 220:.0f}" width="80" height="{p * 220:.0f}" fill="{LINE}"/>',
          f'<rect x="{x + 90}" y="{base - q * 220:.0f}" width="80" height="{q * 220:.0f}" fill="{INK}"/>',
          text(x + 40, base - p * 220 - 10, f"{p:g}", 22, GRAY, "middle"), text(x + 130, base - q * 220 - 10, f"{q:g}", 22, INK, "middle"),
          text(x + 85, base + 36, lab, 26, TXT, "middle", "bold"), text(x + 85, base + 74, f"차이 {abs(p - q):g}", 24, WARN, "middle", "bold")]
b += [text(0, 420, "TV = ½ × (0.175 + 0.35 + 0.175) = 0.35  (예시)", 28, TXT, weight="bold", mono=True),
      text(888, 28, "", 1)]
figs["ex-tv"] = svg(436, "\n".join(b))

# ---------- 판별기 ----------
b = [text(0, 30, "실제 이벤트 한 구간", 26, GRAY)]
for i in range(6):
    b.append(rect(i * 92, 48, 80, 64, LINE, SOFT, 2, 8))
b += [rect(560, 44, 140, 72, INK, FILL, 4, 8), text(630, 90, "후보 1개", 24, INK, "middle", "bold"), text(630, 30, "다음 이벤트", 24, INK, "middle"),
      arrow(444, 124, 444, 174), rect(244, 180, 400, 86, TXT, FILL, 3, 12), text(444, 234, "판별기", 34, TXT, "middle", "bold"),
      arrow(360, 272, 220, 324), arrow(528, 272, 668, 324),
      box(0, 330, 400, 110, "실제 데이터?", [], size=30), box(488, 330, 400, 110, "모델이 만든 것?", [], size=30),
      text(0, 500, "판별기가 헷갈릴수록 생성기가 잘 만든 것", 28, INK, weight="bold")]
figs["t-discrim"] = svg(515, "\n".join(b))

# ---------- AUC ----------
P = lambda v: 40 + (v - 0.5) * 1600
b = [text(0, 34, "AUC: ROC 곡선 아래 넓이", 28, TXT, weight="bold"),
     text(0, 74, "진짜·가짜 한 쌍을 판별기가 바르게 줄 세울 확률", 25, GRAY),
     line(P(0.5), 220, P(1.0), 220, TXT, 4)]
for v in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    b += [line(P(v), 208, P(v), 232, TXT, 3), text(P(v), 268, f"{v:.1f}", 24, GRAY, "middle")]
b += [f'<circle cx="{P(0.758):.0f}" cy="220" r="16" fill="{INK}"/>', text(P(0.758), 180, "newrep 0.758", 26, INK, "middle", "bold"),
      text(P(0.758), 148, "정확도 0.694", 22, INK, "middle"),
      f'<circle cx="{P(0.992):.0f}" cy="220" r="16" fill="{GRAY}"/>', text(P(0.992), 180, "smoothed 0.992", 26, GRAY, "end", "bold"),
      text(P(0.992), 148, "정확도 0.959", 22, GRAY, "end"),
      text(P(0.5), 312, "구별 불가", 26, INK, weight="bold"), text(P(1.0), 312, "완벽히 구별", 26, GRAY, "end", weight="bold"),
      f'<line x1="{P(0.9)}" y1="360" x2="{P(0.55)}" y2="360" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>',
      text(P(0.72), 404, "생성기에게는 이쪽이 좋다", 26, INK, "middle", "bold"),
      text(0, 460, "범례 두 이름이 정확히 어떤 설정인지는 본문이 밝히지 않는다", 24, GRAY),
      text(0, 494, "원문 그림의 범례 값을 옮김", 24, GRAY)]
figs["ex-auc"] = svg(510, "\n".join(b))

# ---------- 롤아웃 ----------
rnd = random.Random(7)
n, x0, x1, y_mid = 120, 40, 860, 230
real_bid, real_ask, gen_bid, gen_ask = [], [], [], []
rb, ra, gb, ga = 0.0, 0.0, 0.0, 0.0
for k in range(n):
    rb += rnd.choice([0, 0, 0, 1, -1]) * 3; ra = rb + rnd.choice([0, 0, 3])
    gb += rnd.choice([0, 0, 0, -1, 0]) * 2.2; ga = max(ga + rnd.choice([0, 0, 1, 1, -1]) * 3.4, gb)
    x = x0 + (x1 - x0) * k / (n - 1)
    real_bid.append((x, y_mid + 30 - rb)); real_ask.append((x, y_mid - 30 - ra))
    gen_bid.append((x, y_mid + 30 - rb * 0.5 - gb)); gen_ask.append((x, y_mid - 30 - ra * 0.5 - ga))


def steps(pts):
    out = [pts[0]]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        out += [(xb, ya), (xb, yb)]
    return out


b = [line(x0, 30, x0, 420, TXT, 2), line(x0, 420, x1, 420, TXT, 2), text(x1, 456, "시간 →", 24, GRAY, "end"),
     text(x0 + 10, 50, "가격", 24, GRAY),
     poly(steps(real_ask), TXT, 3), poly(steps(real_bid), TXT, 3),
     poly(steps(gen_ask), ORANGE, 4), poly(steps(gen_bid), ORANGE, 4),
     line(560, 486, 600, 486, TXT, 3), text(610, 494, "실제 호가", 24, TXT),
     line(560, 526, 600, 526, ORANGE, 4), text(610, 534, "생성한 호가", 24, TXT),
     text(0, 494, "생성 쪽 스프레드가 점점 넓어진다", 26, ORANGE, weight="bold"),
     text(0, 534, "CME US, 2022-10-11", 24, GRAY),
     text(0, 574, "원문 그림을 바탕으로 다시 그림(모양만)", 24, GRAY)]
figs["ex-rollout"] = svg(590, "\n".join(b))

# ---------- 두 가지 보기 ----------
b = [box(0, 0, 420, 330, "연속 공간", ["“매도 잔량 10% 증가”"], size=32),
     f'<rect x="26" y="170" width="300" height="40" rx="6" fill="{LINE}"/>', f'<rect x="26" y="230" width="330" height="40" rx="6" fill="{GRAY}"/>',
     text(340, 200, "100", 22, GRAY), text(370, 260, "110", 22, TXT, weight="bold"),
     box(468, 0, 420, 330, "이산 행동 공간", ["“매수 호가를 한 틱 개선”"], True, size=32),
     rect(494, 170, 368, 44, LINE, SOFT, 2, 6), text(510, 201, "170.01", 26, GRAY, mono=True),
     rect(494, 234, 368, 44, INK, FILL, 4, 6), text(510, 265, "170.02  ← 한 틱 위로", 26, INK, mono=True, weight="bold"),
     text(0, 390, "같은 것을 보는 두 가지 방식, 생성하려면 그 섞임을 모델링해야", 26, TXT, weight="bold")]
figs["ex-two-views"] = svg(405, "\n".join(b))

# ---------- 카드 결제 ----------
b = [text(0, 34, "결제 금액", 30, TXT, weight="bold"), text(500, 34, "결제 사이 간격", 30, TXT, weight="bold")]
base = 340
pts = [(10 + k * 4.4, base - 110 * (k / 22) * math.exp(1 - k / 22)) for k in range(101)]
b += [poly(pts + [(454, base), (10, base)], LINE, 1, SOFT, close=True), line(0, base, 450, base, TXT, 2)]
for x, h, lab in [(70, 230, "1만"), (190, 200, "5만"), (330, 150, "10만")]:
    b += [f'<rect x="{x - 8}" y="{base - h}" width="16" height="{h}" fill="{INK}"/>', text(x, base + 34, lab, 24, GRAY, "middle")]
pts = [(530 + k * 3.5, base - 90 * math.exp(-k / 35)) for k in range(101)]
b += [poly(pts + [(880, base), (530, base)], LINE, 1, SOFT, close=True), line(500, base, W, base, TXT, 2),
      f'<rect x="512" y="{base - 250}" width="16" height="250" fill="{INK}"/>', text(520, base + 34, "0초", 24, GRAY, "middle"),
      text(540, base - 226, "분할 승인", 24, INK, weight="bold"),
      text(0, 420, "정액과 0초, 한 점에 몰린 확률은 금융 데이터 어디에나", 27, TXT, weight="bold"),
      text(0, 460, "(지어낸 예시)", 24, GRAY)]
figs["ex-card"] = svg(475, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
