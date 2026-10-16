#!/usr/bin/env python3
"""핵심 대목 네 곳에만 얹는 소리 없는 모션 그래픽(1776x1000, 25fps)을 matplotlib 으로 그려 ffmpeg 로 굽는다.
화면 디자인과 같은 결: 종이 바탕, 잉크색 하나, 나눔고딕, 글자는 크고 적게. build.py 가 가로 888px 로 줄여 얹는다.

    python3 animate.py            # → trace.mp4, cuj.mp4, traps.mp4, gate.mp4 (+ 확인용 *-sheet.png)
    python3 animate.py cuj        # 하나만

- trace.mp4  트레이스: 같은 답에 이르는 두 풀이. A는 도구 2번·3초, B는 12번·40초 (개념 그림, 10초)
- cuj.mp4    핵심 사용자 여정: 누가·목표·제약·검증 조건 네 칸이 나레이션에서 언급될 때마다 하나씩 뜬다 (cuj-timing.json)
- traps.mp4  네 가지 함정: '첫째…넷째'가 나올 때마다 하나씩 뜨고 방금 말한 함정이 칠해진다 (traps-timing.json)
- gate.mp4   병합 관문: 성공률이 threshold 95%를 넘고 회귀가 없으면 병합, 회귀가 하나라도 있으면 막힌다 (개념 그림, 12초)
"""
import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
FONTS = Path.home() / "Library/Fonts"
for f in ["NanumGothic-Regular.ttf", "NanumGothic-Bold.ttf", "NanumGothic-ExtraBold.ttf", "NanumGothicCoding-Regular.ttf"]:
    if (FONTS / f).exists():
        font_manager.fontManager.addfont(str(FONTS / f))
plt.rcParams.update({"font.family": ["NanumGothic", "DejaVu Sans"], "axes.unicode_minus": False})

W, H, FPS = 1776, 1000, 25
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD = "#F4F4F1", "#1F5C4A", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B"


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def timing(name, default):
    """녹음 뒤 whisper 로 잡은 화면 시작 기준 언급 시각. 파일이 없으면 기본값(미리보기용)."""
    p = HERE / f"{name}-timing.json"
    if p.exists():
        d = json.loads(p.read_text())
        return d["duration"], d["marks"]
    return default


def render(name, seconds, draw):
    out = HERE / f"{name}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
                            stdin=subprocess.PIPE)
    n = int(seconds * FPS)
    sheet_frames = {int(n * k / 5) for k in range(1, 5)}
    shots = []
    for i in range(n):
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=PAPER)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off"); ax.set_facecolor(PAPER)
        draw(ax, i / FPS)
        fig.canvas.draw()
        buf = bytes(fig.canvas.buffer_rgba())
        proc.stdin.write(buf)
        if i in sheet_frames:
            shots.append(buf)
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


def label(ax, x, y, s, size=34, color=TXT, ha="center", bold=False, alpha=1.0):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va="center", fontweight="bold" if bold else "normal", alpha=alpha, zorder=4)


# ---------- (a) 트레이스: 같은 답, 다른 풀이 ----------
def lane(ax, t, y, name, n, t_end, secs, color):
    """시작 → 도구 n번 → 답. 점이 t_end 초에 답에 닿는다. 시계는 secs 초까지 센다."""
    x0, x1 = 300, 1500
    label(ax, 60, y, name, 34, TXT, "left", True)
    ax.plot([x0, x1], [y, y], color=SOFT, lw=10, solid_capstyle="round", zorder=1)
    u = ease(t / t_end) if t_end else 1
    xs = [x0 + (x1 - x0) * (k + 1) / (n + 1) for k in range(n)]
    for k, x in enumerate(xs):
        hit = u >= (k + 1) / (n + 1)
        ax.add_patch(Circle((x, y), 15 if n > 4 else 22, color=color if hit else LINE, zorder=2))
    ax.plot([x0, x0 + (x1 - x0) * u], [y, y], color=color, lw=10, solid_capstyle="round", zorder=1)
    done = u >= 1
    box(ax, x1 + 30, y - 46, 220, 92, ec=INK if done else LINE, fc=INK if done else "#FFFFFF", lw=4, r=46)
    label(ax, x1 + 140, y, "같은 답", 32, "#FFFFFF" if done else GRAY, bold=True)
    label(ax, x0, y + 70, f"도구 {round(n * u) if not done else n}번 · {round(secs * u)}초", 30, color if done else GRAY, "left", done)


def draw_trace(ax, t):
    label(ax, 888, 90, "답안지는 같다, 풀이는 다르다", 46, TXT, bold=True)
    lane(ax, t, 340, "에이전트 A", 2, 1.6, 3, INK)
    lane(ax, t, 640, "에이전트 B", 12, 7.0, 40, BAD)
    if t > 7.6:
        a = ease((t - 7.6) / 0.6)
        label(ax, 888, 900, "트레이스 = 이 걸음을 전부 적은 기록", 38, INK, bold=True, alpha=a)


# ---------- (b) 핵심 사용자 여정: 네 칸이 언급될 때 하나씩 ----------
CUJ = [("누가", ["운영 분석가"]),
       ("목표", ["거래 찾기 → 장부 대조", "→ 회신 초안"]),
       ("제약", ["30초 안에", "사람 손 없이"]),
       ("검증 조건", ["거래 ID가 맞나?", "장부를 먼저 봤나?", "ID 표기를 바꿨나?"])]


