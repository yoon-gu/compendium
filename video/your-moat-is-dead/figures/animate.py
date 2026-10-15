#!/usr/bin/env python3
"""화면에 얹는 소리 없는 개념 애니메이션 네 편(1776x1000, 25fps)을 matplotlib 으로 프레임마다 그려 ffmpeg 로 굽는다.
화면 디자인과 같은 결: 종이 바탕, 잉크색 하나, 나눔고딕, 글자는 크고 적게. build.py 가 가로 888px 로 줄여 얹는다.

    python3 animate.py            # → moat.mp4, cleanroom.mp4, leak.mp4, compound.mp4 (+ 확인용 *-sheet.png)
    python3 animate.py leak       # 하나만

- moat.mp4      표지: '코드'라는 해자의 물이 빠지고, 성 둘레에 책임·데이터·신뢰·물리 세계 벽이 선다 (개념 그림, 9초)
- cleanroom.mp4 클린룸: 관찰 팀 → 명세 → 벽 → 구현 팀. 1984년 몇 달, 지금은 에이전트로 몇 주 (9초)
- leak.mp4      새는 해자 다섯: 기능·화면·파일 형식·연동·좌석 과금 물탱크가 새어 내려간다 (개념 그림, 9초)
- compound.mp4  커지는 해자: '결과 책임' 둘레의 데이터·책임·유통·자기 서버가 나레이션에서 언급될 때마다 하나씩 굵게 켜진다 (길이·시각은 compound-timing.json)
"""
import math
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
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD = "#F4F4F1", "#7A2E3A", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B"


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




WATER = "#8FB3C9"


# ---------- (a) 표지: 해자의 물이 빠지고, 다른 벽이 선다 ----------
def castle(ax, cx, cy, w, h):
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="#FFFFFF", ec=INK, lw=5))
    for i in range(6):
        ax.add_patch(Rectangle((cx - w / 2 + 10 + i * (w - 20) / 6, cy - h / 2 - 34), (w - 20) / 12, 34, color=INK))
    ax.text(cx, cy, "회사", fontsize=46, color=INK, ha="center", va="center", fontweight="bold")


def draw_moat(ax, t):
    cx, cy = 888, 470
    level = 1 - ease((t - 1.0) / 3.0)                      # 물이 빠진다
    ax.add_patch(FancyBboxPatch((cx - 620, cy - 330), 1240, 660, boxstyle="round,pad=0,rounding_size=60",
                                fc=WATER, ec="none", alpha=0.15 + 0.55 * level))
    ax.text(cx - 560, cy - 280, "해자 = 코드", fontsize=40, color="#2F5A73", fontweight="bold", va="center", alpha=0.3 + 0.7 * level)
    castle(ax, cx, cy, 380, 260)
    ax.text(cx + 560, cy - 280, f"코드 비용 {int(100 * (0.1 + 0.9 * level))}", fontsize=34, color=GRAY, ha="right", va="center")
    walls = [("책임", cx, cy - 245), ("데이터", cx + 330, cy), ("신뢰·유통", cx, cy + 245), ("물리 세계", cx - 330, cy)]
    for k, (lab, x, y) in enumerate(walls):
        a = ease((t - 4.4 - k * 0.6) / 0.6)
        if a <= 0:
            continue
        box(ax, x - 130, y - 48, 260, 96, ec=INK, fc="#FFFFFF", lw=5, alpha=a)
        ax.text(x, y, lab, fontsize=36, color=INK, ha="center", va="center", fontweight="bold", alpha=a)


# ---------- (b) 클린룸 ----------
def draw_cleanroom(ax, t):
    box(ax, 60, 220, 380, 300, ec=LINE, lw=3)
    ax.text(250, 290, "원본", fontsize=44, color=TXT, ha="center", va="center", fontweight="bold")
    ax.text(250, 370, "화면 · 메뉴 · 파일", fontsize=30, color=GRAY, ha="center", va="center")
    ax.text(250, 440, "(코드는 안 본다)", fontsize=28, color=GRAY, ha="center", va="center")
    era2 = t >= 4.5
    who1, who2 = ("관찰 에이전트", "구현 에이전트") if era2 else ("관찰 팀", "구현 팀")
    box(ax, 520, 220, 330, 300, ec=INK, lw=5)
    ax.text(685, 330, who1, fontsize=38, color=INK, ha="center", va="center", fontweight="bold")
    ax.text(685, 410, "명세만 쓴다", fontsize=30, color=GRAY, ha="center", va="center")
    arrow(ax, 445, 370, 515, 370, color=GRAY)
    ax.plot([1000, 1000], [160, 600], color=BAD, lw=8)
    ax.text(1000, 640, "벽", fontsize=32, color=BAD, ha="center", va="center", fontweight="bold")
    u = (t % 4.5) / 4.5
    x = 860 + (1180 - 860) * ease((u - 0.25) / 0.4)
    box(ax, x, 320, 120, 150, ec=TXT, fc="#FFFFFF", lw=3, r=8)
    for k in range(4):
        ax.plot([x + 20, x + 100], [360 + k * 25, 360 + k * 25], color=LINE, lw=4)
    ax.text(x + 60, 500, "명세", fontsize=28, color=TXT, ha="center", va="center")
    box(ax, 1320, 220, 380, 300, ec=INK, lw=5)
    ax.text(1510, 330, who2, fontsize=38, color=INK, ha="center", va="center", fontweight="bold")
    ax.text(1510, 410, "원본을 본 적 없다", fontsize=30, color=GRAY, ha="center", va="center")
    year, dur = ("2026년", "몇 주") if era2 else ("1984년", "몇 달")
    ax.text(888, 820, f"{year} · {dur}", fontsize=64, color=INK if era2 else TXT, ha="center", va="center", fontweight="bold")
    ax.text(888, 910, "저작권은 표현을 보호하지 기능을 보호하지 않는다", fontsize=32, color=GRAY, ha="center", va="center")


