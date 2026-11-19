#!/usr/bin/env python3
"""'규칙은 코드로, 판단은 모델로' 회차의 소리 없는 개념 애니메이션 네 편(1776x1000, 25fps). matplotlib 프레임 → ffmpeg.

    python3 animate.py              # → decide, questions, steps, fastpath (.mp4 + 확인용 *-sheet.png)
    python3 animate.py steps        # 하나만

- decide.mp4    그냥 생성(긴 문장 → 해석 코드) vs 결정 호출(보기 다섯 중 하나, 애매하면 unsure → 위로 넘김) (decide-timing.json)
- questions.mp4 세 질문이 '첫째·둘째·셋째'가 들릴 때 하나씩 켜지고 갈 곳(코드·결정 호출)이 붙는다. 마지막에 '셋 다 아니면 모델' (questions-timing.json)
- steps.mp4     고객지원 다섯 단계가 언급될 때마다 코드·결정 호출·모델 세 칸 중 제자리로 들어간다 (steps-timing.json)
- fastpath.mp4  요청 스무 개가 키워드 규칙을 지나 열아홉은 코드로, 하나만 모델로. 하루 백만 건 → 모델 오만 건 (fastpath-timing.json)
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


# ---------- (a) 그냥 생성 vs 결정 호출 ----------
FREE = ["결제 문제로 보입니다만,", "계정이 잠긴 걸 보면", "계정 쪽일 수도 있습니다…"]
CHOICES = ["billing", "technical", "account", "other", "unsure"]


def draw_decide(ax, t):
    dur, m = timing("decide", (30.0, [1.0, 9.0, 16.0, 22.0]))
    box(ax, 40, 30, 1696, 110, ec=LINE, lw=3, r=20)
    label(ax, 80, 85, "문의: \"카드가 두 번 긁혔는데 로그인도 안 돼요\"", 38, TXT, bold=True)
    # 왼쪽: 그냥 생성
    a = ease((t - m[0]) / 0.5)
    label(ax, 60, 200, "그냥 생성", 40, GRAY, bold=True, alpha=max(a, 0.35))
    if a > 0:
        box(ax, 60, 240, 780, 330, ec=LINE, lw=3, r=20, alpha=a)
        shown = (t - m[0] - 0.5) * 16              # 초당 16글자씩 써진다
        for k, ln in enumerate(FREE):
            n = int(min(max(shown - sum(len(x) for x in FREE[:k]), 0), len(ln)))
            if n:
                label(ax, 100, 310 + k * 80, ln[:n], 36, TXT)
        c = ease((t - m[0] - 4.5) / 0.6)
        if c > 0:
            arrow(ax, 450, 590, 450, 650, GRAY, 4, c)
            box(ax, 60, 670, 780, 110, ec=BAD, fc=BADT, lw=4, r=20, alpha=c)
            label(ax, 100, 725, "queue = parse_queue(답)  # ?", 34, BAD, mono=True, alpha=c)
            label(ax, 450, 840, "문장을 다시 해석해야 한다", 36, BAD, "center", True, c)
    # 오른쪽: 결정 호출
    b = ease((t - m[1]) / 0.5)
    label(ax, 940, 200, "결정 호출", 40, INK if b > 0 else GRAY, bold=True, alpha=max(b, 0.35))
    if b > 0:
        pick = 4 if t >= m[2] else -1
        for k, c in enumerate(CHOICES):
            y = 245 + k * 92
            a2 = ease((t - m[1] - 0.25 * k) / 0.4)
            on = k == pick
            col = WARN if k == 4 else INK
            box(ax, 940, y, 420, 74, ec=col, fc=col if on else "#FFFFFF", lw=5 if on else 3, r=37, alpha=a2)
            label(ax, 1150, y + 37, c, 34, "#FFFFFF" if on else col, "center", on, a2, mono=True)
        if pick == 4:
            label(ax, 1390, 650, "← 애매하다", 32, WARN, bold=True, alpha=ease((t - m[2]) / 0.4))
    e = ease((t - m[3]) / 0.6)
    if e > 0:
        arrow(ax, 1150, 715, 1150, 790, WARN, 5, e)
        box(ax, 940, 800, 760, 110, ec=INK, fc=INKT, lw=4, r=20, alpha=e)
        label(ax, 1320, 855, "큰 모델이나 사람에게 넘긴다", 36, INK, "center", True, e)


# ---------- (b) 단계마다 세 가지 질문 ----------
QS = [("성공을 규칙으로 확인할 수 있나?", "형식 · 스키마 · 키워드 · 범위", "code", "코드"),
      ("모델이 규칙을 한 번만 써 줄 수 있나?", "정규식 · JSON 스키마 초안 → 검토 → 커밋", "code", "한 번 쓴 규칙"),
      ("정해진 보기 중 하나를 고르나?", "경로 · 분류 · 예/아니오", "decide", "결정 호출")]


def draw_questions(ax, t):
    dur, m = timing("questions", (40.0, [3.0, 12.0, 22.0, 30.0]))
    cur = max((k for k in range(4) if t >= m[k]), default=-1)
    for k, (q, sub, lane, dest) in enumerate(QS):
        y = 30 + k * 225
        a = ease((t - m[k]) / 0.4)
        if a <= 0:
            box(ax, 40, y, 1696, 190, ec=SOFT, fc=PAPER, lw=3, r=24)
            continue
        now = k == cur
        box(ax, 40, y, 1696, 190, ec=INK, fc="#FFFFFF", lw=6 if now else 3, r=24, alpha=a)
        label(ax, 110, y + 70, f"{k + 1}", 56, INK, "center", True, a)
        label(ax, 180, y + 70, q, 44 if now else 40, TXT, bold=now, alpha=a)
        label(ax, 180, y + 140, sub, 30, GRAY, alpha=a)
        d = ease((t - m[k] - 1.2) / 0.5)
        if d > 0:
            name, col, tint = LANES[lane]
            box(ax, 1220, y + 45, 480, 100, ec=col, fc=tint, lw=4, r=50, alpha=d)
            label(ax, 1460, y + 95, "예 → " + dest, 30 if len(dest) > 6 else 36, col, "center", True, d)
    f = ease((t - m[3]) / 0.5)
    y = 30 + 3 * 225
    if f <= 0:
        box(ax, 40, y, 1696, 190, ec=SOFT, fc=PAPER, lw=3, r=24)
    else:
        box(ax, 40, y, 1696, 190, ec=INK, fc=INKT, lw=6, r=24, alpha=f)
        label(ax, 110, y + 95, "셋 다 아니오", 44, INK, bold=True, alpha=f)
        label(ax, 520, y + 95, "→ 열린 일. 요구를 넘는 가장 작은 모델로", 40, TXT, alpha=f)


# ---------- (c) 고객지원 다섯 단계 ----------
STEPS = [("주문번호 형식 확인", ["code"]), ("의도별로 메시지 보내기", ["code", "decide"]), ("메일에서 송장번호 뽑기", ["code"]),
         ("티켓을 네 창구 중 하나로", ["decide"]), ("고객에게 보낼 답장 쓰기", ["model"])]
LX = {"code": 1010, "decide": 1270, "model": 1530}


def draw_steps(ax, t):
    dur, m = timing("steps", (36.0, [2.0, 7.0, 14.0, 20.0, 25.0, 30.0]))
    for lane, x in LX.items():
        name, col, tint = LANES[lane]
        box(ax, x - 115, 30, 230, 80, ec=col, fc=tint, lw=4, r=40)
        label(ax, x, 70, name, 34, col, "center", True)
        ax.plot([x, x], [125, 870], color=SOFT, lw=3, ls="--", zorder=0)
    cur = max((k for k in range(5) if t >= m[k]), default=-1)
    for k, (s, lanes) in enumerate(STEPS):
        y = 140 + k * 148
        a = ease((t - m[k]) / 0.4)
        if a <= 0:
            box(ax, 40, y, 820, 120, ec=SOFT, fc=PAPER, lw=3, r=20)
            continue
        now = k == cur
        box(ax, 40, y, 820, 120, ec=INK if now else LINE, fc="#FFFFFF", lw=5 if now else 3, r=20, alpha=a)
        label(ax, 80, y + 60, f"{k + 1}. {s}", 38 if now else 36, TXT, bold=now, alpha=a)
        for j, lane in enumerate(lanes):
            u = ease((t - m[k] - 0.6 - j * 1.6) / 0.8)
            if u <= 0:
                continue
            name, col, tint = LANES[lane]
            x = 880 + (LX[lane] - 880) * u
            ax.add_patch(plt.Circle((x, y + 60), 52 if len(lanes) == 2 else 40, color=col, alpha=0.95, zorder=4))
            if lane == "decide" and len(lanes) == 2:
                label(ax, x, y + 60, "나머지", 24, "#FFFFFF", "center", True, u, z=5)
            elif lane == "code" and len(lanes) == 2:
                label(ax, x, y + 60, "환불", 24, "#FFFFFF", "center", True, u, z=5)
    f = ease((t - m[5]) / 0.6)
    if f > 0:
        box(ax, 300, 890, 1176, 90, ec=INK, fc=INKT, lw=4, r=45, alpha=f)
        label(ax, 888, 935, "모델이 꼭 필요한 단계: 다섯 중 하나", 40, INK, "center", True, f)


# ---------- (d) 빠른 길 ----------
def draw_fastpath(ax, t):
    dur, m = timing("fastpath", (40.0, [2.0, 18.0, 26.0]))
    gx = 640
    box(ax, 40, 360, 300, 160, ec=LINE, lw=3, r=20)
    label(ax, 190, 420, "요청", 40, TXT, "center", True)
    label(ax, 190, 470, "20건", 32, GRAY, "center")
    box(ax, gx - 150, 330, 300, 220, ec=OK, fc=OKT, lw=5, r=24)
    label(ax, gx, 400, "키워드 규칙", 38, OK, "center", True)
    label(ax, gx, 455, "환불 · 비밀번호", 28, GRAY, "center")
    label(ax, gx, 500, "몇 ms", 28, GRAY, "center")
    box(ax, 1150, 120, 560, 230, ec=OK, fc=OKT, lw=4, r=24)
    label(ax, 1430, 175, "코드가 끝낸다", 38, OK, "center", True)
    box(ax, 1150, 600, 560, 230, ec=INK, fc=INKT, lw=4, r=24)
    label(ax, 1430, 655, "모델로 간다", 38, INK, "center", True)
    gap = 0.55
    done_code = done_model = 0
    for i in range(20):
        t0 = m[0] + i * gap
        u = t - t0
        if u < 0:
            continue
        to_model = i == 13
        p1 = ease(u / 0.9)                      # 요청 → 규칙
        p2 = ease((u - 1.0) / 1.0)              # 규칙 → 칸
        if p2 >= 1:
            if to_model:
                done_model += 1
            else:
                done_code += 1
            continue
        if p2 <= 0:
            x, y = 340 + (gx - 340) * p1, 440
        else:
            tx, ty = (1200 + (i % 10) * 48, 260 + (i // 10) * 50) if not to_model else (1430, 740)
            x, y = gx + (tx - gx) * p2, 440 + (ty - 440) * p2
        ax.add_patch(plt.Circle((x, y), 18, color=INK if to_model else OK, zorder=5))
    for k in range(done_code):
        j = [i for i in range(20) if i != 13][k]
        ax.add_patch(plt.Circle((1200 + (j % 10) * 48, 260 + (j // 10) * 50), 18, color=OK, zorder=5))
    if done_model:
        ax.add_patch(plt.Circle((1430, 740), 18, color=INK, zorder=5))
    label(ax, 1690, 175, f"{done_code}", 40, OK, "right", True)
    label(ax, 1690, 655, f"{done_model}", 40, INK, "right", True)
    c = ease((t - m[1]) / 0.6)
    if c > 0:
        label(ax, 888, 900, "하루 1,000,000건  →  코드 950,000건  ·  모델 50,000건", 42, TXT, "center", True, c)
    d = ease((t - m[2]) / 0.6)
    if d > 0:
        label(ax, 888, 965, "모델을 바꾸기 전에 이미 1/20", 36, INK, "center", True, d)
        label(ax, 888, 60, "셈을 보이려는 예시 (실측 아님)", 28, GRAY, "center", alpha=d)


ANIMS = {"decide": (timing("decide", (30.0, None))[0], draw_decide), "questions": (timing("questions", (40.0, None))[0], draw_questions),
         "steps": (timing("steps", (36.0, None))[0], draw_steps), "fastpath": (timing("fastpath", (40.0, None))[0], draw_fastpath)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        render(name, *ANIMS[name])
