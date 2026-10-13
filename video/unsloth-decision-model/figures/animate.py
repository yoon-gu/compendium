#!/usr/bin/env python3
"""화면에 얹는 소리 없는 개념 애니메이션 네 편(1776x1000, 25fps)을 matplotlib 으로 프레임마다 그려 ffmpeg 로 굽는다.
화면 디자인과 같은 결: 종이 바탕, 잉크색 하나, 나눔고딕, 글자는 크고 적게. build.py 가 가로 888px 로 줄여 얹는다.

    python3 animate.py              # → gen-vs-dec.mp4, parse-fail.mp4, one-pass.mp4, threshold.mp4 (+ 확인용 *-sheet.png)
    python3 animate.py threshold    # 하나만

- gen-vs-dec.mp4 표지: 생성형은 토큰을 하나씩 찍고, 결정형은 선택지 막대 세 개를 한 번에 채운다 (8초)
- parse-fail.mp4 생성형 분류: "Billing." "The billing team."이 찍히다가 파싱에서 ✗ (10초)
- one-pass.mp4   결정 모델: 프롬프트를 한 번 읽고, 헤드가 선택지마다 점수 (9초)
- threshold.mp4  technical 확률이 0.8을 넘는 순간 행동이 '사람 검토'에서 '자동 버그 리포트'로 (9초)
"""
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
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD = "#F4F4F1", "#8A4B2A", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B"


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


OPTS = [("billing", 0.99), ("technical", 0.01), ("sales", 0.00)]


def option_bars(ax, x, y, fill, w=520, gap=96, label_w=250, opts=OPTS, mono=True):
    for i, (lab, p) in enumerate(opts):
        yy = y + i * gap
        ax.text(x, yy + 26, lab, fontsize=34, color=TXT, va="center", **({"family": "NanumGothicCoding"} if mono else {}))
        bar(ax, x + label_w, yy, w, 52, p * fill)
        if fill > 0.05:
            ax.text(x + label_w + w + 20, yy + 26, f"{p * fill:.2f}", fontsize=32, color=INK, va="center", fontweight="bold")


# ---------- (a) 표지: 생성형 vs 결정형 ----------
GEN = ["The", "answer", "is", "Billing", "."]


