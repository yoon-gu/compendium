#!/usr/bin/env python3
"""'예측을 넘어 결정과 발견으로' 회차의 소리 없는 개념 애니메이션 네 편(1776x1000, 25fps). matplotlib 프레임 → ffmpeg.

    python3 animate.py              # → uplift, problems, stages, owner (.mp4 + 확인용 *-sheet.png)
    python3 animate.py owner        # 하나만

- uplift.mp4   고객 A·B의 '푸시 받으면/안 받아도' 막대 → 확률로 고르면 A, 차이(2%p vs 8%p)로 고르면 B (uplift-timing.json)
- problems.mp4 점수로는 못 푸는 네 가지가 '첫째·둘째·셋째·넷째'에 맞춰 하나씩 켜진다 (problems-timing.json)
- stages.mp4   이해 → 평가 → 선택 → 전달이 언급될 때 차례로 켜진다 (stages-timing.json)
- owner.mp4    기술(랭커·밴딧·업리프트)은 겹친다 → 자원의 주인으로 갈라 DeciML(서비스 자원)·NeXA(고객 시간) (owner-timing.json)
"""
import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
FONTS = Path.home() / "Library/Fonts"
for f in ["NanumGothic-Regular.ttf", "NanumGothic-Bold.ttf", "NanumGothic-ExtraBold.ttf", "NanumGothicCoding-Regular.ttf", "NanumGothicCoding-Bold.ttf"]:
    if (FONTS / f).exists():
        font_manager.fontManager.addfont(str(FONTS / f))
plt.rcParams.update({"font.family": ["NanumGothic", "DejaVu Sans"], "axes.unicode_minus": False})

W, H, FPS = 1776, 1000, 25
PAPER, INK, TXT, GRAY, LINE, SOFT = "#F4F4F1", "#3F7A66", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF"
OK, OKT, WARN, WARNT, BAD, BADT, INKT = "#4E8F76", "#EAF3EE", "#C9963A", "#F8F0E0", "#C0605A", "#F6E7E5", "#E3EEEA"
MONO = "NanumGothicCoding"
LANES = {"code": ("코드", OK, OKT), "decide": ("결정 호출", WARN, WARNT), "model": ("모델", INK, INKT)}


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


def label(ax, x, y, s, size=34, color=TXT, ha="left", bold=False, alpha=1.0, mono=False, z=3):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va="center", fontweight="bold" if bold else "normal", alpha=alpha,
            family=MONO if mono else None, zorder=z)


def arrow(ax, x1, y1, x2, y2, color=INK, lw=5, alpha=1.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=34, alpha=alpha))


def timing(name, default):
    p = HERE / f"{name}-timing.json"
    if p.exists():
        d = json.loads(p.read_text())
        return d["duration"], d["marks"]
    return default




# ---------- (a) 반응할 사람 vs 달라질 사람 ----------
CUST = [("A", "단골", 30, 28), ("B", "뜸한 고객", 10, 2)]