def draw_cuj(ax, t):
    _, marks = timing("cuj", (14.0, [2.0, 4.0, 7.0, 9.5, 12.0]))
    label(ax, 888, 70, "핵심 사용자 여정 (CUJ)", 44, TXT, bold=True)
    current = max((k for k in range(4) if t >= marks[k]), default=-1)
    for k, (head, lines) in enumerate(CUJ):
        a = ease((t - marks[k]) / 0.35)
        x, y = 70 + (k % 2) * 830, 150 + (k // 2) * 400
        if a <= 0:
            box(ax, x, y, 806, 370, ec=SOFT, fc=PAPER, lw=3, r=24)
            continue
        now = k == current
        box(ax, x, y, 806, 370, ec=INK, fc="#FFFFFF", lw=6 if now else 3, r=24, alpha=a)
        box(ax, x, y, 806, 90, ec=INK, fc=INK if now else SOFT, lw=0, r=24, alpha=a)
        label(ax, x + 40, y + 45, head, 38, "#FFFFFF" if now else INK, "left", True, a)
        for i, s in enumerate(lines):
            ly = y + 150 + i * 76
            label(ax, x + 40, ly, s, 40, TXT, "left", False, a)
            if k == 3 and len(marks) > 4 and t >= marks[4]:   # '평가 지점이 된다' — 검증 조항에 체크가 붙는다
                c = ease((t - marks[4] - i * 0.25) / 0.3)
                label(ax, x + 740, ly, "✓", 40, INK, bold=True, alpha=c)
    if len(marks) > 4 and t >= marks[4]:
        label(ax, 888, 960, "조항 하나하나가 평가 지점이 된다", 34, INK, bold=True, alpha=ease((t - marks[4]) / 0.5))


# ---------- (c) 네 가지 함정: '첫째…넷째'에 맞춰 ----------
TRAPS = [("시험지를 바꾼다", "→ 시험 묶음을 얼리고 한 번에 하나만"),
         ("1-5점으로 채점한다", "→ 예/아니요로 묻는다"),
         ("청구서를 안 본다", "→ 지연·토큰·비용을 품질과 한 줄에"),
         ("프레임워크마다 따로 만든다", "→ OpenTelemetry + OpenInference 하나로")]


def draw_traps(ax, t):
    _, marks = timing("traps", (20.0, [2.0, 7.0, 9.0, 11.0]))
    current = max((k for k in range(4) if t >= marks[k]), default=-1)
    for k, (head, fix) in enumerate(TRAPS):
        a = ease((t - marks[k]) / 0.35)
        y = 40 + k * 235
        if a <= 0:
            box(ax, 60, y, 1656, 205, ec=SOFT, fc=PAPER, lw=3, r=28)
            label(ax, 150, y + 102, str(k + 1), 56, SOFT, bold=True)
            continue
        now = k == current
        box(ax, 60, y, 1656, 205, ec=INK, fc=INK if now else "#FFFFFF", lw=5 if now else 3, r=28, alpha=a)
        label(ax, 150, y + 102, str(k + 1), 64, "#FFFFFF" if now else INK, bold=True, alpha=a)
        label(ax, 250, y + 70, head, 44, "#FFFFFF" if now else TXT, "left", True, a)
        label(ax, 250, y + 145, fix, 32, "#DDE9E4" if now else GRAY, "left", False, a)


# ---------- (d) 병합 관문 ----------
def pr_run(ax, t, rate, regress):
    """PR 카드가 관문에 들어가 두 조건을 차례로 확인한다. t 는 이 PR 의 0-6초."""
    x = 40 + 120 * ease(t / 1.0)
    box(ax, x, 380, 300, 170, ec=INK, fc="#FFFFFF", lw=5, r=22)
    label(ax, x + 150, 440, "PR", 52, INK, bold=True)
    label(ax, x + 150, 505, "프롬프트 수정", 30, GRAY)
    box(ax, 560, 60, 1180, 820, ec=TXT, fc="#FFFFFF", lw=5, r=28)
    label(ax, 1150, 135, "병합 관문", 48, TXT, bold=True)
    u = ease((t - 1.0) / 1.2)                                 # 성공률 막대가 찬다
    label(ax, 620, 245, "예/아니요 성공률", 40, TXT, "left")
    label(ax, 1680, 245, f"{round(rate * u)}/100", 42, INK, "right", True)
    ax.add_patch(Rectangle((620, 290), 1060, 70, color=SOFT))
    ax.add_patch(Rectangle((620, 290), 1060 * rate / 100 * u, 70, color=INK))
    tx = 620 + 1060 * 0.95
    ax.plot([tx, tx], [270, 380], color=BAD, lw=5)
    label(ax, tx, 410, "threshold 95%", 32, BAD, "right", True)
    if t > 2.3:
        a = ease((t - 2.3) / 0.4)
        label(ax, 620, 520, "회귀 (전에 통과하던 핵심 지표)", 40, TXT, "left", alpha=a)
        label(ax, 1680, 600, "하나 떨어짐" if regress else "0개", 46, BAD if regress else INK, "right", True, a)
    if t > 3.2:
        a = ease((t - 3.2) / 0.4)
        ok = not regress
        box(ax, 900, 700, 500, 120, ec=INK if ok else BAD, fc=INK if ok else BAD, lw=0, r=60, alpha=a)
        label(ax, 1150, 760, "병합" if ok else "막힘", 54, "#FFFFFF", bold=True, alpha=a)


def draw_gate(ax, t):
    first = t < 6.0
    pr_run(ax, t if first else t - 6.0, 96 if first else 97, regress=not first)
    label(ax, 888, 950, "성공률이 threshold를 넘고, 회귀가 없어야 병합", 38, GRAY)


ANIMS = {"trace": (lambda: 10.0, draw_trace), "cuj": (lambda: timing("cuj", (14.0, []))[0], draw_cuj),
         "traps": (lambda: timing("traps", (20.0, []))[0], draw_traps), "gate": (lambda: 12.0, draw_gate)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        seconds, draw = ANIMS[name]
        render(name, seconds(), draw)