# ---------- (c) 새는 해자 다섯 ----------
TANKS = ["기능", "화면", "파일 형식", "연동", "좌석 과금"]


def draw_leak(ax, t):
    ax.text(60, 80, "새는 해자 다섯", fontsize=48, color=TXT, fontweight="bold", va="center")
    for i, lab in enumerate(TANKS):
        x = 100 + i * 330
        start = 0.6 + i * 0.5
        level = 1 - 0.8 * ease((t - start) / 4.0)
        box(ax, x, 220, 240, 520, ec=TXT, fc="#FFFFFF", lw=4, r=12)
        h = 500 * level
        ax.add_patch(Rectangle((x + 10, 730 - h), 220, h, color=WATER, alpha=0.8))
        if t > start:   # 바닥에서 새는 물방울
            for k in range(4):
                dy = ((t * 1.6 + k * 0.25 + i * 0.1) % 1.0) * 120
                ax.plot(x + 120, 760 + dy, "o", ms=10, color=WATER, alpha=1 - dy / 120)
        ax.text(x + 120, 830, lab, fontsize=36, color=TXT, ha="center", va="center", fontweight="bold")
        ax.text(x + 120, 190, f"{int(100 * level)}%", fontsize=32, color=BAD if level < 0.5 else GRAY, ha="center", va="center", fontweight="bold")
    ax.text(888, 950, "에이전트가 명세를 다시 구현하면 물이 샌다", fontsize=32, color=GRAY, ha="center", va="center")


# ---------- (d) 커지는 해자 ----------
# 네 가지가 나레이션에서 언급되는 순간 하나씩 굵게 켜진다. 시각은 compound-timing.json(녹음 뒤 계산)에서 읽는다.
import json
TIMING = HERE / "compound-timing.json"
SPOKES = [("데이터 루프", 0, -310), ("책임", 470, 0), ("유통", 0, 310), ("자기 서버", -470, 0)]   # 언급 순서대로 위·오른쪽·아래·왼쪽


def compound_timing():
    if TIMING.exists():
        d = json.loads(TIMING.read_text())
        return d["duration"], d["marks"]
    return 10.0, [3.0, 4.6, 6.2, 7.8]


def draw_compound(ax, t):
    _, marks = compound_timing()
    cx, cy = 888, 470
    for k, (lab, dx, dy) in enumerate(SPOKES):
        on = ease((t - marks[k]) / 0.35)
        x, y = cx + dx, cy + dy
        ax.plot([cx, x], [cy, y], color=INK if on > 0.5 else LINE, lw=3 + 3 * on, zorder=1)
        bw, bh = 300 + 30 * on, 100 + 10 * on
        box(ax, x - bw / 2, y - bh / 2, bw, bh, ec=INK if on > 0 else LINE, fc=INK if on > 0.5 else "#FFFFFF", lw=3 + 3 * on, r=48)
        ax.text(x, y, lab, fontsize=34 + 6 * on, color="#FFFFFF" if on > 0.5 else (GRAY if on == 0 else INK),
                ha="center", va="center", fontweight="bold" if on > 0 else "normal", zorder=3)
    ax.add_patch(plt.Circle((cx, cy), 165, color=INK, zorder=2))
    ax.text(cx, cy - 34, "결과", fontsize=48, color="#FFFFFF", ha="center", va="center", fontweight="bold", zorder=3)
    ax.text(cx, cy + 34, "책임", fontsize=48, color="#FFFFFF", ha="center", va="center", fontweight="bold", zorder=3)
    ax.text(888, 940, "도구는 주말에 복제된다. 약속은 매달 지켜야 한다.", fontsize=34, color=GRAY, ha="center", va="center")


ANIMS = {"moat": (9, draw_moat), "cleanroom": (9, draw_cleanroom), "leak": (9, draw_leak), "compound": (compound_timing()[0], draw_compound)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        render(name, *ANIMS[name])
