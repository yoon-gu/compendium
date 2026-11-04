#!/usr/bin/env python3
"""비판적 사고 회차의 소리 없는 개념 애니메이션 다섯 편(1776x1000, 25fps). matplotlib 프레임 → ffmpeg.
화면 디자인과 같은 결: 종이 바탕, 잉크색 하나, 나눔고딕. build.py 가 가로 888px 로 줄여 얹는다.

    python3 animate.py              # → experiment, spectrum, questions, greencheck, tax (.mp4 + 확인용 *-sheet.png)
    python3 animate.py spectrum     # 하나만

- experiment.mp4 인지적 항복 실험: AI 없음 기준선에서 맞는 AI +25%p, 틀린 AI -15%p 막대가 자라고, 틀린 쪽 자신감 눈금이 오른다 (12초)
- spectrum.mp4   위임·추종·항복 세 칸이 나레이션에서 언급될 때 하나씩 켜지고, 공이 아래로 미끄러진다 (spectrum-timing.json)
- questions.mp4  스스로에게 묻는 질문 여섯이 '첫째…여섯째'가 들릴 때마다 하나씩 뜬다 (questions-timing.json)
- greencheck.mp4 같은 가정으로 쓴 테스트는 초록불, 실제 호출 apply_discount(100, 10) = -900, 증명한 것/안 한 것 (14초)
- tax.mp4        오케스트레이션 세금: 에이전트가 만든 양은 가파르게, 내가 이름 걸 수 있는 양은 완만히 — 사이가 세금 (11초)
"""
import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
FONTS = Path.home() / "Library/Fonts"
for f in ["NanumGothic-Regular.ttf", "NanumGothic-Bold.ttf", "NanumGothic-ExtraBold.ttf", "NanumGothicCoding-Regular.ttf", "NanumGothicCoding-Bold.ttf"]:
    if (FONTS / f).exists():
        font_manager.fontManager.addfont(str(FONTS / f))
plt.rcParams.update({"font.family": ["NanumGothic", "DejaVu Sans"], "axes.unicode_minus": False})

W, H, FPS = 1776, 1000, 25
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD, OK = "#F4F4F1", "#2E5A4F", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B", "#3A7D44"
MONO = "NanumGothicCoding"


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def pixel_axes(fig):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off"); ax.set_facecolor(PAPER)
    return ax


