#!/usr/bin/env python3
"""실습 기록(lab/runs/<이름>.jsonl)을 터미널 모양 클립(mp4, 1808x1016, 25fps)으로 다시 그린다.

    python3 terminal.py l1-chat                 # → term-l1-chat.mp4 (+ 확인용 term-l1-chat-sheet.png)
    python3 terminal.py l4-agent --speed 1.5    # 실제 간격을 1.5배 빠르게
    python3 terminal.py l6-cache --only usage   # 출력에서 패턴에 맞는 줄만 강조색

- 글자는 기록된 실제 출력 그대로다. 바꾸는 것은 속도뿐: 입력은 타자 효과(글자당 0.04초), 출력 사이 빈 시간은 MAX_GAP 초로 줄인다.
- 화면 1808x1016 은 가로판 클립 자리(904x508)의 두 배라 또렷하게 줄어든다.
- ANSI 색 코드는 지우고, `you>`·`assistant>`·`[tool]`·`[usage]`·`[array]` 머리만 색으로 구분한다.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "lab" / "runs"
W, H, FPS = 1808, 1016, 25
PAD, LH, BAR = 44, 60, 64           # 여백, 줄 높이, 창 제목 줄 높이(macOS 터미널처럼 신호등 셋 + 제목)
COLS = 68                           # 한 줄 글자 수(한글은 2칸). 904px 로 줄어도 읽히게 크게
BG, FG, DIM, PROMPT, ASSIST, TOOL, USAGE, ERR = "#1B1D21", "#E6E6E3", "#8A8D93", "#8FD3A0", "#F2E2A0", "#9CC7F5", "#F0A9A9", "#F0A9A9"
FONT = ImageFont.truetype(str(Path.home() / "Library/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc"), 40, index=0)
FONT_B = ImageFont.truetype(str(Path.home() / "Library/Fonts/D2Coding-Ver1.3.2-20180524-all.ttc"), 40, index=1)
FONT_T = ImageFont.truetype(str(Path.home() / "Library/Fonts/NanumGothic-Regular.ttf"), 26)
TYPE_SEC, MAX_GAP, TAIL = 0.04, 1.2, 2.5
LEAD = 1.5                          # 기준 줄은 나레이션이 그 말을 하기 이 만큼 앞서 찍힌다 — 모델 답이 다 뜬 뒤에 설명이 들리게
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def width(ch):
    return 2 if ord(ch) > 0x2E7F else 1


def wrap(line):
    out, cur, w = [], "", 0
    for ch in line:
        cw = width(ch)
        if w + cw > COLS:
            out.append(cur); cur, w = "", 0
        cur += ch; w += cw
    out.append(cur)
    return out


def color_of(line):
    s = line.lstrip()
    if s.startswith("you>"):
        return PROMPT, FONT_B
    if s.startswith("assistant>"):
        return ASSIST, FONT_B
    if s.startswith("[tool]") or s.startswith("[sub]"):
        return TOOL, FONT
    if s.startswith("[usage]") or s.startswith("[array]") or s.startswith("[harness]"):
        return USAGE, FONT
    if "Error" in s or "Traceback" in s or s.startswith("ERROR"):
        return ERR, FONT
    return FG, FONT


def events(name, speed):
    """기록을 (시각, 글자) 로 편다. 입력은 글자마다 타자 시각을 준다. 긴 빈 시간은 MAX_GAP 으로 줄인다."""
    raw = [json.loads(l) for l in (RUNS / f"{name}.jsonl").open(encoding="utf-8")]
    out, clock, prev, last_in = [], 0.0, None, None
    for e in raw:
        if e["k"] == "cmd":
            text = "$ " + e["s"] + "\n"
            for ch in text:
                out.append((clock, ch)); clock += TYPE_SEC
            clock += 0.6
            prev = e["t"]
            continue
        gap = 0 if prev is None else (e["t"] - prev) / speed
        clock += min(gap, MAX_GAP)
        prev = e["t"]
        if e["k"] == "in":
            last_in = e["s"]
            for ch in e["s"] + "\n":
                out.append((clock, ch)); clock += TYPE_SEC
        elif e["k"] == "out":
            s = ANSI.sub("", e["s"]).replace("\r", "")
            if last_in is not None and s.lstrip("\n").startswith(last_in):   # pty 메아리(입력이 출력으로 되돌아온 것)는 지운다
                s = s.lstrip("\n")[len(last_in):].lstrip("\n")
                last_in = None
            if s.strip().endswith("you>"):           # 프롬프트 뒤 입력은 같은 줄에 이어 쓴다
                s = s.rstrip() + " "
            if s.startswith("\n") and out and out[-1][1] == "\n":
                s = s[1:]                             # 빈 줄 두 개는 하나로
            for ch in s:
                out.append((clock, ch))
    return out, clock + TAIL


def warp(ev, total, name):
    """term-<name>-timing.json 이 있으면: 기록의 기준 줄(정규식 n번째 일치가 끝나는 글자)이 나레이션 단어 시각에 찍히도록
    이벤트 시각을 구간별 선형으로 다시 배치하고, 클립 길이를 화면 길이에 맞춘다."""
    p = HERE / f"term-{name}-timing.json"
    if not p.exists():
        return ev, total
    d = json.loads(p.read_text())
    text = "".join(c for _, c in ev)
    pairs = [(0.0, 0.0)]
    for m in d["marks"]:
        hits = list(re.finditer(m["pat"], text))
        if len(hits) < m["nth"]:
            continue
        nat = ev[hits[m["nth"] - 1].end() - 1][0]
        tm = max(m["t"] - LEAD, 0.5)
        if nat > pairs[-1][0] and tm > pairs[-1][1]:
            pairs.append((nat, tm))
    nat_end = ev[-1][0]
    end_target = max(d["duration"] - TAIL, pairs[-1][1] + 1.0)
    if nat_end > pairs[-1][0]:
        pairs.append((nat_end, end_target))

    def f(x):
        for (a0, b0), (a1, b1) in zip(pairs, pairs[1:]):
            if x <= a1:
                return b0 + (b1 - b0) * (x - a0) / (a1 - a0) if a1 > a0 else b0
        return pairs[-1][1]
    return [(f(c), ch) for c, ch in ev], d["duration"]


def render(name, speed=1.0):
    ev, total = events(name, speed)
    ev, total = warp(ev, total, name)
    cmd = json.loads((RUNS / f"{name}.jsonl").open(encoding="utf-8").readline())["s"]
    title = f"lab — {cmd.split('/')[-1]} — zsh"
    frames = int(total * FPS)
    rows = (H - BAR - 2 * PAD) // LH
    out = HERE / f"term-{name}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
                            stdin=subprocess.PIPE)
    text, k, shots = "", 0, []
    sheet_at = {int(frames * f) for f in (0.15, 0.4, 0.7, 0.97)}
    for i in range(frames):
        t = i / FPS
        while k < len(ev) and ev[k][0] <= t:
            text += ev[k][1]; k += 1
        lines = [w for ln in text.split("\n") for w in wrap(ln)]
        cursor_on = int(t * 2) % 2 == 0
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, BAR], fill="#2A2D33")                       # 창 제목 줄
        for j, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):          # 신호등 (k 는 이벤트 인덱스라 쓰지 않는다)
            d.ellipse([28 + j * 36, BAR // 2 - 11, 50 + j * 36, BAR // 2 + 11], fill=c)
        d.text((W // 2, BAR // 2), title, fill="#B8BBC2", font=FONT_T, anchor="mm")
        shown = lines[-rows:]
        top = BAR + PAD
        for r, ln in enumerate(shown):
            col, font = color_of(ln)
            d.text((PAD, top + r * LH), ln, fill=col, font=font)
        if cursor_on and shown:
            last = shown[-1]
            x = PAD + sum(width(c) for c in last) * 22
            d.rectangle([x + 4, top + (len(shown) - 1) * LH + 8, x + 24, top + (len(shown) - 1) * LH + 50], fill=FG)
        proc.stdin.write(im.tobytes())
        if i in sheet_at:
            shots.append(im.copy())
    proc.stdin.close(); proc.wait()
    assert proc.returncode == 0
    sheet = Image.new("RGB", (W, H), BG)
    for j, s in enumerate(shots[:4]):
        sheet.paste(s.resize((W // 2, H // 2)), ((j % 2) * W // 2, (j // 2) * H // 2))
    sheet.save(HERE / f"term-{name}-sheet.png")
    print(f"{out.name}: {frames} 프레임, {total:.1f}초")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    speed = float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--speed=")), "1.0"))
    for n in args:
        render(n, speed)
