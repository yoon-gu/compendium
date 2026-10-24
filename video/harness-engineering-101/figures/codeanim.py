#!/usr/bin/env python3
"""코드 화면을 '직접 타이핑하는' 클립(mp4, 1808x1016, 25fps)으로 만든다. 설명이 그 줄을 말할 때 그 줄이 쳐지도록
code-<이름>-timing.json({duration, marks:[{t, line}]}, timing.py 가 만든다)에 맞춰 타자 속도를 구간별로 조절한다.

    python3 codeanim.py                      # make.py 의 CODE_SPECS 전부 → code-<이름>.mp4 (+ code-<이름>-last.png 마지막 프레임)
    python3 codeanim.py code-l1 code-l4-loop

- 타자 효과음: 글자가 쳐지는 시각마다 짧은 클릭(합성 소음, 저작권 없음)을 넣은 code-<이름>-keys.wav 를 함께 만든다.
  영상에 섞는 것은 ../../sfx.py (build.py 는 클립을 무음으로 얹으므로 빌드 뒤에 한 번 더 돌린다).

- 글자·색·줄 접기·수업 표시 줄은 make.py 의 SVG 와 같다(code_rows, tokens 를 그대로 쓴다).
- 타이밍 파일이 없으면 글자당 0.03초로 친다. 줄이 14개를 넘으면 터미널처럼 아래로 흘러 치는 줄이 보이게 한다.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make  # noqa: E402  (import 만으로는 SVG 를 쓰지 않는다)

W, H, FPS = 1808, 1016, 25
PAD, LH, SIZE, ROWS_VISIBLE = 40, 60, 40, 15
BG, NUM, HL = "#1B1D21", "#6B6F76", (0x2F, 0x5D, 0x8A, 90)
FONT = ImageFont.truetype(str(Path.home() / "Library/Fonts/NanumGothicCoding-Regular.ttf"), SIZE)
FONT_B = ImageFont.truetype(str(Path.home() / "Library/Fonts/NanumGothicCoding-Bold.ttf"), SIZE)
TYPE_SEC, LEAD, TAIL = 0.03, 0.3, 1.0


def schedule(rows, name):
    """각 줄의 '다 쳐진 시각'을 정한다. 타이밍 파일의 (t, line) 기준점 사이는 글자 수에 비례해 배분."""
    counts = [max(len(txt), 1) for _, txt, _ in rows]
    cum = [0]
    for c in counts:
        cum.append(cum[-1] + c)
    total = cum[-1]
    p = HERE / f"{name}-timing.json"
    if not p.exists():
        return [LEAD + cum[i + 1] * TYPE_SEC for i in range(len(rows))], LEAD + total * TYPE_SEC + TAIL, []
    d = json.loads(p.read_text())
    pts, pos, anchors = [(0, LEAD)], 0, []
    for m in d["marks"]:
        hit = next((i for i in range(pos, len(rows)) if m["line"] in rows[i][1]), None)
        if hit is None or m["t"] <= pts[-1][1]:
            continue
        pts.append((cum[hit + 1], m["t"])); pos = hit + 1
        # 설명 중인 줄: 접힌 이어짐 줄(번호 None)까지 한 덩어리
        last = hit
        while last + 1 < len(rows) and rows[last + 1][0] is None:
            last += 1
        anchors.append((m["t"], hit, last))
    end_t = max(d["duration"] - TAIL, pts[-1][1] + 0.5)
    if total > pts[-1][0]:
        pts.append((total, min(end_t, pts[-1][1] + (total - pts[-1][0]) * 0.06)))

    def f(x):
        for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
            if x <= a1:
                return b0 + (b1 - b0) * (x - a0) / (a1 - a0) if a1 > a0 else b0
        return pts[-1][1]
    return [f(cum[i + 1]) for i in range(len(rows))], d["duration"], anchors


def keys_wav(rows, starts, ends, total, dest, sr=24000):
    """글자마다 클릭 하나. 띄어쓰기는 낮고 둔한 소리(스페이스바), 나머지는 짧은 노이즈 버스트. 세기·높이를 조금씩 흔든다."""
    import wave
    import numpy as np
    rng = np.random.default_rng(3)
    out = np.zeros(int(total * sr) + sr, dtype=np.float32)
    t_click = np.arange(int(0.028 * sr)) / sr
    for (no, txt, hl), a, z in zip(rows, starts, ends):
        n = max(len(txt), 1)
        for k, ch in enumerate(txt):
            t = a + (z - a) * (k + 0.5) / n
            i = int(t * sr)
            if ch == " ":
                burst = np.sin(2 * np.pi * 110 * t_click) * np.exp(-t_click / 0.008) * 0.5
            else:
                tone = 1800 + rng.uniform(-500, 900)
                burst = (rng.standard_normal(len(t_click)) * 0.6 + np.sin(2 * np.pi * tone * t_click) * 0.4) * np.exp(-t_click / 0.004)
            burst *= rng.uniform(0.18, 0.32)
            out[i:i + len(burst)] += burst[:len(out) - i]
    out = np.clip(out, -1, 1)
    with wave.open(str(dest), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype("<i2").tobytes())


def render(name):
    rows = make.spec_rows(name)
    ends, total, anchors = schedule(rows, name)
    starts = [LEAD] + ends[:-1]
    keys_wav(rows, starts, ends, total, HERE / f"{name}-keys.wav")
    boxes = [(t0, (anchors[i + 1][0] if i + 1 < len(anchors) else total), a, z) for i, (t0, a, z) in enumerate(anchors)]   # 설명 중인 줄 네모
    out = HERE / f"{name}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
                            stdin=subprocess.PIPE)
    n = int(total * FPS)
    last = None
    for fi in range(n):
        t = fi / FPS
        # 각 줄에서 지금까지 쳐진 글자 수
        typed = []
        for (no, txt, hl), a, z in zip(rows, starts, ends):
            if t >= z:
                typed.append(len(txt))
            elif t <= a:
                typed.append(0)
            else:
                typed.append(int(len(txt) * (t - a) / (z - a)))
        cur = max([i for i, k in enumerate(typed) if k > 0] + [0])
        first = max(0, cur - ROWS_VISIBLE + 1) if len(rows) > ROWS_VISIBLE else 0
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im, "RGBA")
        box_rows = next(((a, z) for t0, t1, a, z in boxes if t0 <= t < t1), None)
        for r, i in enumerate(range(first, min(len(rows), first + ROWS_VISIBLE))):
            no, txt, hl = rows[i]
            y = PAD + r * LH
            if hl and typed[i] > 0:
                d.rectangle([12, y - 6, W - 12, y + LH - 10], fill=HL)
            if no is not None and typed[i] > 0:
                d.text((PAD, y), f"{no:3d}", fill=NUM, font=FONT)
            x0, x = PAD + 90, PAD + 90
            shown, done = txt[:typed[i]], ""
            for tok, col in make.tokens(txt):
                if not shown:
                    break
                part = tok[:len(shown)]; shown = shown[len(part):]
                d.text((x, y), part, fill=col, font=FONT)
                done += part; x = x0 + d.textlength(done, font=FONT)   # 글꼴 실제 폭으로 다음 토큰 자리를 잡는다
            if i == cur and typed[i] < len(txt) or (i == cur and t < ends[-1]):
                if int(t * 2) % 2 == 0:
                    d.rectangle([x + 2, y + 4, x + 20, y + LH - 14], fill="#E6E6E3")
        if box_rows:
            a, z = box_rows
            if a < first + ROWS_VISIBLE and z >= first:
                ya = PAD + (max(a, first) - first) * LH - 8; yz = PAD + (min(z, first + ROWS_VISIBLE - 1) - first + 1) * LH - 6
                grow = min(1.0, (t - next(t0 for t0, t1, aa, zz in boxes if (aa, zz) == (a, z))) / 0.25)   # 0.25초 동안 펼쳐지는 네모
                d.rounded_rectangle([PAD + 70, ya, PAD + 70 + (W - PAD * 2 - 70) * grow, yz], radius=10, outline=(0x8F, 0xB4, 0xDC, 230), width=4,
                                    fill=(0x8F, 0xB4, 0xDC, 28))
        proc.stdin.write(im.tobytes()); last = im
    proc.stdin.close(); proc.wait()
    assert proc.returncode == 0
    last.save(HERE / f"{name}-last.png")
    print(f"{out.name}: {n} 프레임, {total:.1f}초, 줄 {len(rows)}개")


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(make.CODE_SPECS)
    for nm in names:
        render(nm)
