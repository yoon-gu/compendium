#!/usr/bin/env python3
"""핵심 대목 세 곳에만 얹는 소리 없는 모션 그래픽(1776x1000, 25fps). 목록은 나레이션에서 언급될 때 하나씩 뜨고
방금 말한 항목이 잉크색으로 칠해진다(<이름>-timing.json, 녹음 뒤 whisper 로 잡는다).

    python3 animate.py            # → stages.mp4, habits.mp4, iphone.mp4 (+ 확인용 *-sheet.png)

- stages.mp4  여섯 단계 여정: 검색창 → 붙여넣기 → 탭 완성 → 에이전트 → Opus 4.5-4.6 → Opus 5.5 (stages-timing.json)
- habits.mp4  Opus 5.5에서 일하는 법 여섯 가지 (habits-timing.json)
- iphone.mp4  맡기고 자리를 뜨면 몇 시간 뒤 앱이 폰에 깔린다, 사용 한도 40% (개념 그림, 12초)
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
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD = "#F4F4F1", "#6B4E2E", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B"


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
    sheet_frames = {int(n * k / 5) + int(FPS * 0.8) for k in range(0, 4)}
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



ON, SUB_ON = "#FFFFFF", "#EADFD3"


def current_of(t, marks):
    return max((k for k in range(len(marks)) if t >= marks[k]), default=-1)


def rows(ax, t, items, marks, top=30, step=160, h=140):
    cur = current_of(t, marks)
    for k, (head, sub) in enumerate(items):
        y = top + k * step
        a = ease((t - marks[k]) / 0.35)
        if a <= 0:
            box(ax, 40, y, 1696, h, ec=SOFT, fc=PAPER, lw=3, r=22)
            label(ax, 100, y + h / 2, str(k + 1), 46, SOFT, bold=True)
            continue
        now = k == cur
        box(ax, 40, y, 1696, h, ec=INK, fc=INK if now else "#FFFFFF", lw=5 if now else 3, r=22, alpha=a)
        label(ax, 100, y + h / 2, str(k + 1), 50, ON if now else INK, bold=True, alpha=a)
        label(ax, 170, y + h * 0.36, head, 42, ON if now else TXT, "left", True, a)
        label(ax, 170, y + h * 0.74, sub, 30, SUB_ON if now else GRAY, "left", False, a)


STAGES = [("ChatGPT = 더 나은 검색창", "내가 짜고, 모르는 것만 묻는다"),
          ("예시 붙여넣기", "싫은 언어(Ruby)를 피하는 비상구"),
          ("Cursor 탭 완성", "이미 쓴 패턴을 이어 쓸 뿐"),
          ("Claude 에이전트 코딩", "말로 시키되 모든 줄을 검토"),
          ("Opus 4.5 · 4.6", "일일이 짚어 주지 않아도 된다, 생산성 약 3배"),
          ("Opus 5.5", "한 단계 위에서: QA · 설계 · 도구")]


def draw_stages(ax, t):
    _, marks = timing("stages", (16.0, [1.0, 3.0, 5.0, 7.0, 9.0, 11.0]))
    rows(ax, t, STAGES, marks)


HABITS = [("QA 중심으로 계획", "코드 리뷰보다 제대로 도는지 확인"),
          ("화면은 여러 안을 한꺼번에", "고르는 일이 일이 된다"),
          ("계획·진행은 모델이 노트에", "저자의 노트 앱에 직접 적는다"),
          ("도구와 대시보드", "번다운 · 취약점 · 성능 모니터링"),
          ("서브에이전트 + 감독", "일을 나눠 주고 감독 에이전트를 둔다"),
          ("쓸모없는 실험도 잔뜩", "아이디어를 모으는 일이 즐겁다")]


def draw_habits(ax, t):
    _, marks = timing("habits", (16.0, [1.0, 3.0, 5.0, 7.0, 9.0, 11.0]))
    rows(ax, t, HABITS, marks)


def draw_iphone(ax, t):
    # 왼쪽: 노트북(일렉트론 앱) → 오른쪽: 폰. 시계가 몇 시간 흐르고, 사용 한도 막대가 40%까지 찬다
    box(ax, 120, 260, 520, 340, ec=TXT, fc="#FFFFFF", lw=4, r=16)
    ax.add_patch(Rectangle((80, 600), 600, 26, color=TXT))
    label(ax, 380, 400, "노트 앱", 44, TXT, bold=True)
    label(ax, 380, 470, "Electron", 32, GRAY)
    u = ease((t - 1.0) / 6.0)
    for k in range(5):
        x = 690 + 110 * k
        a = 1.0 if u * 5 > k else 0.25
        ax.add_patch(Circle((x, 430), 14, color=INK, alpha=a))
    label(ax, 910, 350, "자리를 비운 사이…" if u < 1 else "몇 시간 뒤", 34, GRAY, bold=True)
    box(ax, 1290, 170, 300, 560, ec=TXT, fc="#FFFFFF", lw=5, r=46)
    on = ease((t - 7.2) / 0.6)
    box(ax, 1320, 240, 240, 400, ec=INK, fc=INK, lw=0, r=20, alpha=on)
    label(ax, 1440, 400, "노트 앱", 36, "#FFFFFF", bold=True, alpha=on)
    label(ax, 1440, 460, "Swift", 30, "#EADFD3", alpha=on)
    label(ax, 1440, 690, "QA 해 주세요", 28, INK, bold=True, alpha=ease((t - 8.4) / 0.5))
    label(ax, 120, 800, "월 20달러 구독 · 5시간 사용 한도", 32, TXT, "left", True)
    ax.add_patch(Rectangle((120, 840), 1200, 40, color=SOFT))
    ax.add_patch(Rectangle((120, 840), 1200 * 0.40 * u, 40, color=INK))
    label(ax, 1340, 860, f"{int(round(40 * u))}%", 36, INK, "left", True)
    label(ax, 888, 960, "기능은 다 갖추지 않았지만 작동하는 시제품", 30, GRAY)


ANIMS = {"stages": (lambda: timing("stages", (16.0, []))[0], draw_stages),
         "habits": (lambda: timing("habits", (16.0, []))[0], draw_habits),
         "iphone": (lambda: 12.0, draw_iphone)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ANIMS:
        seconds, draw = ANIMS[name]
        render(name, seconds(), draw)
