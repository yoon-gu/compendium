#!/usr/bin/env python3
"""쇠구슬이 또렷하게 보이는 루브 골드버그식 구슬 장치 애니메이션(888x500, 25fps, 12초)을 그린다.
구슬이 경사로 세 개를 지그재그로 내려와 도미노를 쓰러뜨리고, 마지막 도미노가 지렛대를 눌러 종을 친다.

    python3 marble_anim.py            # → ../work/marble-run.mp4 (+ 미리보기 ../work/marble-sheet.png)
"""
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SEC = 888, 500, 25, 12
PAPER, INK, STEEL, DARK, GRAY = (244, 244, 241), (138, 28, 43), (120, 124, 130), (20, 20, 20), (107, 107, 104)
OUT = Path(__file__).resolve().parent.parent / "work"
FONT = "/Users/yoon-gu/Library/Fonts/NanumGothic-Bold.ttf"

# 경사로: (x1,y1)→(x2,y2). 구슬은 이 선을 따라 굴러간다
RAMPS = [((40, 60), (560, 150)), ((640, 190), (120, 290)), ((60, 330), (520, 420))]
DOMINO_X = [600, 650, 700, 750]           # 도미노 네 개
BELL = (830, 300)


def lerp(a, b, t):
    return a + (b - a) * t


def ball_pos(t):
    """시간(초)에 따른 구슬 중심 좌표. 경사로 3개(각 2.6초) + 낙하(0.5초) + 도미노 앞 정지."""
    seg = [2.6, 0.5, 2.6, 0.5, 2.6, 0.4]
    if t < seg[0]:
        u = t / seg[0]; u = u * u * 0.6 + u * 0.4            # 가속
        (x1, y1), (x2, y2) = RAMPS[0]; return lerp(x1, x2, u), lerp(y1, y2, u) - 22
    t -= seg[0]
    if t < seg[1]:
        u = t / seg[1]; return 580 + 50 * u, 128 + 60 * u * u            # 낙하
    t -= seg[1]
    if t < seg[2]:
        u = t / seg[2]; u = u * u * 0.6 + u * 0.4
        (x1, y1), (x2, y2) = RAMPS[1]; return lerp(x1, x2, u), lerp(y1, y2, u) - 22
    t -= seg[2]
    if t < seg[3]:
        u = t / seg[3]; return 100 - 50 * u, 268 + 60 * u * u
    t -= seg[3]
    if t < seg[4]:
        u = t / seg[4]; u = u * u * 0.6 + u * 0.4
        (x1, y1), (x2, y2) = RAMPS[2]; return lerp(x1, x2, u), lerp(y1, y2, u) - 22
    t -= seg[4]
    return 520 + min(t / seg[5], 1) * 60, 398               # 도미노를 향해 굴러가 멈춤


def frame(t):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for (x1, y1), (x2, y2) in RAMPS:                      # 경사로
        d.line([(x1, y1), (x2, y2)], fill=DARK, width=8)
        d.line([(x1, y1 + 10), (x2, y2 + 10)], fill=GRAY, width=3)
    d.rectangle([520, 440, 888, 448], fill=DARK)            # 바닥
    hit = max(0.0, t - 9.6)                                 # 도미노 넘어짐 시작 시각
    for i, x in enumerate(DOMINO_X):                        # 도미노: 차례로 넘어진다
        ang = min(max((hit - i * 0.25) / 0.35, 0), 1) * math.radians(70)
        top = (x + 70 * math.sin(ang), 440 - 70 * math.cos(ang))
        d.line([(x, 440), top], fill=INK, width=18)
    # 지렛대와 종: 마지막 도미노가 넘어지면 지렛대가 기울고 종이 흔들린다
    lever = min(max((hit - 1.0) / 0.3, 0), 1)
    d.line([(770, 440), (840, 440 - 60 * lever)], fill=DARK, width=8)
    swing = math.sin((t - 10.9) * 18) * 12 * max(0, 1 - (t - 10.9) / 1.2) if t > 10.9 else 0
    bx, by = BELL[0] + swing, BELL[1]
    d.polygon([(bx - 34, by + 50), (bx + 34, by + 50), (bx + 22, by - 10), (bx, by - 36), (bx - 22, by - 10)], fill=INK)
    d.ellipse([bx - 8, by + 44, bx + 8, by + 60], fill=DARK)
    d.line([(BELL[0], 240), (bx, by - 36)], fill=DARK, width=4)
    if t > 10.9:
        f = ImageFont.truetype(FONT, 34); d.text((bx - 40, by - 100), "땡!", fill=INK, font=f)
    # 쇠구슬: 크고 또렷하게, 하이라이트와 그림자
    x, y = ball_pos(t); r = 22
    d.ellipse([x - r + 6, y + r - 6, x + r + 6, y + r + 4], fill=(200, 200, 196))
    d.ellipse([x - r, y - r, x + r, y + r], fill=STEEL, outline=DARK, width=3)
    d.ellipse([x - r * 0.55, y - r * 0.6, x - r * 0.05, y - r * 0.15], fill=(225, 228, 232))
    f = ImageFont.truetype(FONT, 26); d.text((40, 456), "쇠구슬 하나가 굴러가며 다음 장치를 차례로 건드린다", fill=GRAY, font=f)
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = OUT / "marble-frames"; frames.mkdir(exist_ok=True)
    for i in range(FPS * SEC):
        frame(i / FPS).save(frames / f"f-{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f-%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(OUT / "marble-run.mp4")], check=True)
    sheet = Image.new("RGB", (6 * 300 + 10, 2 * 180 + 10), (153, 153, 153))
    for k, t in enumerate([0.5, 2.0, 3.5, 5.5, 7.0, 8.8, 9.9, 10.3, 10.7, 11.1, 11.5, 11.9]):
        sheet.paste(frame(t).resize((290, 163)), (10 + (k % 6) * 300, 10 + (k // 6) * 180))
    sheet.save(OUT / "marble-sheet.png")
    print(OUT / "marble-run.mp4")


if __name__ == "__main__":
    main()
