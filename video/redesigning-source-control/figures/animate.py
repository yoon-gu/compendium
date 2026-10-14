#!/usr/bin/env python3
"""화면에 얹는 소리 없는 개념 애니메이션 네 편(1776x1000, 25fps)을 matplotlib 으로 프레임마다 그려 ffmpeg 로 굽는다.
화면 디자인과 같은 결: 종이 바탕, 잉크색 하나, 나눔고딕, 글자는 크고 적게. build.py 가 가로 888px 로 줄여 얹는다.

    python3 animate.py            # → growth.mp4, fetch.mp4, tiers.mp4, merge.mp4 (+ 확인용 *-sheet.png)
    python3 animate.py tiers      # 하나만

- growth.mp4 표지: 하루 병합 변경 2026년 5월 2,500건 → 9월 30,000건 이상 (원문 수치 두 개만, 8초)
- fetch.mp4  git은 작업마다 이력을 통째로, Scion은 읽는 파일만 받아 간다 (개념 그림, 9초)
- tiers.mp4  요청이 daemon → cache → server 로 가다가 대부분 가까운 층에서 끝난다 (개념 그림, 9초)
- merge.mp4  병합 큐는 한 줄로 기다리고, 병합 뒤 복구는 한꺼번에 들어가 충돌을 Claude가 고친다 (개념 그림, 10초)
"""
import random
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
for f in ["NanumGothic-Regular.ttf", "NanumGothic-Bold.ttf", "NanumGothic-ExtraBold.ttf", "NanumGothicCoding-Regular.ttf"]:
    if (FONTS / f).exists():
        font_manager.fontManager.addfont(str(FONTS / f))
plt.rcParams.update({"font.family": ["NanumGothic", "DejaVu Sans"], "axes.unicode_minus": False})

W, H, FPS = 1776, 1000, 25
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD = "#F4F4F1", "#5B3F8C", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B"


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


def box(ax, x, y, w, h, ec=LINE, fc="#FFFFFF", lw=3, r=18, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, alpha=alpha))


def bar(ax, x, y, w, h, frac, color=INK):
    ax.add_patch(Rectangle((x, y), w, h, color=SOFT))
    ax.add_patch(Rectangle((x, y), max(w * frac, 3), h, color=color))


def arrow(ax, x1, y1, x2, y2, color=INK, lw=5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=40))


def sq(ax, x, y, s, color, alpha=1.0):
    ax.add_patch(Rectangle((x - s / 2, y - s / 2), s, s, color=color, alpha=alpha))


# ---------- (a) 표지: 하루 병합 변경 ----------
def draw_growth(ax, t):
    ax.text(60, 90, "모노레포에 하루 병합되는 변경", fontsize=44, color=TXT, fontweight="bold", va="center")
    base, top = 900, 230
    g1, g2 = ease((t - 0.4) / 1.2), ease((t - 1.8) / 2.6)
    for x, val, g, lab, col in [(260, 2500, g1, "2026년 5월", GRAY), (1100, 30000, g2, "2026년 9월", INK)]:
        h = (base - top) * val / 30000 * g
        ax.add_patch(Rectangle((x, base - h), 360, h, color=col))
        ax.text(x + 180, base + 50, lab, fontsize=36, color=TXT, ha="center", va="center")
        if g > 0.02:
            ax.text(x + 180, base - h - 50, f"{int(val * g):,}건" + ("+" if val == 30000 and g > 0.99 else ""), fontsize=52,
                    color=col, ha="center", va="center", fontweight="bold")
    ax.plot([140, 1640], [base, base], color=LINE, lw=3)
    if t > 4.8:
        a = ease((t - 4.8) / 0.6)
        ax.text(860, 420, "× 12", fontsize=96, color=INK, ha="center", va="center", fontweight="bold", alpha=a)
        ax.text(860, 520, "다섯 달", fontsize=40, color=GRAY, ha="center", va="center", alpha=a)


# ---------- (b) 전부 받기 vs 읽는 것만 ----------
def panel_fetch(ax, x0, title, heavy, t):
    col = GRAY if heavy else INK
    ax.text(x0 + 400, 70, title, fontsize=50, color=col, ha="center", va="center", fontweight="bold")
    box(ax, x0 + 250, 130, 300, 150, ec=col, lw=4)
    ax.text(x0 + 400, 180, "서버", fontsize=38, color=TXT, ha="center", va="center", fontweight="bold")
    ax.text(x0 + 400, 240, "이력 100GB", fontsize=30, color=GRAY, ha="center", va="center")
    for j in range(3):
        jx = x0 + 60 + j * 260
        box(ax, jx, 720, 200, 150, ec=LINE, lw=3)
        ax.text(jx + 100, 795, f"CI 작업 {j + 1}", fontsize=30, color=TXT, ha="center", va="center")
        start = 0.5 + j * 0.5
        for k in range(10 if heavy else 2):
            u = ((t - start - k * (0.12 if heavy else 0.9)) % 3.0) / 1.6
            if t < start or u > 1:
                continue
            y = 290 + (700 - 290) * ease(u)
            sq(ax, jx + 100 + (k % 3 - 1) * (36 if heavy else 0), y, 40 if heavy else 22, col, 0.85)
    ax.text(x0 + 400, 930, "작업마다 수 GB" if heavy else "작업마다 읽는 파일만", fontsize=40, color=col, ha="center", va="center", fontweight="bold")