def render(name, seconds, draw):
    out = HERE / f"{name}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
                            stdin=subprocess.PIPE)
    n = int(seconds * FPS)
    sheet_times = [seconds * k / 5 for k in range(1, 5)]
    shots = []
    for i in range(n):
        t = i / FPS
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=PAPER)
        draw(pixel_axes(fig), t)
        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        proc.stdin.write(bytes(buf))
        if any(abs(t - s) < 0.5 / FPS for s in sheet_times):
            shots.append(bytes(buf))
        plt.close(fig)
    proc.stdin.close(); proc.wait()
    assert proc.returncode == 0
    from PIL import Image
    sheet = Image.new("RGB", (W, H), PAPER)
    for k, buf in enumerate(shots[:4]):
        im = Image.frombuffer("RGBA", (W, H), buf, "raw", "RGBA", 0, 1).convert("RGB").resize((W // 2, H // 2))
        sheet.paste(im, ((k % 2) * W // 2, (k // 2) * H // 2))
    sheet.save(HERE / f"{name}-sheet.png")
    print(f"{out.name}: {n} 프레임, {seconds}초")


def box(ax, x, y, w, h, ec=LINE, fc="#FFFFFF", lw=3, r=18, alpha=1.0, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z))


def timing(name, default):
    p = HERE / f"{name}-timing.json"
    if p.exists():
        d = json.loads(p.read_text())
        return d["duration"], d["marks"]
    return default


# ---------- (a) 인지적 항복 실험 ----------
def draw_experiment(ax, t):
    ax.text(70, 80, "AI 조수를 붙인 추론 문제 (참가자 1,372명)", fontsize=40, color=TXT, fontweight="bold", va="center")
    base_y, scale = 640, 9.0            # 정답률 기준선(AI 없음) 위치, 1%p = 9px
    ax.plot([120, 1660], [base_y, base_y], color=GRAY, lw=3, ls="--")
    ax.text(1660, base_y + 40, "AI 없음 기준선", fontsize=30, color=GRAY, ha="right", va="center")
    for k, (lab, d, col, start) in enumerate([("AI가 맞을 때", 25, OK, 1.0), ("AI가 틀릴 때", -15, BAD, 3.0)]):
        x = 360 + k * 620
        u = ease((t - start) / 1.4)
        h = d * scale * u
        ax.add_patch(Rectangle((x - 130, base_y - max(h, 0)), 260, abs(h), color=col, alpha=0.9))
        if u > 0:
            ax.text(x, base_y - h + (-40 if d > 0 else 50), f"{'+' if d > 0 else ''}{round(d * u)}%p", fontsize=56, color=col,
                    ha="center", va="center", fontweight="bold")
        ax.text(x, base_y - 50 if d < 0 else base_y + 90, lab, fontsize=38, color=TXT, ha="center", va="center", fontweight="bold")
    # 틀린 답을 받은 쪽 자신감 눈금이 오른다
    c = ease((t - 6.0) / 1.5)
    if t > 5.6:
        gx, gy = 1450, 260
        box(ax, gx - 160, gy - 90, 320, 360, ec=BAD, lw=5, r=24)
        ax.text(gx, gy - 40, "틀린 쪽 자신감", fontsize=30, color=BAD, ha="center", va="center", fontweight="bold")
        ax.add_patch(Rectangle((gx - 40, gy), 80, 220, color=SOFT))
        ax.add_patch(Rectangle((gx - 40, gy + 220 - 100 - 90 * c), 80, 100 + 90 * c, color=BAD))
        ax.annotate("", xy=(gx + 110, gy + 20), xytext=(gx + 110, gy + 200),
                    arrowprops=dict(arrowstyle="-|>", color=BAD, lw=5, mutation_scale=40, alpha=c))
    if t > 8.5:
        ax.text(888, 950, "틀린 답을 받았는데 자신감은 올랐다", fontsize=40, color=BAD, ha="center", va="center",
                fontweight="bold", alpha=ease((t - 8.5) / 0.6))


# ---------- (b) 위임·추종·항복 스펙트럼 ----------
SPECTRUM = [("인지 위임", "맡기되 결과의 주인은 나", INK), ("추종", "출력이 다음 생각의 전제", "#8A7A3A"), ("인지적 항복", "확인할 필요조차 못 느낀다", BAD)]


def draw_spectrum(ax, t):
    dur, marks = timing("spectrum", (12.0, [1.0, 4.5, 8.0]))
    current = max((k for k in range(3) if t >= marks[k]), default=-1)
    for k, (head, sub, col) in enumerate(SPECTRUM):
        y = 70 + k * 300
        a = ease((t - marks[k]) / 0.4)
        now = k == current
        if a <= 0:
            box(ax, 260, y, 1300, 250, ec=SOFT, fc=PAPER, lw=3, r=30)
            continue
        box(ax, 260, y, 1300, 250, ec=col, fc=col if now else "#FFFFFF", lw=6 if now else 4, r=30, alpha=a)
        ax.text(330, y + 95, head, fontsize=60 if now else 52, color="#FFFFFF" if now else col, va="center", fontweight="bold", alpha=a)
        ax.text(330, y + 185, sub, fontsize=38, color="#F3F3F0" if now else GRAY, va="center", alpha=a)
    # 왼쪽 세로 미끄럼틀과 공: 지금 말하는 칸 높이로 내려간다
    ax.plot([140, 140], [120, 870], color=LINE, lw=10, solid_capstyle="round")
    tgt = [195, 495, 795]
    if current >= 0:
        prev = tgt[max(current - 1, 0)]
        y = prev + (tgt[current] - prev) * ease((t - marks[current]) / 0.8)
        ax.add_patch(plt.Circle((140, y), 42, color=SPECTRUM[current][2], zorder=5))
    ax.text(140, 950, "신뢰가 쌓일수록 아래로", fontsize=30, color=GRAY, ha="left", va="center")


# ---------- (c) 스스로에게 묻는 질문 여섯 ----------
QUESTIONS = ["묻기 전에 가설을 세웠나?", "생각을 도와 달라는 건가, 덜어 달라는 건가?", "이게 틀렸다면 무엇이 참이어야 할까?",
             "반대 주장을 다른 각도에서 들어 봤나?", "유지보수할 사람 앞에서 걸 수 있나?", "나는 무엇을 더는 연습하지 않나?"]


def draw_questions(ax, t):
    dur, marks = timing("questions", (18.0, [1.0, 4.0, 7.0, 10.0, 13.0, 16.0]))
    current = max((k for k in range(6) if t >= marks[k]), default=-1)
    for k, q in enumerate(QUESTIONS):
        y = 40 + k * 156
        a = ease((t - marks[k]) / 0.35)
        if a <= 0:
            box(ax, 60, y, 1656, 128, ec=SOFT, fc=PAPER, lw=3, r=24)
            continue
        now = k == current
        box(ax, 60, y, 1656, 128, ec=INK, fc=INK if now else "#FFFFFF", lw=6 if now else 3, r=24, alpha=a)
        ax.text(130, y + 64, f"{k + 1}", fontsize=52, color="#FFFFFF" if now else INK, ha="center", va="center", fontweight="bold", alpha=a)
        ax.text(200, y + 64, q, fontsize=46 if now else 42, color="#FFFFFF" if now else TXT, va="center",
                fontweight="bold" if now else "normal", alpha=a)


# ---------- (d) 초록불이 증명한 것 ----------
def code(ax, x, y, s, color=TXT, size=34, alpha=1.0, weight="normal"):
    ax.text(x, y, s, fontsize=size, color=color, va="center", family=MONO, alpha=alpha, fontweight=weight)


def draw_greencheck(ax, t):
    box(ax, 60, 40, 1656, 330, ec=LINE, lw=3, r=16)
    code(ax, 100, 100, "def apply_discount(price, pct):    # pct = 0.1 같은 비율이라 가정", GRAY, 32)
    code(ax, 100, 160, "    return price * (1 - pct)", TXT, 36)
    code(ax, 100, 250, "def test_apply_discount():", GRAY, 32)
    code(ax, 100, 310, "    assert apply_discount(100, 0.1) == 90", TXT, 36)
    g = ease((t - 1.5) / 0.5)
    if g > 0:
        box(ax, 1340, 270, 330, 80, ec=OK, fc=OK, lw=3, r=40, alpha=g)
        ax.text(1505, 310, "✓ 통과", fontsize=40, color="#FFFFFF", ha="center", va="center", fontweight="bold", alpha=g)
    a = ease((t - 4.0) / 0.6)
    if a > 0:
        ax.text(100, 450, "실제 호출: 쿠폰 값은 10 (= 10%)", fontsize=38, color=TXT, va="center", fontweight="bold", alpha=a)
        box(ax, 60, 500, 1656, 110, ec=BAD, lw=5, r=16, alpha=a)
        code(ax, 100, 555, "apply_discount(100, 10)", TXT, 44, a)
        v = -900 * ease((t - 5.0) / 1.2)
        if t > 5.0:
            code(ax, 1000, 555, f"→ {int(v)}", BAD, 54, 1.0, "bold")
    b = ease((t - 7.5) / 0.6)
    if b > 0:
        box(ax, 60, 680, 800, 270, ec=OK, lw=5, r=20, alpha=b)
        ax.text(100, 740, "증명한 것", fontsize=40, color=OK, va="center", fontweight="bold", alpha=b)
        ax.text(100, 820, "같은 가정 안에서", fontsize=36, color=TXT, va="center", alpha=b)
        ax.text(100, 880, "계산이 맞는다", fontsize=36, color=TXT, va="center", alpha=b)
    c = ease((t - 9.5) / 0.6)
    if c > 0:
        box(ax, 916, 680, 800, 270, ec=BAD, lw=5, r=20, alpha=c)
        ax.text(956, 740, "증명하지 않은 것", fontsize=40, color=BAD, va="center", fontweight="bold", alpha=c)
        ax.text(956, 820, "그 가정이 맞는지", fontsize=36, color=TXT, va="center", alpha=c)
        ax.text(956, 880, "실제 입력이 무엇인지", fontsize=36, color=TXT, va="center", alpha=c)


# ---------- (e) 오케스트레이션 세금 ----------
def draw_tax(ax, t):
    x0, y0, x1, y1 = 180, 860, 1640, 120
    ax.plot([x0, x1], [y0, y0], color=TXT, lw=3); ax.plot([x0, x0], [y0, y1], color=TXT, lw=3)
    ax.text(x1, y0 + 50, "세션 수 →", fontsize=32, color=GRAY, ha="right", va="center")
    ax.text(x0 - 20, y1 - 30, "결과물의 양", fontsize=32, color=GRAY, ha="left", va="center")
    u = ease((t - 0.8) / 6.0)
    n = 60
    xs = [x0 + (x1 - x0) * u * i / n for i in range(n + 1)]
    gen = [y0 - (y0 - y1 - 40) * ((x - x0) / (x1 - x0)) for x in xs]                       # 에이전트가 만든 양: 선형으로 가파르게
    me = [y0 - 260 * (1 - (1 - (x - x0) / (x1 - x0)) ** 2) for x in xs]                    # 내가 책임질 수 있는 양: 금방 포화
    if u > 0:
        ax.fill_between(xs, gen, me, color=BAD, alpha=0.18, lw=0)
        ax.plot(xs, gen, color=INK, lw=7)
        ax.plot(xs, me, color=OK, lw=7)
    if u > 0.35:
        ax.text(xs[-1] - 10, gen[-1] - 40, "에이전트가 만든 양", fontsize=36, color=INK, ha="right", va="center", fontweight="bold")
        ax.text(xs[-1] - 10, me[-1] + 50, "내 이름을 걸 수 있는 양", fontsize=36, color=OK, ha="right", va="center", fontweight="bold")
    s = ease((t - 6.5) / 0.6)
    if s > 0:
        xm = x0 + (x1 - x0) * 0.78
        gm = y0 - (y0 - y1 - 40) * 0.78
        mm = y0 - 260 * (1 - 0.22 ** 2)
        ax.annotate("", xy=(xm, gm + 10), xytext=(xm, mm - 10), arrowprops=dict(arrowstyle="<|-|>", color=BAD, lw=5, mutation_scale=36, alpha=s))
        ax.text(xm - 30, gm - 70, "오케스트레이션 세금", fontsize=44, color=BAD, ha="right", va="center", fontweight="bold", alpha=s)
    if t > 8.5:
        ax.text(888, 950, "세션을 늘리기 전에 검사를 조이거나 속도를 늦춘다", fontsize=36, color=TXT, ha="center", va="center",
                alpha=ease((t - 8.5) / 0.6))


ANIMS = {"experiment": (12, draw_experiment), "spectrum": (timing("spectrum", (12.0, None))[0], draw_spectrum),
         "questions": (timing("questions", (18.0, None))[0], draw_questions), "greencheck": (14, draw_greencheck), "tax": (11, draw_tax)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        render(name, *ANIMS[name])
