#!/usr/bin/env python3
"""화면에 얹는 소리 없는 개념 애니메이션 세 편(1776x1000, 25fps)을 matplotlib 으로 프레임마다 그려 ffmpeg 로 굽는다.
화면 디자인과 같은 결: 종이 바탕, 잉크색 하나, 나눔고딕, 글자는 크고 적게. build.py 가 가로 888px 로 줄여 16:9 자리에 얹는다.

    python3 animate.py            # → traj.mp4, ar-loop.mp4, atom.mp4, rollout.mp4 (+ 확인용 *-sheet.png)
    python3 animate.py atom       # 하나만

- traj.mp4    ε 예측(DDPM식) 궤적이 초반에 8σ 밖으로 튀어 나가는 모습 vs flow matching 의 곧은 궤적 (개념 그림, 8초)
- ar-loop.mp4 자기회귀 생성: 종류를 뽑고, 값을 만들고, 흐름 끝에 붙이고, 다시 (9초)
- rollout.mp4 표지: 모델이 앞날을 여러 갈래로 그려 보고 하나씩 골라 호가 경로를 이어 간다 (개념 그림, 지어낸 데이터, 10초)
- atom.mp4    atom smoothing: 한 점에 몰린 84.9% 를 N(0,1)의 한 구간으로 폈다가, 생성 후 다시 0으로 접는다 (10초)
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
for f in ["NanumGothic-Regular.ttf", "NanumGothic-Bold.ttf", "NanumGothic-ExtraBold.ttf"]:
    font_manager.fontManager.addfont(str(FONTS / f))
plt.rcParams.update({"font.family": ["NanumGothic", "DejaVu Sans"], "axes.unicode_minus": False})

W, H, FPS = 1776, 1000, 25
PAPER, INK, TXT, GRAY, LINE, SOFT, WARN = "#F4F4F1", "#2F6B4F", "#141414", "#6B6B68", "#B9B9B4", "#ECECE8", "#A23B3B"


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def canvas():
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=PAPER)
    return fig


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
        fig = canvas()
        draw(fig, t)
        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        proc.stdin.write(bytes(buf))
        if any(abs(t - s) < 0.5 / FPS for s in sheet_times):
            shots.append((t, bytes(buf)))
        plt.close(fig)
    proc.stdin.close(); proc.wait()
    assert proc.returncode == 0
    # 확인용 contact sheet (4장)
    from PIL import Image
    sheet = Image.new("RGB", (W, H), PAPER)
    for k, (t, buf) in enumerate(shots[:4]):
        im = Image.frombuffer("RGBA", (W, H), buf, "raw", "RGBA", 0, 1).convert("RGB").resize((W // 2, H // 2))
        sheet.paste(im, ((k % 2) * W // 2, (k // 2) * H // 2))
    sheet.save(HERE / f"{name}-sheet.png")
    print(f"{out.name}: {n} 프레임, {seconds}초")


# ---------- (a) 노이즈 → 데이터 궤적 ----------
rnd = random.Random(3)
TRAJ = []
for i in range(16):
    z0 = rnd.gauss(0, 1.0)
    d = rnd.uniform(-2.2, 2.2)
    blow = i % 8 != 0                                   # 대부분이 튀어 나간다(개념 그림)
    k = rnd.choice([-1, 1]) * rnd.uniform(0.75, 1.25) * (1 if blow else 0.12)
    TRAJ.append((z0, d, k, blow))


def eps_path(z0, d, k, s):
    dev = k * 15 * (1 - math.exp(-s / 0.07))
    y = (1 - s) * z0 + s * d + dev
    return max(min(y, 11.4), -11.4)


def draw_traj(fig, t):
    prog = ease(t / 5.2)
    titles = [("ε 예측 (DDPM식)", WARN), ("flow matching", INK)]
    for p in range(2):
        ax = fig.add_axes([0.07 + p * 0.48, 0.17, 0.41, 0.66])
        ax.set_facecolor("#FFFFFF")
        ax.set_xlim(0, 1); ax.set_ylim(-12, 12)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        for side in ["left", "bottom"]:
            ax.spines[side].set_color(GRAY); ax.spines[side].set_linewidth(2)
        ax.set_xticks([]); ax.set_yticks([-8, 0, 8]); ax.set_yticklabels(["−8σ", "0", "8σ"], fontsize=34, color=GRAY)
        ax.tick_params(length=0, pad=10)
        ax.axhspan(8, 12, color=WARN, alpha=0.08); ax.axhspan(-12, -8, color=WARN, alpha=0.08)
        ax.axhline(8, color=WARN, lw=2.5, ls=(0, (6, 6))); ax.axhline(-8, color=WARN, lw=2.5, ls=(0, (6, 6)))
        ax.set_xlabel("노이즈  →  데이터", fontsize=38, color=TXT, labelpad=16)
        ax.set_title(titles[p][0], fontsize=50, color=titles[p][1], fontweight="bold", pad=24)
        steps = max(2, int(prog * 120))
        ss = [prog * j / (steps - 1) for j in range(steps)]
        for z0, d, k, blow in TRAJ:
            if p == 0:
                ys = [eps_path(z0, d, k, s) for s in ss]
                out = any(abs(y) >= 8 for y in ys)
                ax.plot(ss, ys, color=WARN if out else INK, lw=3.2, alpha=0.85)
            else:
                ys = [(1 - s) * z0 + s * d for s in ss]
                ax.plot(ss, ys, color=INK, lw=3.2, alpha=0.85)
            ax.plot([0], [z0], "o", color=GRAY, ms=9)
        if p == 0 and t > 1.4:
            a = min(1, (t - 1.4) / 0.6)
            ax.text(0.62, -5, "초반에 튀어 나간다", fontsize=40, color=WARN, ha="center", va="center", fontweight="bold", alpha=a)
        if p == 1 and t > 4.4:
            a = min(1, (t - 4.4) / 0.6)
            ax.text(0.5, -5, "곧은 길", fontsize=40, color=INK, ha="center", va="center", fontweight="bold", alpha=a)
    fig.text(0.985, 0.03, "개념 그림", fontsize=30, color=GRAY, ha="right")


# ---------- (b) 자기회귀 생성 ----------
CHIP_W, CHIP_H, GAP = 210, 130, 22
STREAM0 = [("체결", "100주"), ("BBO", "잔량만"), ("BBO", "매수 −1틱"), ("주문", "170.02"), ("BBO", "매도 +1틱")]
NEW = [("BBO", "매도 +1틱"), ("체결", "200주"), ("BBO", "잔량만")]
CYCLE = 3.0


def chip(ax, x, y, kind, val, accent=False, alpha=1.0, filled=True):
    ax.add_patch(FancyBboxPatch((x, y), CHIP_W, CHIP_H, boxstyle="round,pad=0,rounding_size=16",
                                fc="#FFFFFF" if filled else PAPER, ec=INK if accent else LINE, lw=5 if accent else 3, alpha=alpha))
    if kind:
        ax.text(x + CHIP_W / 2, y + 48, kind, fontsize=36, color=INK if accent else TXT, ha="center", va="center", fontweight="bold", alpha=alpha)
    if val:
        ax.text(x + CHIP_W / 2, y + 98, val, fontsize=28, color=GRAY, ha="center", va="center", alpha=alpha)


def draw_ar(fig, t):
    ax = pixel_axes(fig)
    c = min(int(t // CYCLE), len(NEW) - 1)
    u = t - c * CYCLE
    stream = STREAM0 + NEW[:c]
    step = 0 if u < 0.9 else (1 if u < 1.6 else (2 if u < 2.2 else 3))
    labels = ["① 종류를 뽑고", "② 값을 만들고", "③ 끝에 붙인다"]
    for i, lab in enumerate(labels):
        on = step == i + 1
        ax.text(150 + i * 530, 90, lab, fontsize=50, color=INK if on else LINE, fontweight="bold", va="center")
    # 흐름: 마지막 5개만 보인다. 붙이는 동안 왼쪽으로 한 칸 민다
    slide = ease((u - 2.2) / 0.8) if step == 3 else 0.0
    x_right = 1180
    vis = stream[-5:]
    for j, (k, v) in enumerate(vis):
        x = x_right - (len(vis) - j) * (CHIP_W + GAP) - slide * (CHIP_W + GAP)
        a = 1.0 if x > 40 else max(0.0, 1 - (40 - x) / 120)
        chip(ax, x, 220, k, v, alpha=a)
    ax.text(140, 410, "지금까지의 이벤트", fontsize=34, color=GRAY)
    # 모델
    mx, my, mw, mh = 520, 520, 520, 150
    reading = step == 0
    ax.add_patch(FancyBboxPatch((mx, my), mw, mh, boxstyle="round,pad=0,rounding_size=20", fc="#FFFFFF",
                                ec=INK if reading else TXT, lw=6 if reading else 3))
    ax.text(mx + mw / 2, my + mh / 2, "트랜스포머", fontsize=44, color=INK if reading else TXT, ha="center", va="center", fontweight="bold")
    ax.annotate("", xy=(mx + mw / 2, my - 6), xytext=(mx + mw / 2, 380),
                arrowprops=dict(arrowstyle="-|>", color=INK if reading else LINE, lw=5, mutation_scale=40))
    ax.annotate("", xy=(1290, my + mh / 2), xytext=(mx + mw + 8, my + mh / 2),
                arrowprops=dict(arrowstyle="-|>", color=INK if step in (1, 2) else LINE, lw=5, mutation_scale=40))
    # 다음 이벤트 자리
    kind, val = NEW[c]
    ox, oy = 1320, my + mh / 2 - CHIP_H / 2
    if step >= 1:
        # 범주 막대: 두 칸 중 하나가 뽑힌다
        if step == 1:
            for i, (lab, p) in enumerate([("체결", 0.3), ("BBO", 0.7)]):
                yy = 760 + i * 70
                ax.add_patch(Rectangle((1320, yy), 300 * p, 48, color=INK if lab == kind else LINE))
                ax.text(1300, yy + 24, lab, fontsize=30, color=TXT, ha="right", va="center", fontweight="bold" if lab == kind else "normal")
        if step == 2:
            rr = random.Random(int(t * 10))
            spread = 1 - ease((u - 1.6) / 0.5)
            for _ in range(40):
                ax.plot(ox + CHIP_W / 2 + rr.gauss(0, 1) * 150 * spread, oy + 98 + rr.gauss(0, 1) * 110 * spread, "o", color=INK, ms=8, alpha=0.55)
            ax.text(ox + CHIP_W / 2, 900, "확산으로 값을 만든다", fontsize=32, color=INK, ha="center")
        if step == 1:
            ax.text(1470, 950, "범주로 종류를 뽑는다", fontsize=32, color=INK, ha="center")
        show_val = val if step >= 2 and u > 2.0 else ""
        if step == 3:
            # 흐름 끝으로 날아간다
            e = ease((u - 2.2) / 0.8)
            tx, ty = x_right - (CHIP_W + GAP) - (CHIP_W + GAP) * 0, 220
            tx = x_right - (CHIP_W + GAP)
            chip(ax, ox + (tx - ox) * e, oy + (ty - oy) * e, kind, val, accent=True)
        else:
            chip(ax, ox, oy, kind, show_val, accent=True)
    else:
        chip(ax, ox, oy, "?", "", filled=False)
    ax.text(ox + CHIP_W / 2, oy - 28, "다음 이벤트", fontsize=32, color=GRAY, ha="center")


# ---------- (c) atom smoothing ----------
L, R, C, MASS = -1.50, 1.38, -0.02, 0.849


def npdf(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def ncdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


SAMPLES = sorted([random.Random(11 + i).gauss(0, 1) for i in range(46)], key=lambda z: random.Random(int(z * 1e6)).random())


def draw_atom(fig, t):
    ax = fig.add_axes([0.06, 0.15, 0.9, 0.62])
    ax.set_facecolor(PAPER)
    ax.set_xlim(-3.6, 3.6); ax.set_ylim(0, 0.62)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(TXT); ax.spines["bottom"].set_linewidth(2.5)
    ax.set_yticks([]); ax.set_xticks([-3, -2, -1, 0, 1, 2, 3]); ax.tick_params(labelsize=32, colors=GRAY, length=0, pad=10)
    zs = [-3.6 + 7.2 * k / 400 for k in range(401)]
    # 목표 N(0,1) (점선)
    ax.plot(zs, [npdf(z) for z in zs], color=GRAY, lw=3, ls=(0, (6, 6)))
    # 양쪽 꼬리(원래부터 0이 아닌 값들)
    for seg in ([z for z in zs if z <= L], [z for z in zs if z >= R]):
        ax.fill_between(seg, [npdf(z) for z in seg], color=LINE, alpha=0.8, lw=0)
    if t < 1.5:
        phase, u = 1, 0.0
    elif t < 4.0:
        phase, u = 2, ease((t - 1.5) / 2.5)
    elif t < 7.0:
        phase, u = 3, 1.0
    elif t < 8.6:
        phase, u = 4, 1.0
    else:
        phase, u = 5, 1.0
    fold = ease((t - 7.0) / 1.4) if phase >= 4 else 0.0
    # 펴지는 덩어리: 질량 84.9% 를 지키며 [l, r] 로 넓어진다
    if fold < 1:
        uu = max(u, 0.012)
        l, r = C + (L - C) * uu, C + (R - C) * uu
        scale = MASS / max(ncdf(r) - ncdf(l), 1e-6)
        seg = [l + (r - l) * k / 200 for k in range(201)]
        hs = [min(npdf(z) * scale, 0.6) for z in seg]
        a = 1 - fold
        ax.fill_between(seg, hs, color=INK, alpha=0.75 * a, lw=0)
        if phase >= 2:
            ax.axvspan(l, r, ymax=0.06, color=INK, alpha=0.25 * a, lw=0)
    if fold > 0:   # 다시 0으로 접힌 덩어리
        ax.add_patch(Rectangle((C - 0.035, 0), 0.07, 0.6 * fold, color=INK, alpha=0.85))
    if fold > 0.5 or phase == 1:
        ax.text(0.2, 0.56, "84.9%", fontsize=44, color=INK, fontweight="bold", va="center")
    elif u > 0.6:
        ax.text(C, 0.2, "84.9%", fontsize=44, color="#FFFFFF", fontweight="bold", ha="center", va="center", alpha=1 - fold)
    else:
        ax.text(0.2, 0.56, "84.9%", fontsize=44, color=INK, fontweight="bold", va="center", alpha=1 - u / 0.6)
    # 생성: 표본이 떨어지고, 구간 안이면 0으로 모인다
    if phase >= 3:
        for i, z in enumerate(SAMPLES):
            t0 = 4.0 + i * 0.05
            if t < t0:
                continue
            fall = ease((t - t0) / 0.6)
            inside = L < z < R
            x = z + (C - z) * fold if inside else z
            y = 0.5 - 0.48 * fall
            ax.plot([x], [y], "o", color=INK if inside else GRAY, ms=13, alpha=0.9 if fold < 1 or not inside else 0.0)
    msgs = {1: "① 0에 몰린 84.9%", 2: "② N(0,1)의 한 구간으로 편다", 3: "③ 확산 모델이 값을 만든다",
            4: "④ 구간 안이면 정확히 0으로", 5: "④ 구간 안이면 정확히 0으로"}
    fig.text(0.5, 0.89, msgs[phase], fontsize=56, color=INK, ha="center", va="center", fontweight="bold")
    fig.text(0.985, 0.03, "원문 설명을 바탕으로 한 해석", fontsize=28, color=GRAY, ha="right")
    fig.text(0.06, 0.05, "z (분위수 변환한 값)    점선 = 목표 N(0,1)", fontsize=30, color=GRAY)


def step_paths(seed, n, start, drift=0.0, widen=0.0):
    """(매수, 매도) 호가 계단 경로. 이벤트마다 0·±1틱으로 움직이고, widen 만큼 스프레드가 점점 벌어진다."""
    rng = random.Random(seed)
    bid, ask, out = start, start + 2, []
    for i in range(n):
        r = rng.random()
        if r < 0.35:
            move = rng.choice([-1, 1]) + ((1 if drift > 0 else -1) if rng.random() < abs(drift) else 0)
            bid += move; ask += move
        elif r < 0.5:
            ask += 1 if rng.random() < 0.5 + widen else -1
            ask = max(ask, bid + 1)
        out.append((bid, ask))
    return out


ROLL_N, ROLL_FAN, ROLL_AHEAD = 64, 9, 12
ROLL_TRUE = step_paths(7, ROLL_N, 0)
ROLL_GEN = step_paths(11, ROLL_N, 0, drift=0.15, widen=0.12)


def draw_rollout(fig, t):
    ax = pixel_axes(fig)
    x0, x1, y0, y1 = 110, 1690, 120, 860
    lo, hi = -9, 15
    px = lambda i: x0 + (x1 - x0) * i / ROLL_N
    py = lambda v: y1 - (y1 - y0) * (v - lo) / (hi - lo)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="white", edgecolor=LINE, lw=1.5))
    k = int(ease(t / 8.6) * ROLL_N)        # 지금까지 확정된 이벤트 수(끝 1.4초는 정지)

    def steps(path, upto, color, lw):
        for side, ls in ((0, "-"), (1, (0, (6, 4)))):   # 실선 매수, 점선 매도
            ax.plot([px(i) for i in range(upto + 1)], [py(path[0][side])] + [py(path[i][side]) for i in range(upto)],
                    color=color, lw=lw, ls=ls, drawstyle="steps-pre")

    steps(ROLL_TRUE, k, TXT, 2.4)                         # 실제 호가(검정)
    steps(ROLL_GEN, k, INK, 3.6)                          # 모델이 만든 호가(잉크색)
    if k < ROLL_N:                                        # 앞날 후보 부채꼴: 여러 갈래를 흐리게 그려 보고 하나를 고른다
        head = ROLL_GEN[k - 1] if k else (0, 2)
        ahead = min(ROLL_AHEAD, ROLL_N - k)                # 그림 오른쪽 끝을 넘지 않게
        for j in range(ROLL_FAN):                          # 갈래마다 기울기를 달리해 부채꼴로 퍼지게
            fut = step_paths(1000 * k + j, ahead, head[0], drift=-0.6 + 1.2 * j / (ROLL_FAN - 1), widen=0.12)
            fut = [(b, a + head[1] - head[0] - 2) for b, a in fut]
            xs = [px(k + i + 1) for i in range(ahead)]
            for side in (0, 1):
                ax.plot([px(k)] + xs, [py(head[side])] + [py(v[side]) for v in fut], color=INK, lw=1.4,
                        alpha=0.16, drawstyle="steps-pre", ls="-" if side == 0 else (0, (6, 4)))
        ax.add_patch(plt.Circle((px(k), py(head[0])), 9, color=INK))
    # 범례·표기(글자는 크고 적게)
    ax.plot([x0 + 20, x0 + 80], [y0 + 40, y0 + 40], color=TXT, lw=2.4); ax.text(x0 + 95, y0 + 40, "실제 호가", va="center", fontsize=30, color=TXT)
    ax.plot([x0 + 300, x0 + 360], [y0 + 40, y0 + 40], color=INK, lw=3.6); ax.text(x0 + 375, y0 + 40, "모델이 생성한 호가", va="center", fontsize=30, color=INK, weight="bold")
    ax.text(x0 + 760, y0 + 40, "실선 매수 · 점선 매도 · 흐린 갈래 = 모델이 그려 본 앞날", va="center", fontsize=24, color=GRAY)
    ax.text(x0, y1 + 50, "이벤트 →", fontsize=26, color=GRAY, va="center")
    ax.text(x1, y1 + 50, "개념 그림 · 지어낸 데이터", fontsize=24, color=GRAY, ha="right", va="center")


ANIMS = {"traj": (8.0, draw_traj), "ar-loop": (9.0, draw_ar), "atom": (10.0, draw_atom), "rollout": (10.0, draw_rollout)}

if __name__ == "__main__":
    for name in (sys.argv[1:] or ANIMS):
        sec, fn = ANIMS[name]
        render(name, sec, fn)
