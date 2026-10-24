#!/usr/bin/env python3
"""2편 모션 그래픽 세 편. animate.py 의 render·도형 도우미를 그대로 쓴다. 표시 시각은 <이름>-timing.json(timing.py)에서.

    python3 animate2.py                 # pile subagent events
    python3 animate2.py subagent
"""
import sys

from matplotlib.patches import Rectangle

import animate as A
from animate import BAD, GRAY, H, INK, LINE, OK, TINT, TXT, W, arrow, box, current_of, ease, label, timing

SOFT = "#ECECE8"


# ------------------------------------------------------------ pile: 바퀴마다 쌓이는 배열
ROUNDS = [("read_file(build.log)", 6.0), ("run_command(grep …)", 2.2), ("read_file(pager.py)", 1.6),
          ("run_command(tests)", 3.4), ("read_file(README.md)", 1.2)]


def draw_pile(ax, t):
    dur, marks = timing("pile", (20.0, [1.0, 4.0, 7.0, 10.0, 13.0]))
    cur = current_of(t, marks)
    label(ax, W / 2, 56, "바퀴마다 모델의 답(얇은 줄)과 도구 결과(두꺼운 덩어리)가 붙는다", 34, GRAY)
    x0, y, bw = 160, 110, 900
    box(ax, x0, y, bw, 54, LINE, "#FFFFFF", 3, 10)
    label(ax, x0 + 20, y + 27, "user: 빌드가 왜 깨졌는지 알려 줘", 26, TXT, ha="left")
    y += 64
    for i, (call, size) in enumerate(ROUNDS[:cur + 1]):
        a = ease((t - marks[i]) / 0.5) if i == cur else 1.0
        box(ax, x0, y, bw, 36, INK, TINT, 3, 8, alpha=a)
        label(ax, x0 + 20, y + 18, f"assistant: tool_use {call}", 22, INK, ha="left", alpha=a, mono=True)
        y += 42
        h = 26 * size
        box(ax, x0, y, bw, h, BAD, "#FBEFEF", 3, 8, alpha=a)
        label(ax, x0 + 20, y + min(h / 2, 30), "tool_result", 22, BAD, ha="left", alpha=a, mono=True)
        y += h + 10
    # 오른쪽: 매 바퀴 통째로 다시 보내는 양
    total = sum(26 * s + 42 for _, s in ROUNDS[:cur + 1]) + 64
    rx = 1200
    label(ax, rx, 140, "이번 호출에 보내는 양", 28, GRAY, ha="left")
    ax.add_patch(Rectangle((rx, 180), 120, max(4, total * 0.95), fc=BAD, ec="none", alpha=0.85))
    label(ax, rx + 140, 180 + total * 0.95 / 2, f"바퀴 {max(cur + 1, 0)}", 32, TXT, ha="left", bold=True)
    label(ax, W / 2, 975, "1편에서 본 대로, 배열은 매 바퀴 통째로 다시 간다", 30, INK, bold=True)


# ------------------------------------------------------------ subagent: 빈 배열로 도는 같은 루프 (l8-agent 실측)
SUB = ["find . -type f …", "rg -n 'requests|urllib…'", "cat net/http.py net/backoff.py …", "cat catalog/*.py …",
       "cat cart/*.py tests/…", "cat search · warehouse · …", "rg -n 'import|request_json…'", "cat orders/webhooks.py …"]