def draw_uplift(ax, t):
    dur, m = timing("uplift", (40.0, [1.0, 5.0, 14.0, 20.0, 27.0]))
    label(ax, 888, 50, "푸시는 한 통뿐. 누구에게?", 44, TXT, "center", True)
    base, top = 690, 220                      # y 축: 0% → base, 35% → top
    sy = lambda p: base - p / 35 * (base - top)
    ax.plot([60, 1716], [base, base], color=LINE, lw=3)
    for k, (name, sub, yes, no) in enumerate(CUST):
        a = ease((t - m[k]) / 0.6)
        x0 = 160 + k * 820
        label(ax, x0 + 250, 790, f"고객 {name}", 44, TXT if a > 0 else SOFT, "center", True, max(a, 0.3))
        label(ax, x0 + 250, 845, sub, 32, GRAY, "center", alpha=max(a, 0.3))
        if a <= 0:
            continue
        for j, (p, cap, col, tint) in enumerate([(yes, "푸시 받으면", INK, INKT), (no, "안 받아도", GRAY, SOFT)]):
            h = (base - sy(p)) * a
            bx = x0 + j * 270
            box(ax, bx, base - h, 220, h, ec=col, fc=tint, lw=3, r=10, z=2)
            label(ax, bx + 110, base - h - 40, f"{p}%", 44, col, "center", True, a)
            label(ax, bx + 110, base + 36, cap, 26, GRAY, "center", alpha=a)
    # 반응 확률로 고르면 → A
    c = ease((t - m[2]) / 0.5)
    if c > 0 and t < m[4]:
        box(ax, 140, sy(30) - 150, 260, 60, ec=BAD, fc=BADT, lw=3, r=30, alpha=c, z=4)
        label(ax, 270, sy(30) - 120, "확률로 고르면 ✓", 26, BAD, "center", True, c, z=5)
    # 푸시가 만든 차이
    d = ease((t - m[3]) / 0.6)
    if d > 0:
        for k, (name, sub, yes, no) in enumerate(CUST):
            x0 = 160 + k * 820
            gx = x0 + 520
            ax.plot([gx, gx], [sy(no), sy(no) + (sy(yes) - sy(no)) * d], color=OK if k else WARN, lw=10, solid_capstyle="butt", zorder=3)
            ax.plot([x0, gx + 20], [sy(no), sy(no)], color=LINE, lw=2, ls="--", zorder=1)
            label(ax, gx + 30, (sy(yes) + sy(no)) / 2, f"+{yes - no}%p", 40, OK if k else WARN, bold=True, alpha=d)
    e = ease((t - m[4]) / 0.6)
    if e > 0:
        box(ax, 960, sy(10) - 230, 420, 64, ec=OK, fc=OKT, lw=4, r=32, alpha=e, z=4)
        label(ax, 1170, sy(10) - 198, "차이로 고르면 ✓", 28, OK, "center", True, e, z=5)
        label(ax, 888, 945, "반응할 사람이 아니라 달라질 사람에게", 40, INK, "center", True, e)


# ---------- (b) 점수로는 못 푸는 네 가지 ----------
PROBS = [("제약 아래 배분", "푸시가 한 통이라면 누구에게?", "보내지 않을 사람도 정한다"),
         ("증분 효과", "클릭률은 올랐는데 구매는 왜 그대로?", "반응 확률 대신 달라질 정도"),
         ("지면 간 조율", "아침 푸시 상품을 낮에 홈 맨 위에 또?", "지면별 성적 vs 하루 전체 경험"),
         ("발견 지면의 구조", "새 큐레이션 지면마다 서빙을 처음부터?", "서비스 변화 속도를 따라가야")]


def draw_problems(ax, t):
    dur, m = timing("problems", (50.0, [2.0, 12.0, 20.0, 34.0]))
    cur = max((k for k in range(4) if t >= m[k]), default=-1)
    for k, (h, q, sub) in enumerate(PROBS):
        y = 30 + k * 240
        a = ease((t - m[k]) / 0.4)
        if a <= 0:
            box(ax, 40, y, 1696, 210, ec=SOFT, fc=PAPER, lw=3, r=24)
            label(ax, 110, y + 105, f"{k + 1}", 56, SOFT, "center", True)
            continue
        now = k == cur
        box(ax, 40, y, 1696, 210, ec=INK if now else LINE, fc=INKT if now else "#FFFFFF", lw=6 if now else 3, r=24, alpha=a)
        label(ax, 110, y + 105, f"{k + 1}", 56, INK, "center", True, a)
        label(ax, 180, y + 62, h, 44, INK if now else TXT, bold=True, alpha=a)
        label(ax, 180, y + 125, q, 34, TXT, alpha=a)
        label(ax, 180, y + 176, sub, 28, GRAY, alpha=a)


# ---------- (c) 이해 → 평가 → 선택 → 전달 ----------
STAGES = [("이해", "Understanding", ["고객 · 상품을", "표현 · 피처로"]),
          ("평가", "Valuation", ["선택지마다 가치를", "비교 가능한 숫자로"]),
          ("선택", "Selection", ["제약 안에서", "누구에게 · 무엇을"]),
          ("전달", "→ 서비스", ["실제 발송 ·", "노출까지"])]