def draw_gen_vs_dec(ax, t):
    ax.plot([888, 888], [60, 940], color=LINE, lw=3)
    ax.text(60, 100, "생성형", fontsize=60, color=TXT, fontweight="bold", va="center")
    ax.text(948, 100, "결정형", fontsize=60, color=INK, fontweight="bold", va="center")
    # 왼쪽: 토큰이 하나씩
    k = min(int(max(t - 0.6, 0) / 1.0) + (1 if t >= 0.6 else 0), len(GEN))
    for i in range(len(GEN)):
        x, y = 60 + (i % 3) * 250, 250 + (i // 3) * 190
        if i < k:
            box(ax, x, y, 230, 150, ec=TXT, lw=3)
            ax.text(x + 115, y + 75, GEN[i], fontsize=42, color=TXT, ha="center", va="center", fontweight="bold")
        elif i == k:
            box(ax, x, y, 230, 150, ec=LINE, fc=PAPER, lw=3)
            if int(t * 3) % 2:
                ax.text(x + 115, y + 75, "▍", fontsize=52, color=GRAY, ha="center", va="center")
    ax.text(60, 760, f"토큰 {k}개 생성", fontsize=44, color=TXT, fontweight="bold")
    ax.text(60, 840, "토큰 하나에 한 번씩 계산", fontsize=36, color=GRAY)
    # 오른쪽: 막대가 한 번에
    fill = ease((t - 1.0) / 1.0)
    option_bars(ax, 948, 250, fill, w=360, gap=150, label_w=230, opts=OPTS)
    ax.text(948, 760, "토큰 0개 생성", fontsize=44, color=INK, fontweight="bold")
    ax.text(948, 840, "한 번 읽고 선택지마다 확률", fontsize=36, color=GRAY)


# ---------- (b) 생성형 분류가 깨지는 순간 ----------
TRIES = [("Billing.", 0.6), ("The billing team.", 4.0)]


def draw_parse_fail(ax, t):
    box(ax, 60, 50, 1656, 150, ec=LINE, fc=SOFT)
    ax.text(100, 125, "“Answer with one of: billing / technical / sales”", fontsize=40, color=TXT, va="center")
    for row, (ans, t0) in enumerate(TRIES):
        y = 290 + row * 330
        if t < t0:
            continue
        ax.text(60, y, f"시도 {row + 1}", fontsize=34, color=GRAY, va="center")
        n = min(int((t - t0) / 0.2) + 1, len(ans))
        box(ax, 60, y + 40, 760, 160, ec=TXT, lw=3)
        ax.text(100, y + 120, ans[:n], fontsize=60, color=TXT, va="center", fontweight="bold")
        tp = t0 + len(ans) * 0.2 + 0.4
        if t >= tp:
            arrow(ax, 840, y + 120, 1000, y + 120, color=GRAY)
            box(ax, 1020, y + 40, 696, 160, ec=LINE)
            ax.text(1050, y + 120, "== 'billing' ?", fontsize=46, color=TXT, va="center", family="NanumGothicCoding")
        if t >= tp + 0.8:
            ax.text(1640, y + 120, "✗", fontsize=90, color=BAD, ha="center", va="center", fontweight="bold")
            ax.text(1716, y + 240, "파싱 실패", fontsize=38, color=BAD, ha="right", va="center", fontweight="bold")


# ---------- (c) 한 번 읽고 헤드가 점수 ----------
TOKS = [("입력", 3, False), ("질문", 1, False), ("선택지", 3, True)]


def draw_one_pass(ax, t):
    # 프롬프트 토큰 줄: 빛이 왼쪽에서 오른쪽으로 한 번 지나간다
    sweep = ease((t - 0.4) / 1.8) * 1656
    x = 60
    for lab, n, opt in TOKS:
        for j in range(n):
            lit = x + 60 < 60 + sweep
            box(ax, x, 60, 120, 110, ec=INK if lit else LINE, fc="#FFFFFF", lw=5 if lit else 3, r=12)
            ax.text(x + 60, 115, lab if j == 0 else "·", fontsize=28 if j == 0 else 40, color=INK if lit else GRAY, ha="center", va="center")
            x += 136
    ax.text(x + 30, 115, "→ 프롬프트 하나", fontsize=36, color=GRAY, va="center")
    # LLM 상자
    on = 0.4 < t < 2.6
    arrow(ax, 400, 190, 400, 270, color=INK if on else LINE)
    box(ax, 60, 280, 720, 170, ec=INK if on else TXT, lw=6 if on else 3)
    ax.text(420, 350, "LLM이 한 번 읽는다", fontsize=46, color=INK if on else TXT, ha="center", va="center", fontweight="bold")
    ax.text(420, 410, "자리마다 은닉 상태", fontsize=32, color=GRAY, ha="center", va="center")
    # 헤드
    hon = 2.6 <= t < 4.4
    arrow(ax, 400, 460, 400, 540, color=INK if t >= 2.6 else LINE)
    box(ax, 60, 550, 720, 170, ec=INK if hon else (TXT if t >= 2.6 else LINE), lw=6 if hon else 3)
    ax.text(420, 620, "결정 헤드", fontsize=46, color=INK if t >= 2.6 else LINE, ha="center", va="center", fontweight="bold")
    ax.text(420, 680, "선택지 자리를 보고 채점", fontsize=32, color=GRAY, ha="center", va="center")
    # 막대
    fill = ease((t - 3.2) / 1.4)
    arrow(ax, 800, 635, 880, 635, color=INK if fill > 0 else LINE)
    option_bars(ax, 910, 470, fill, w=460, gap=110, label_w=230)
    ax.text(60, 860, "생성 토큰 0개 · 순전파 1번", fontsize=46, color=INK if t >= 4.6 else LINE, fontweight="bold")


# ---------- (d) 문턱값 ----------
def draw_threshold(ax, t):
    p = 0.30 + 0.62 * ease((t - 1.0) / 5.0)
    ax.text(60, 90, "technical 확률", fontsize=46, color=TXT, fontweight="bold", va="center")
    ax.text(1716, 90, f"{p:.2f}", fontsize=72, color=INK if p >= 0.8 else TXT, fontweight="bold", va="center", ha="right")
    bx, bw = 60, 1656
    bar(ax, bx, 170, bw, 90, p, INK if p >= 0.8 else GRAY)
    tx = bx + bw * 0.8
    ax.plot([tx, tx], [145, 285], color=TXT, lw=5)
    ax.text(tx, 330, "문턱 0.8", fontsize=36, color=TXT, ha="center", va="center", fontweight="bold")
    ax.text(bx, 330, "0", fontsize=32, color=GRAY, va="center")
    ax.text(bx + bw, 330, "1", fontsize=32, color=GRAY, va="center", ha="right")
    for i, (title, sub, active) in enumerate([("사람이 한 번 본다", "0.8 미만", p < 0.8), ("버그 리포트 자동 생성", "0.8 이상", p >= 0.8)]):
        x = 60 + i * 868
        box(ax, x, 440, 788, 380, ec=INK if active else LINE, fc=INK if active else "#FFFFFF", lw=6 if active else 3, r=24)
        ax.text(x + 394, 580, title, fontsize=50, color="#FFFFFF" if active else LINE, ha="center", va="center", fontweight="bold")
        ax.text(x + 394, 690, sub, fontsize=38, color="#FFFFFF" if active else LINE, ha="center", va="center")


ANIMS = {"gen-vs-dec": (8, draw_gen_vs_dec), "parse-fail": (10, draw_parse_fail),
         "one-pass": (9, draw_one_pass), "threshold": (9, draw_threshold)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        render(name, *ANIMS[name])