def draw_fetch(ax, t):
    ax.plot([888, 888], [40, 960], color=LINE, lw=3)
    panel_fetch(ax, 0, "git", True, t)
    panel_fetch(ax, 900, "Scion", False, t)


# ---------- (c) 3층 캐시 ----------
COLS = [(170, "CI 작업"), (620, "daemon"), (1070, "cache"), (1520, "server")]
rnd = random.Random(7)
REQS = []
for i in range(60):
    r = rnd.random()
    REQS.append((i * 0.13, rnd.randint(0, 3), 1 if r < 0.86 else (2 if r < 0.985 else 3)))   # 출발 시각, 줄, 끝나는 층(개념 비율)


def draw_tiers(ax, t):
    ax.text(60, 70, "요청은 대부분 가까운 층에서 끝난다", fontsize=44, color=TXT, fontweight="bold", va="center")
    for x, lab in COLS:
        box(ax, x - 150, 180, 300, 620, ec=INK if lab != "CI 작업" else LINE, fc="#FFFFFF", lw=4 if lab != "CI 작업" else 3)
        ax.text(x, 860, lab, fontsize=38, color=TXT, ha="center", va="center", fontweight="bold", family="NanumGothicCoding" if lab != "CI 작업" else None)
    for k, (x0, _), (x1, _) in zip(range(3), COLS, COLS[1:]):
        arrow(ax, x0 + 160, 490, x1 - 160, 490, color=LINE, lw=3)
    counts = [0, 0, 0]
    for t0, lane, stop in REQS:
        u = t - t0
        if u < 0:
            continue
        y = 250 + lane * 150
        travel = 0.9 * stop
        if u < travel:
            x = COLS[0][0] + (COLS[stop][0] - COLS[0][0]) * (u / travel)
            ax.plot(x, y, "o", ms=16, color=INK if stop == 1 else (GRAY if stop == 2 else BAD))
        else:
            counts[stop - 1] += 1
    tot = max(sum(counts), 1)
    for i, c in enumerate(counts):
        ax.text(COLS[i + 1][0], 940, f"여기서 끝남 {c}", fontsize=28, color=GRAY, ha="center", va="center")
    ax.text(1716, 70, "내용이 안 바뀌니 어느 층이든 캐시", fontsize=30, color=GRAY, ha="right", va="center")


# ---------- (d) 병합 큐 vs 병합 뒤 복구 ----------
def draw_merge(ax, t):
    ax.plot([888, 888], [40, 960], color=LINE, lw=3)
    ax.text(444, 70, "병합 큐", fontsize=50, color=GRAY, ha="center", va="center", fontweight="bold")
    ax.text(1332, 70, "병합 뒤 복구", fontsize=50, color=INK, ha="center", va="center", fontweight="bold")
    # 왼쪽: 1.2초마다 하나씩 통과, 0.4초마다 하나씩 도착
    arrived, passed = int(t / 0.4) + 1, int(t / 1.2)
    waiting = arrived - passed
    box(ax, 120, 160, 650, 90, ec=GRAY, fc=SOFT, lw=3)
    ax.text(445, 205, "main", fontsize=36, color=TXT, ha="center", va="center", family="NanumGothicCoding")
    ax.add_patch(Rectangle((410, 290), 70, 30, color=GRAY))
    ax.text(530, 305, "검사 중", fontsize=28, color=GRAY, va="center")
    for k in range(min(waiting, 14)):
        sq(ax, 445, 380 + k * 40, 30, GRAY, 0.8)
    ax.text(444, 940, f"대기 {waiting}건", fontsize=44, color=BAD if waiting > 10 else GRAY, ha="center", va="center", fontweight="bold")
    # 오른쪽: 변경이 한꺼번에 들어가고, 가끔 충돌 → Claude가 고침
    box(ax, 1008, 160, 650, 90, ec=INK, fc="#FFFFFF", lw=4)
    ax.text(1333, 205, "main", fontsize=36, color=INK, ha="center", va="center", family="NanumGothicCoding")
    rr = random.Random(3)
    for k in range(40):
        t0, lane = k * 0.24, rr.randint(0, 7)
        conflict = k % 9 == 4
        u = (t - t0) / 1.0
        if u < 0:
            continue
        x = 1060 + lane * 78
        if u < 1:
            sq(ax, x, 860 - (860 - 260) * ease(u), 30, INK, 0.85)
        elif conflict and u < 2.2:
            ax.plot(x, 290, "o", ms=26, color=BAD if u < 1.6 else INK)
            ax.text(x, 340, "충돌" if u < 1.6 else "Claude가 고침", fontsize=24, color=BAD if u < 1.6 else INK, ha="center", va="center")
    ax.text(1332, 940, f"병합 {sum(1 for k in range(40) if t - k * 0.24 >= 1)}건 · 테스트는 병합 뒤", fontsize=36, color=INK, ha="center", va="center", fontweight="bold")


ANIMS = {"growth": (8, draw_growth), "fetch": (9, draw_fetch), "tiers": (9, draw_tiers), "merge": (10, draw_merge)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        render(name, *ANIMS[name])