def draw_stages(ax, t):
    dur, m = timing("stages", (45.0, [2.0, 9.0, 20.0, 30.0]))
    cur = max((k for k in range(4) if t >= m[k]), default=-1)
    for k, (h, en, lines) in enumerate(STAGES):
        x = 40 + k * 430
        a = ease((t - m[k]) / 0.5)
        last = k == 3
        col, tint = (OK, OKT) if last else (INK, INKT)
        if a <= 0:
            box(ax, x, 200, 380, 520, ec=SOFT, fc=PAPER, lw=3, r=26)
            continue
        now = k == cur
        box(ax, x, 200, 380, 520, ec=col, fc=tint if now else "#FFFFFF", lw=6 if now else 3, r=26, alpha=a)
        label(ax, x + 190, 300, h, 64, col, "center", True, a)
        label(ax, x + 190, 380, en, 28, GRAY, "center", alpha=a)
        for j, ln in enumerate(lines):
            label(ax, x + 190, 500 + j * 60, ln, 30, TXT, "center", alpha=a)
        if k:
            arrow(ax, x - 44, 460, x - 4, 460, INK, 5, a)
    label(ax, 888, 100, "문제가 달라도 순서는 같다", 44, TXT, "center", True)
    f = ease((t - m[3] - 2.0) / 0.6)
    if f > 0:
        box(ax, 240, 800, 1296, 110, ec=INK, fc=INKT, lw=4, r=55, alpha=f)
        label(ax, 888, 855, "푸시면 '누구에게 어떤 자원'  ·  추천이면 '슬레이트'", 36, INK, "center", True, f)


# ---------- (d) 자원이 누구 것인가 ----------
def draw_owner(ax, t):
    dur, m = timing("owner", (50.0, [2.0, 8.0, 12.0, 20.0, 24.0, 32.0]))
    a = ease((t - m[0]) / 0.5)
    split = ease((t - m[1]) / 1.0)
    techs = ["랭커", "밴딧", "업리프트"]
    for k, s in enumerate(techs):
        x = 888 + (k - 1) * 260
        box(ax, x - 110, 40, 220, 80, ec=GRAY, fc="#FFFFFF", lw=3, r=40, alpha=a)
        label(ax, x, 80, s, 32, GRAY, "center", True, a)
    if a > 0 and split < 1:
        label(ax, 888, 170, "기술로 나누면 거의 다 겹친다", 34, GRAY, "center", alpha=a * (1 - split))
    if split > 0:
        label(ax, 888, 170, "유한한 자원이 누구 것인가?", 40, TXT, "center", True, split)
        ax.plot([888, 888], [220, 220 + 700 * split], color=LINE, lw=4, ls="--")
    sides = [(m[2], m[3], 70, "서비스의 자원", ["푸시 한 통", "쿠폰 예산", "유료 노출 자리"], "서비스가 먼저 다가간다", "DeciML", "결정", WARN, WARNT),
             (m[4], m[5], 948, "고객의 자원", ["시간", "주의"], "고객이 먼저 찾아 나선다", "NeXA", "발견", OK, OKT)]
    for s0, s1, x, h, items, who, plat, kind, col, tint in sides:
        b = ease((t - s0) / 0.5)
        if b <= 0:
            continue
        box(ax, x, 240, 760, 480, ec=col, fc="#FFFFFF", lw=4, r=26, alpha=b)
        label(ax, x + 380, 300, h, 44, col, "center", True, b)
        for j, it in enumerate(items):
            box(ax, x + 140, 350 + j * 90, 480, 70, ec=col, fc=tint, lw=3, r=35, alpha=ease((t - s0 - 0.4 - 0.5 * j) / 0.4))
            label(ax, x + 380, 385 + j * 90, it, 32, TXT, "center", alpha=ease((t - s0 - 0.4 - 0.5 * j) / 0.4))
        label(ax, x + 380, 670, who, 30, GRAY, "center", alpha=b)
        c = ease((t - s1) / 0.5)
        if c > 0:
            box(ax, x + 130, 770, 500, 150, ec=col, fc=col, lw=4, r=30, alpha=c)
            label(ax, x + 380, 822, plat, 48, "#FFFFFF", "center", True, c)
            label(ax, x + 380, 880, f"{kind} 문제", 32, "#FFFFFF", "center", alpha=c)


ANIMS = {"uplift": (timing("uplift", (40.0, None))[0], draw_uplift), "problems": (timing("problems", (50.0, None))[0], draw_problems),
         "stages": (timing("stages", (45.0, None))[0], draw_stages), "owner": (timing("owner", (50.0, None))[0], draw_owner)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        render(name, *ANIMS[name])
