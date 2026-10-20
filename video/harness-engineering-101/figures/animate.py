#!/usr/bin/env python3
"""핵심 대목에 얹는 소리 없는 모션 그래픽(1800x1012 ≈ 가로판 클립 자리 904x508 의 두 배, 25fps).
항목은 나레이션에서 언급될 때 하나씩 뜨고 방금 말한 항목이 잉크색으로 칠해진다(<이름>-timing.json, 녹음 뒤 whisper 로 잡는다).

    python3 animate.py                 # 전부
    python3 animate.py loop cache      # 골라서

- intro.mp4       뇌(모델)와 몸(하니스) 사이를 JSON 배열이 오간다. 사용자 → 배열 → 뇌 → 배열 → 몸 → 세상 (14초 고정)
- array-grow.mp4  수업 1 실측: 턴마다 배열이 자란다 1488 → 1719 바이트, /clear 로 277 (array-grow-timing.json)
- loop.mp4        수업 4 실측: 호출 → stop_reason → 도구 실행 → 결과 붙임 → 다시 호출. 실제 도구 호출 5개가 차례로 켜진다 (loop-timing.json)
- cache.mp4       수업 6 실측: 바퀴마다 cache_read 가 자라는 판 vs 시각 한 줄 때문에 0 인 판 (cache-timing.json)
- errors.mp4      수업 5 실측: 오류 그대로(9번) vs 삼킴(12번) 두 줄의 도구 호출이 시간 순으로 켜진다 (errors-timing.json)
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

HERE = Path(__file__).resolve().parent
FONTS = Path.home() / "Library/Fonts"
for f in ["NanumGothic-Regular.ttf", "NanumGothic-Bold.ttf", "NanumGothic-ExtraBold.ttf", "NanumGothicCoding-Regular.ttf", "NanumGothicCoding-Bold.ttf"]:
    if (FONTS / f).exists():
        font_manager.fontManager.addfont(str(FONTS / f))
plt.rcParams.update({"font.family": ["NanumGothic", "DejaVu Sans"], "axes.unicode_minus": False})
MONO = "NanumGothicCoding"

W, H, FPS = 1808, 1016, 25        # 가로판 클립 자리(904x508)의 꼭 두 배. 캔버스가 1px 깎이면 아래서 종이색으로 채운다
PAPER, INK, TXT, GRAY, LINE, SOFT, BAD, OK, TINT = "#F4F4F1", "#2F5D8A", "#141414", "#6B6B68", "#B9B9B4", "#E4E4DF", "#A23B3B", "#3C7A4A", "#E7EEF5"


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def timing(name, default):
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
        cw, ch = fig.canvas.get_width_height()
        arr = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(ch, cw, 4)
        if (ch, cw) != (H, W):                      # figsize*dpi 의 부동소수 오차로 1px 모자랄 때
            full = np.empty((H, W, 4), dtype=np.uint8); full[:] = (0xF4, 0xF4, 0xF1, 0xFF)
            full[:min(ch, H), :min(cw, W)] = arr[:H, :W]; arr = full
        buf = arr.tobytes()
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


def label(ax, x, y, s, size=34, color=TXT, ha="center", bold=False, alpha=1.0, mono=False):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va="center", fontweight="bold" if bold else "normal", alpha=alpha, zorder=4,
            family=MONO if mono else None)


def arrow(ax, x1, y1, x2, y2, color=INK, lw=4, alpha=1.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, alpha=alpha, mutation_scale=28))


def current_of(t, marks):
    return max((k for k in range(len(marks)) if t >= marks[k]), default=-1)


# ---------------------------------------------------------------- intro
def draw_intro(ax, t):
    """사용자 → [몸] → 배열 → [뇌] → 배열 → [몸] → 세상. 점(메시지)이 길을 따라 흐른다."""
    label(ax, W / 2, 80, "뇌는 글자만 받고 글자만 낸다. 세상을 만지는 것은 몸이다.", 40, GRAY)
    bx, by, bw, bh = 120, 300, 440, 420     # 몸
    nx, ny, nw, nh = 1250, 300, 440, 420    # 뇌
    box(ax, bx, by, bw, bh, INK, TINT, 4, 26); label(ax, bx + bw / 2, by + 60, "몸 = 하니스", 44, INK, bold=True)
    for i, s in enumerate(["배열을 짠다", "도구를 돌린다", "결과를 붙인다"]):
        label(ax, bx + bw / 2, by + 150 + i * 70, s, 32, TXT)
    box(ax, nx, ny, nw, nh, LINE, "#FFFFFF", 4, 26); label(ax, nx + nw / 2, ny + 60, "뇌 = 모델", 44, TXT, bold=True)
    for i, s in enumerate(["글자를 받아", "글자를 낸다", "그뿐"]):
        label(ax, nx + nw / 2, ny + 150 + i * 70, s, 32, GRAY)
    # 배열 통로
    box(ax, 620, 440, 570, 140, INK, "#FFFFFF", 3, 14); label(ax, 905, 510, "JSON 배열", 40, INK, bold=True, mono=True)
    label(ax, 905, 620, "둘 사이 유일한 통로", 30, GRAY)
    # 위 차선(470)은 몸 → 배열 → 뇌로 오른쪽, 아래 차선(550)은 뇌 → 배열 → 몸으로 왼쪽. 점이 가는 길과 같은 방향
    arrow(ax, bx + bw, 470, 620, 470); arrow(ax, 1190, 470, nx, 470, INK)
    arrow(ax, nx, 550, 1190, 550, GRAY); arrow(ax, 620, 550, bx + bw, 550, GRAY)
    # 세상
    box(ax, 120, 800, 440, 130, LINE, SOFT, 3, 18); label(ax, 340, 865, "세상: 파일 · 셸 · 사람", 32, TXT)
    arrow(ax, 340, by + bh, 340, 800, INK)
    # 흐르는 점: 몸 → 배열 → 뇌 → 배열 → 몸 → 세상 (주기 7초)
    u = (t % 7.0) / 7.0
    path = [(bx + bw, 470), (620, 470), (1190, 470), (nx, 470), (nx, 550), (1190, 550), (620, 550), (bx + bw, 550), (340, 720), (340, 800)]
    seg = u * (len(path) - 1); k = int(seg); f = seg - k
    if k < len(path) - 1:
        x = path[k][0] + (path[k + 1][0] - path[k][0]) * f
        y = path[k][1] + (path[k + 1][1] - path[k][1]) * f
        ax.add_patch(Circle((x, y), 16, fc=INK if k < 3 else (GRAY if k < 7 else OK), ec="none", zorder=6))
    stage = ["요청을 배열에 넣는다", "요청을 배열에 넣는다", "배열을 통째로 보낸다", "뇌가 다음 글자를 잇는다", "답(또는 도구 부탁)이 돌아온다", "답(또는 도구 부탁)이 돌아온다",
             "몸이 배열에 붙인다", "몸이 배열에 붙인다", "부탁한 도구를 몸이 실행한다", "부탁한 도구를 몸이 실행한다"][min(k, 9)]
    label(ax, W / 2, 960, stage, 34, INK, bold=True)


# ---------------------------------------------------------------- array-grow (수업 1 실측)
TURNS = [("user", "안녕하세요. 저는 윤구예요…", 1488, False), ("assistant", "안녕하세요, 윤구님! …", 1488, True),
         ("user", "제 이름이 뭐라고 했죠?", 1719, False), ("assistant", "윤구님이라고 말씀하셨어요.", 1719, True),
         ("/clear", "", 0, False), ("user", "제 이름이 뭐죠?", 277, False), ("assistant", "저는 Claude라고 합니다…", 277, True)]


def draw_array_grow(ax, t):
    dur, marks = timing("array-grow", (26.0, [1.0, 3.5, 7.0, 10.0, 14.0, 17.0, 20.0]))
    cur = current_of(t, marks)
    label(ax, W / 2, 70, "배열은 턴마다 통째로 다시 간다. /clear 는 messages = [] 다.", 38, GRAY)
    # 왼쪽: 배열 상자 쌓기
    x0, y0, bw, bh, gap = 140, 160, 760, 92, 14
    shown = []
    for i in range(cur + 1):
        role, s, size, _ = TURNS[i]
        if role == "/clear":
            shown = []
            continue
        shown.append(i)
    for j, i in enumerate(shown):
        role, s, size, is_a = TURNS[i]
        a = ease((t - marks[i]) / 0.5) if i == cur else 1.0
        y = y0 + j * (bh + gap)
        box(ax, x0, y, bw, bh, INK if is_a else LINE, TINT if is_a else "#FFFFFF", 3, 14, alpha=a)
        label(ax, x0 + 20, y + bh / 2, role, 28, INK if is_a else GRAY, ha="left", bold=True, alpha=a, mono=True)
        label(ax, x0 + 200, y + bh / 2, s, 30, TXT, ha="left", alpha=a)
    if cur >= 0 and TURNS[cur][0] == "/clear":
        a = ease((t - marks[cur]) / 0.6)
        label(ax, x0 + bw / 2, y0 + 150, "messages = []", 56, BAD, bold=True, alpha=a, mono=True)
    # 오른쪽: 바이트 막대
    rx, ry, rw = 1060, 220, 440
    label(ax, rx, 170, "len(json.dumps(messages))", 30, GRAY, ha="left", mono=True)
    hist = [TURNS[i][2] for i in range(cur + 1) if TURNS[i][0] == "assistant"]
    cleared = any(TURNS[i][0] == "/clear" for i in range(cur + 1))
    for k, v in enumerate(hist):
        y = ry + k * 110
        frac = v / 1800
        ax.add_patch(Rectangle((rx, y), rw * frac, 70, fc=BAD if cleared and k == len(hist) - 1 else INK, ec="none"))
        label(ax, rx + rw * frac + 20, y + 35, f"{v} bytes", 34, TXT, ha="left", bold=True, mono=True)
        label(ax, rx - 16, y + 35, f"턴 {k + 1}", 28, GRAY, ha="right")
    if cur >= 0:
        role = TURNS[cur][0]
        msg = {"user": "사용자 말을 붙여서 보낸다", "assistant": "답을 붙인다. 다음 턴엔 이것까지 다시 간다",
               "/clear": "서버에 지울 세션이 없다. 내 리스트만 비운다"}[role]
        label(ax, W / 2, 960, msg, 34, INK, bold=True)


# ---------------------------------------------------------------- loop (수업 4 실측)
CALLS = ["run_command(ls -la …)", "run_command(cat README.md; pager.py; …)", "run_command(python3 -m unittest -v)",
         "write_file(pager.py)", "run_command(python3 -m unittest -v)", "end_turn"]


def draw_loop(ax, t):
    dur, marks = timing("loop", (24.0, [2.0, 5.5, 9.0, 12.5, 16.0, 19.5]))
    cur = current_of(t, marks)
    label(ax, W / 2, 64, "에이전트 = 채팅 호출을 감싼 while 루프", 40, GRAY)
    # 왼쪽: 루프 다이어그램 (4 노드)
    nodes = [(330, 230, "call_llm(messages)"), (330, 450, "stop_reason?"), (330, 670, "도구 실행"), (330, 890, "결과를 배열에 붙임")]
    phase = ((t * 1.0) % 4) if cur < len(CALLS) - 1 and cur >= 0 else -1
    for i, (x, y, s) in enumerate(nodes):
        on = int(phase) == i
        box(ax, x - 260, y - 50, 520, 100, INK if on else LINE, TINT if on else "#FFFFFF", 5 if on else 3, 18)
        label(ax, x, y, s, 34 if i != 1 else 36, INK if on else TXT, bold=on, mono=(i != 2 and i != 3))
    for i in range(3):
        arrow(ax, 330, nodes[i][1] + 52, 330, nodes[i + 1][1] - 52)
    ax.plot([330, 330 - 330, 0, 330 - 330, 330], [940, 940, 940, 180, 180], color=INK, lw=4)   # 되돌아가는 선
    ax.plot([0, 0], [940, 180], color=INK, lw=4); arrow(ax, 0, 180, 70, 180)
    label(ax, 650, 450, 'tool_use → 계속', 28, GRAY, ha="left"); label(ax, 650, 500, 'end_turn → 멈춤', 28, GRAY, ha="left")
    # 오른쪽: 실제 도구 호출이 차례로 켜진다
    rx, ry = 960, 170
    label(ax, rx, 130, '"테스트가 하나 실패해. 고쳐 줘."  → 한 턴, 호출 6번', 30, GRAY, ha="left")
    for i, s in enumerate(CALLS):
        y = ry + i * 118
        a = 1.0 if i <= cur else 0.18
        on = i == cur
        done = s == "end_turn"
        box(ax, rx, y, 780, 96, (OK if done else INK) if on else LINE, (("#E6F2E8" if done else TINT) if on else "#FFFFFF"), 5 if on else 3, 16, alpha=a)
        label(ax, rx + 24, y + 48, f"{i + 1}", 30, INK, ha="left", bold=True, alpha=a)
        label(ax, rx + 80, y + 48, s, 30, (OK if done else TXT), ha="left", alpha=a, mono=True, bold=done)
    if 0 <= cur < len(CALLS):
        msg = ["파일 목록부터 본다", "README·코드·테스트를 읽는다", "테스트를 돌려 실패를 본다", "올림 나눗셈으로 고쳐 쓴다", "다시 돌려 3개 통과를 확인", "더 부를 도구가 없다 → 사용자에게"][cur]
        label(ax, W / 2, 985, msg, 34, INK, bold=True)


# ---------------------------------------------------------------- cache (수업 6 실측)
GOOD = [(633, 0), (435, 633), (700, 1068), (486, 1768), (653, 2254)]        # (cache_write, cache_read)
BUST = [(644, 0), (1146, 0), (1555, 0), (2105, 0), (2648, 0)]


def draw_cache(ax, t):
    dur, marks = timing("cache", (28.0, [2.0, 5.0, 8.0, 11.0, 14.0, 19.0]))
    cur = current_of(t, marks)
    label(ax, W / 2, 60, "같은 작업, 같은 모델. 다른 것은 시스템 프롬프트 맨 위 한 줄뿐", 38, GRAY)
    shown = min(cur + 1, 5)
    second = cur >= 5
    scale = 480 / 3000

    def panel(x0, title, data, tint):
        label(ax, x0, 130, title, 34, INK if tint else BAD, ha="left", bold=True, mono=True)
        label(ax, x0, 180, "바퀴  ■ cache_read(10% 값)  ■ cache_write(제값+25%)", 22, GRAY, ha="left", mono=True)
        for k in range(shown):
            w, r = data[k]
            y = 220 + k * 120
            a = ease((t - marks[k]) / 0.5) if k == cur else 1.0
            label(ax, x0, y + 30, f"{k + 1}", 30, GRAY, ha="left", alpha=a)
            ax.add_patch(Rectangle((x0 + 60, y), r * scale, 28, fc=INK, ec="none", alpha=a))
            ax.add_patch(Rectangle((x0 + 60, y + 34), w * scale, 28, fc=BAD, ec="none", alpha=a))
            label(ax, x0 + 70 + max(r, w) * scale, y + 31, f"read {r} · write {w}", 24, TXT, ha="left", alpha=a, mono=True)

    panel(90, "안정된 프롬프트", GOOD, True)
    if second or cur >= 0:
        panel(960, "Current time: 09:52:17", BUST, False)
    if cur >= 0:
        msgs = ["첫 바퀴: 둘 다 처음 보는 바이트. 적중 0은 당연하다", "둘째 바퀴: 왼쪽은 633 토큰을 캐시에서 읽었다. 오른쪽은 0",
                "셋째: 왼쪽 적중이 1068. 오른쪽은 또 전부 새로 쓴다", "넷째: 1768. 오른쪽은 매번 25% 웃돈까지 낸다", "다섯째: 2254. 오른쪽은 끝까지 0",
                "오류는 없다. 청구서에만 찍힌다"]
        label(ax, W / 2, 960, msgs[min(cur, 5)], 34, INK if cur < 5 else BAD, bold=True)


# ---------------------------------------------------------------- errors (수업 5 실측)
HONEST = ["find", "read pager", "read test", "read README", "unittest", "write X denied", "chmod u+w", "write_file", "unittest OK"]
SILENT = ["find", "read pager", "read test", "read README", "pytest→unit", "unittest", "write → \"\"", "unittest X", "cat; chmod", "write_file", "unittest OK", "chmod 444"]


def draw_errors(ax, t):
    dur, marks = timing("errors", (26.0, [1.0, 9.0, 18.0]))
    cur = current_of(t, marks)
    label(ax, W / 2, 60, "읽기 전용 pager.py 를 고치라고 했다. 도구가 실패를 어떻게 전하느냐에 따라", 36, GRAY)
    # 두 줄의 도구 호출이 시간순으로 켜진다 (1단계: 왼쪽 켜짐, 2단계: 오른쪽 켜짐, 3단계: 결론)
    def row(y, title, calls, color, on, hl):
        label(ax, 90, y, title, 34, color, ha="left", bold=True)
        n = len(calls) if on else 0
        for i, s in enumerate(calls):
            x = 90 + i * 136
            a = 1.0 if i < n else 0.15
            bad = " X" in s or "\"\"" in s
            ax.add_patch(Circle((x + 40, y + 90), 30, fc=(BAD if bad else (OK if "OK" in s else color)), ec="none", alpha=a))
            label(ax, x + 40, y + 90, str(i + 1), 26, "#FFFFFF", bold=True, alpha=a)
            label(ax, x + 40, y + 150 + (36 if i % 2 else 0), s, 20, TXT, alpha=a, mono=True)
        if on:
            label(ax, 1700, y, hl, 34, color, ha="right", bold=True)

    row(170, "오류를 그대로 돌려준다", HONEST, INK, cur >= 0, "9번 · 23초")
    row(470, "실패를 삼킨다 (빈 문자열)", SILENT, BAD, cur >= 1, "12번 · 18초")
    if cur >= 0:
        msg = ["6번째에서 Permission denied 를 받자마자 chmod. 한 바퀴 만에 회복", "7번째 쓰기가 성공한 줄 알고 테스트 → 그대로 실패 → 탐정 놀이 세 바퀴",
               "둘 다 고쳤다. 하지만 삼킨 쪽은 운이 좋았다 — 저자의 MI Copilot 은 파일을 망가뜨렸다"][min(cur, 2)]
        label(ax, W / 2, 920, msg, 32, INK if cur < 2 else BAD, bold=True)


ALL = {"intro": (14.0, draw_intro), "array-grow": (None, draw_array_grow), "loop": (None, draw_loop), "cache": (None, draw_cache), "errors": (None, draw_errors)}
DEFAULTS = {"array-grow": 26.0, "loop": 24.0, "cache": 28.0, "errors": 26.0}

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ALL)
    for n in names:
        sec, fn = ALL[n]
        if sec is None:
            sec = timing(n, (DEFAULTS[n], None))[0]
        render(n, sec, fn)
