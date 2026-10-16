#!/usr/bin/env python3
"""핵심 대목 네 곳에만 얹는 소리 없는 모션 그래픽(1776x1000, 25fps). 항목이 나레이션에서 언급될 때마다 하나씩 뜨고,
방금 말한 항목은 잉크색으로 칠해진다. 언급 시각은 녹음 뒤 whisper 로 잡아 <이름>-timing.json 에 적는다.

    python3 animate.py            # → eras.mp4, brain.mp4, agents.mp4, week.mp4 (+ 확인용 *-sheet.png)
    python3 animate.py brain      # 하나만

- eras.mp4    마케팅 다섯 시대와 실험 속도 (eras-timing.json)
- brain.mp4   두뇌 폴더의 파일 여섯 (brain-timing.json)
- agents.mp4  고객 언어 에이전트 둘레의 나머지 다섯 에이전트 (agents-timing.json)
- week.mp4    회계 사무소 캠페인의 월·화·수·2주 뒤 (week-timing.json)
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
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD = "#F4F4F1", "#2B4C7E", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B"


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



def current_of(t, marks):
    return max((k for k in range(len(marks)) if t >= marks[k]), default=-1)


def card(ax, x, y, w, h, a, now, r=26):
    if a <= 0:
        box(ax, x, y, w, h, ec=SOFT, fc=PAPER, lw=3, r=r)
        return False
    box(ax, x, y, w, h, ec=INK, fc=INK if now else "#FFFFFF", lw=5 if now else 3, r=r, alpha=a)
    return True


ON, SUB_ON = "#FFFFFF", "#DCE4F0"


# ---------- (a) 다섯 시대 ----------
ERAS = [("매드맨 시대", "1950-1990년대 · TV·신문, 큰 예산", "1년에 몇 번", 0.06),
        ("디지털 마케터", "2000년대 · 클릭을 셀 수 있게", "한 달에 몇 번", 0.16),
        ("그로스 해커", "2010년대 · 퍼널·A/B, 엔지니어를 기다림", "일주일에 몇 번", 0.30),
        ("AI 보조 마케터", "2022년 말 · 초안만 빨라짐", "그대로", 0.30),
        ("마케팅 엔지니어", "지금 · 아이디어 낸 사람이 만든다", "하루에 수십 번", 1.0)]


def draw_eras(ax, t):
    _, marks = timing("eras", (14.0, [1.0, 3.5, 6.0, 8.5, 11.0]))
    cur = current_of(t, marks)
    for k, (name, sub, speed, frac) in enumerate(ERAS):
        y = 30 + k * 190
        a = ease((t - marks[k]) / 0.35)
        if not card(ax, 40, y, 1696, 165, a, k == cur):
            continue
        now = k == cur
        label(ax, 80, y + 58, name, 44, ON if now else TXT, "left", True, a)
        label(ax, 80, y + 120, sub, 30, SUB_ON if now else GRAY, "left", False, a)
        bx, bw = 1000, 520
        ax.add_patch(Rectangle((bx, y + 95), bw, 30, color=SOFT if not now else "#3E5F92", alpha=a))
        ax.add_patch(Rectangle((bx, y + 95), bw * frac * ease((t - marks[k]) / 0.8), 30, color=ON if now else INK, alpha=a))
        label(ax, 1696, y + 55, speed, 38, ON if now else INK, "right", True, a)


# ---------- (b) 두뇌 폴더의 파일 여섯 ----------
BRAIN = [("START-HERE.md", "모든 에이전트가 먼저 읽는 한 쪽"), ("company/customer-fit.md", "누가 사고 누가 남는가 — 아주 구체적으로"),
         ("company/offers.md", "무엇을 얼마에, 무엇을 약속해도 되나"), ("brand/voice.md", "좋았던 광고·퇴짜 놓은 광고와 그 이유"),
         ("brand/founder-opinions.md", "창업자의 강한 의견 — 남이 못 베끼는 것"), ("decisions/failed-campaigns.md", "돈을 치른 실패의 교훈")]


def draw_brain(ax, t):
    _, marks = timing("brain", (16.0, [1.0, 3.0, 5.0, 7.0, 9.0, 11.0]))
    cur = current_of(t, marks)
    for k, (fn, desc) in enumerate(BRAIN):
        y = 25 + k * 160
        a = ease((t - marks[k]) / 0.35)
        if not card(ax, 40, y, 1696, 140, a, k == cur, r=22):
            label(ax, 100, y + 70, str(k + 1), 48, SOFT, bold=True)
            continue
        now = k == cur
        label(ax, 100, y + 70, str(k + 1), 52, ON if now else INK, bold=True, alpha=a)
        ax.text(170, y + 48, fn, fontsize=36, color=ON if now else TXT, ha="left", va="center", fontweight="bold",
                family=["NanumGothicCoding", "NanumGothic"], alpha=a, zorder=4)
        label(ax, 170, y + 104, desc, 32, SUB_ON if now else GRAY, "left", False, a)


# ---------- (c) 나머지 다섯 에이전트 ----------
AGENTS = [("구매 계기", "수요가 생기는 순간"), ("검색", "사기 직전의 질문"), ("크리에이티브", "서로 다른 광고"),
          ("놓친 거래", "다시 열릴 조건"), ("성과", "월요일 메모")]
POS = [(888, 140), (1460, 380), (1250, 820), (526, 820), (316, 380)]


def draw_agents(ax, t):
    _, marks = timing("agents", (14.0, [1.0, 3.5, 6.0, 8.5, 11.0]))
    cur = current_of(t, marks)
    cx, cy = 888, 500
    for k, ((name, sub), (x, y)) in enumerate(zip(AGENTS, POS)):
        a = ease((t - marks[k]) / 0.35)
        ax.plot([cx, x], [cy, y], color=INK if a > 0 else SOFT, lw=4 if a > 0 else 3, zorder=1, alpha=max(a, 0.6))
        if not card(ax, x - 210, y - 85, 420, 170, a, k == cur, r=40):
            continue
        now = k == cur
        label(ax, x, y - 22, name, 42, ON if now else INK, bold=True, alpha=a)
        label(ax, x, y + 40, sub, 30, SUB_ON if now else GRAY, alpha=a)
    ax.add_patch(Circle((cx, cy), 170, color=INK, zorder=2))
    label(ax, cx, cy - 30, "고객 언어", 42, ON, bold=True)
    label(ax, cx, cy + 32, "에이전트", 42, ON, bold=True)


# ---------- (d) 캠페인 하나의 일주일 ----------
WEEK = [("월", ["고객의 말: \"실제로 돈을 벌었는지 모르겠다\"", "무료 수익성 점검 제안 승인"]),
        ("화", ["광고 세 가지 · 이익 계산기 페이지", "옛 잠재 고객 60명에게 편지 초안"]),
        ("수", ["사람이 한자리에서 검토", "지킬 수 없는 약속 하나 빼고 $2,000 시험"]),
        ("2주 뒤", ["지출 → 점검 예약 → 계약", "계산기 페이지가 최고, 표본은 아직 작다"])]


def draw_week(ax, t):
    _, marks = timing("week", (20.0, [1.0, 5.0, 10.0, 15.0]))
    cur = current_of(t, marks)
    for k, (day, lines) in enumerate(WEEK):
        y = 30 + k * 240
        a = ease((t - marks[k]) / 0.35)
        if not card(ax, 40, y, 1696, 215, a, k == cur):
            label(ax, 170, y + 107, day, 46, SOFT, bold=True)
            continue
        now = k == cur
        label(ax, 170, y + 107, day, 52, ON if now else INK, bold=True, alpha=a)
        for i, s in enumerate(lines):
            label(ax, 330, y + 70 + i * 76, s, 36, ON if now else TXT, "left", i == 0, a)


ANIMS = {"eras": (lambda: timing("eras", (14.0, []))[0], draw_eras), "brain": (lambda: timing("brain", (16.0, []))[0], draw_brain),
         "agents": (lambda: timing("agents", (14.0, []))[0], draw_agents), "week": (lambda: timing("week", (20.0, []))[0], draw_week)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        seconds, draw = ANIMS[name]
        render(name, seconds(), draw)