def draw_subagent(ax, t):
    dur, marks = timing("subagent", (30.0, [1.0, 4.0, 12.0, 16.0, 20.0]))
    # marks: 0 부모가 agent 부름, 1 자식 배열 생김, 2 보고가 돌아옴, 3 자식 배열 버림, 4 부모 계속
    cur = current_of(t, marks)
    label(ax, W / 2, 56, "서브에이전트 = 빈 배열에서 도는 같은 루프. 답 한 덩어리만 돌아온다", 34, GRAY)
    # 부모 배열
    px, pw = 80, 700
    label(ax, px, 120, "부모 배열", 32, INK, ha="left", bold=True)
    rows = [("user", "HTTP 호출을 모두 찾아 표로", LINE), ("assistant", 'tool_use: agent(task="…")', INK)]
    if cur >= 2:
        rows.append(("user", "tool_result: 보고서 한 덩어리", OK))
    if cur >= 4:
        rows.append(("assistant", "표로 정리해 답한다", LINE))
    for i, (role, s, c) in enumerate(rows):
        y = 160 + i * 96
        on = (cur == 0 and i == 1) or (cur in (2, 3) and i == 2)
        box(ax, px, y, pw, 80, c, TINT if c == INK else ("#E6F2E8" if c == OK else "#FFFFFF"), 5 if on else 3, 12)
        label(ax, px + 20, y + 40, role, 24, INK, ha="left", bold=True, mono=True)
        label(ax, px + 190, y + 40, s, 25, TXT, ha="left", mono=i == 1)
    label(ax, px, 960, "부모 배열 38,515 bytes 로 끝", 30, INK, ha="left", bold=True, alpha=1.0 if cur >= 4 else 0.0)
    # 자식 배열
    cx, cw = 960, 780
    if 1 <= cur <= 3:
        fade = 1.0 - ease((t - marks[3]) / 1.0) * 0.85 if cur == 3 else 1.0
        label(ax, cx, 120, "자식 배열 (새로 비어 있는 배열)", 32, GRAY, ha="left", bold=True, alpha=fade)
        box(ax, cx, 160, cw, 64, LINE, "#FFFFFF", 3, 10, alpha=fade)
        label(ax, cx + 20, 192, "user: 작업 디렉터리는 … 이다. HTTP 호출을 찾아라 …", 22, TXT, ha="left", alpha=fade)
        span = (marks[2] - marks[1]) if len(marks) > 2 else 8.0
        n = len(SUB) if cur >= 2 else int(min(len(SUB), (t - marks[1]) / max(span, 0.1) * len(SUB) + 1))
        for i in range(n):
            y = 236 + i * 72
            box(ax, cx + 30, y, cw - 30, 60, LINE, SOFT, 2, 8, alpha=fade)
            label(ax, cx + 50, y + 30, f"[sub] {SUB[i]}", 21, GRAY, ha="left", mono=True, alpha=fade)
        if cur >= 2:
            label(ax, cx, 236 + len(SUB) * 72 + 30, "140,121 bytes → 버림", 30, BAD if cur == 3 else GRAY, ha="left", bold=True, alpha=fade)
    if cur == 2:      # 보고 한 덩어리가 부모로
        u = ease((t - marks[2]) / 1.2)
        x = cx - (cx - (px + pw)) * u
        box(ax, x - 200, 400, 200, 70, OK, "#E6F2E8", 4, 12)
        label(ax, x - 100, 435, "보고서", 26, OK, bold=True)


# ------------------------------------------------------------ events: 사건이 차례를 연다
SOURCES = [("키보드", "사람이 엔터를 친다"), ("작업 완료", "b2 finished: exit 1"), ("파일 변경", "pager.py changed on disk"), ("타이머", "10분 뒤 깨워 줘")]


def draw_events(ax, t):
    dur, marks = timing("events", (24.0, [1.0, 3.0, 5.0, 7.0, 10.0]))
    cur = current_of(t, marks)
    label(ax, W / 2, 56, "무엇이든 같은 입구로: 배열 맨 아래에 붙이고 모델을 부른다", 34, GRAY)
    for i, (name, ex) in enumerate(SOURCES):
        y = 160 + i * 200
        on = i <= cur
        a = 1.0 if on else 0.2
        box(ax, 60, y, 520, 150, INK if i == cur else LINE, TINT if i == cur else "#FFFFFF", 5 if i == cur else 3, 16, alpha=a)
        label(ax, 90, y + 50, name, 34, INK, ha="left", bold=True, alpha=a)
        label(ax, 90, y + 105, ex, 24, GRAY, ha="left", alpha=a, mono=i > 0)
        if on:
            arrow(ax, 590, y + 75, 840, 520, color=INK if i == cur else LINE, alpha=a)
    box(ax, 850, 420, 520, 200, INK, TINT, 5, 18)
    label(ax, 1110, 490, "배열 맨 아래에 붙이고", 32, INK, bold=True)
    label(ax, 1110, 550, "모델을 부른다", 32, INK, bold=True)
    arrow(ax, 1380, 520, 1500, 520)
    box(ax, 1510, 440, 240, 160, LINE, "#FFFFFF", 3, 18)
    label(ax, 1630, 520, "뇌", 40, TXT, bold=True)
    if cur >= 4:
        a = ease((t - marks[4]) / 0.6)
        label(ax, 1110, 760, "깨울 때마다 돈 · 알림은 사실만 · 사람이 보고 멈출 수 있게", 26, BAD, bold=True, alpha=a)


ALL = {"pile": draw_pile, "subagent": draw_subagent, "events": draw_events}
DEFAULTS = {"pile": 20.0, "subagent": 30.0, "events": 24.0}

if __name__ == "__main__":
    for n in [a for a in sys.argv[1:] if not a.startswith("--")] or list(ALL):
        A.render(n, timing(n, (DEFAULTS[n], None))[0], ALL[n])
