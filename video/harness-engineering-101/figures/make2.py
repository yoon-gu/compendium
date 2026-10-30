#!/usr/bin/env python3
"""2편(수업 7-10) 화면용 정지 그림. make.py 의 그리기 도우미를 그대로 쓰고, 숫자는 lab/runs 의 실제 녹화 값이다.  python3 make2.py"""
import json
from pathlib import Path

from make import (BAD, F, GRAY, INK, LAB, LINE, MONO, OK, SOFT, TXT, W, arrow, box, code, rect, svg, text)

HERE = Path(__file__).resolve().parent
TINT, PINK = "#E7EEF5", "#FBEFEF"
figs = {}


def table(rows, widths, head=None, size=27, rh=78, accent=()):
    """간단한 표: rows = [(칸, 칸, …)]. accent 는 강조할 행 번호."""
    out, y = [], 0
    if head:
        x = 0
        for h, w in zip(head, widths):
            out.append(text(x + 18, 32, h, 25, GRAY, weight="bold")); x += w
        y = 50
    for i, r in enumerate(rows):
        acc = i in accent
        out.append(rect(0, y, W, rh - 10, INK if acc else LINE, TINT if acc else "#FFFFFF", 4 if acc else 3, 10))
        x = 0
        for j, (c, w) in enumerate(zip(r, widths)):
            out.append(text(x + 18, y + rh / 2 + 4, c, size, INK if (j == 0 and acc) else (TXT if j == 0 else GRAY), weight="bold" if j == 0 else "normal"))
            x += w
        y += rh
    return y, "\n".join(out)


# ---------- 오늘의 지도 ----------
h, b = table([("7 예산", "배열이 차서 호출이 거절된다", "자르고, 잘랐다고 말한다"),
              ("8 서브에이전트", "탐색 기록이 배열에 남는다", "빈 배열에 맡긴다"),
              ("9 리마인더", "바뀐 세상·계획을 놓친다", "맨 아래에 알림을 붙인다"),
              ("10 백그라운드", "느린 명령 앞에서 멈춘다", "몸이 기다리고 깨운다")],
             [230, 360, 314], head=("수업", "무너지는 것", "고치는 법"), size=26, rh=96)
figs["map-2"] = svg(h, b)

# ---------- 준비물 ----------
h, b = table([("1편 그대로", "Python 3.10+, API 키, 설치할 패키지 없음"),
              ("새 실습 파일", "lessons/l7_budget.py … l10_background.py"),
              ("예제 만들기", "python3 make_samples.py"),
              ("생기는 것", "sample-project2/ (로그 2.3MB) · minishop/")],
             [250, 654], size=26, rh=92, accent=(2,))
figs["setup-2"] = svg(h, b)

# ---------- 윈도우와 예산 ----------
b = [text(0, 36, "컨텍스트 윈도우 (하이쿠: 1,000,000 토큰)", 28, GRAY, weight="bold"),
     rect(0, 60, W, 110, LINE, "#FFFFFF", 3, 10),
     rect(0, 60, W * 0.55, 110, INK, TINT, 3, 10),
     text(24, 126, "잘 읽히는 범위", 28, INK, weight="bold"),
     text(W * 0.55 + 24, 126, "앞쪽을 덜 챙긴다 (열화)", 26, GRAY),
     text(0, 236, "넘치면?", 28, BAD, weight="bold"),
     rect(0, 260, W, 110, BAD, PINK, 3, 10),
     text(24, 326, "HTTP 400: prompt is too long", 28, BAD, mono=True),
     text(0, 430, "가방처럼 던져 넣지 말고, 예산처럼 쓴다", 30, INK, weight="bold")]
figs["window-budget"] = svg(450, "\n".join(b))

# ---------- 무엇이 예산을 먹었나 (l7-whole 실측) ----------
parts = [("시스템 + 도구 정의", 608, "약 600"), ("사용자 질문", 40, "수십"), ("도구 결과 하나 (build.log)", 1_266_637, "약 1,266,600")]
b = [text(0, 32, "거절된 배열의 덩어리별 토큰 (총 1,267,285)", 26, GRAY, weight="bold")]
for i, (name, v, lab) in enumerate(parts):
    y = 64 + i * 130
    b.append(text(0, y + 26, name, 27, TXT, weight="bold"))
    wbar = max(6, min(W, W * v / 400_000))
    b.append(rect(0, y + 44, wbar, 56, BAD if i == 2 else INK, PINK if i == 2 else TINT, 3, 6))
    b.append(text(min(wbar, W - 300) + 16 if i < 2 else W - 20, y + 82, lab + " 토큰" + (" → 화면 밖으로" if i == 2 else ""), 26,
                  BAD if i == 2 else TXT, "start" if i < 2 else "end", "bold"))
b.append(text(0, 470, "예산을 먹는 건 말이 아니라 도구 결과", 30, INK, weight="bold"))
figs["budget-bars"] = svg(490, "\n".join(b))

# ---------- 압축과 메모리 파일 ----------
b = [text(0, 32, "압축 (compaction)", 28, INK, weight="bold"),
     rect(0, 52, 120, 70, LINE, SOFT, 3, 8), text(60, 96, "system", 22, GRAY, "middle"),
     rect(128, 52, 470, 70, LINE, SOFT, 3, 8), text(363, 96, "오래된 바퀴들 (길다)", 24, GRAY, "middle"),
     rect(606, 52, 298, 70, INK, TINT, 3, 8), text(755, 96, "최근 몇 바퀴", 24, INK, "middle", "bold"),
     arrow(363, 130, 363, 178),
     rect(0, 186, 120, 70, LINE, SOFT, 3, 8), text(60, 230, "system", 22, GRAY, "middle"),
     rect(128, 186, 200, 70, OK, "#EDF5EF", 3, 8), text(228, 230, "요약 한 덩어리", 23, OK, "middle", "bold"),
     rect(336, 186, 298, 70, INK, TINT, 3, 8), text(485, 230, "최근 몇 바퀴", 24, INK, "middle", "bold"),
     text(0, 300, "요약 지시: 지금 상태 · 정한 것 · 만진 파일 · 남은 일", 25, GRAY),
     text(0, 376, "메모리 파일", 28, INK, weight="bold"),
     box(0, 396, 430, 190, "배열 = RAM", ["세션이 끝나면 비워진다"], False, 28),
     box(474, 396, 430, 190, "파일 = 디스크", ["시작할 때 넣어 준다", "빌드 명령·규칙 등"], True, 28)]
figs["compaction-memory"] = svg(596, "\n".join(b))

# ---------- 서브에이전트: 무엇을 아끼고 무엇을 쓰나 (l8 실측) ----------
def bars(y0, title, a, bv, note, scale):
    out = [text(0, y0, title, 27, TXT, weight="bold")]
    for k, (lab, v, c, fill) in enumerate([("없이", a, GRAY, SOFT), ("맡김", bv, INK, TINT)]):
        y = y0 + 22 + k * 74
        out.append(text(0, y + 42, lab, 25, GRAY))
        out.append(rect(90, y, max(6, (W - 330) * v / scale), 56, c, fill, 3, 6))
        out.append(text(90 + (W - 330) * v / scale + 14, y + 40, f"{v:,}", 26, c, weight="bold"))
    out.append(text(0, y0 + 196, note, 24, GRAY))
    return out


b = bars(32, "부모 배열 (bytes)", 57_052, 38_515, "자식 배열 140,121 bytes 는 끝나고 버렸다", 60_000)
b += bars(296, "입력 토큰 합계", 36_558, 134_816, "맡긴 버전 = 부모 24,778 + 자식 110,038", 140_000)
b.append(text(0, 556, "돈은 더 든다. 사는 것은 부모의 작업 기억", 30, INK, weight="bold"))
figs["sub-cost"] = svg(576, "\n".join(b))

# ---------- 좋은 일감 (l8-agent 실제 첫머리) ----------
b = [text(0, 30, "실제로 부모가 쓴 일감의 첫머리", 25, GRAY, weight="bold"),
     rect(0, 48, W, 130, INK, "#1B1D21", 0, 10),
     text(22, 96, "작업 디렉터리는 /private/tmp/he101/l8b 이다 (프로젝트", 25, "#C3E88D", mono=True),
     text(22, 140, "루트, 이 경로 밖은 읽거나 수정하지 말 것). 이 안에 있는 …", 25, "#C3E88D", mono=True)]
h, t = table([("무엇을", "바깥으로 나가는 HTTP 호출을 모두 찾는다"), ("어디서", "작업 디렉터리 = 프로젝트 루트"),
              ("하지 말 것", "경로 밖 읽기·파일 수정"), ("돌려줄 형식", "표 + 파일·줄 근거")], [230, 674], size=26, rh=84)
b.append(f'<g transform="translate(0,210)">{t}</g>')
b.append(text(0, 210 + h + 40, "첫 시도엔 '어디서'가 빠져 자식이 홈 폴더를 뒤지기 시작했다", 25, BAD, weight="bold"))
figs["ticket"] = svg(210 + h + 60, "\n".join(b))

# ---------- 맡길 일, 맡기지 말 일 ----------
b = [box(0, 0, 440, 400, "맡길 일", ["무언가를 찾기", "테스트 돌리고 실패만 요약", "긴 문서에서 핵심 뽑기", "서로 독립인 여러 조각"], True, 32),
     box(464, 0, 440, 400, "맡기지 말 일", ["이 세션의 판단이 필요한 일", "명령 하나면 끝날 일", "줄줄이 이어지는 수정"], False, 32),
     text(W / 2, 450, "읽을 건 많고, 남길 건 짧은 일", 30, INK, "middle", "bold")]
figs["delegate"] = svg(470, "\n".join(b))

# ---------- 리마인더는 어디에 붙나 ----------
rows = [("system", "캐시가 붙어 고정 — 고치면 아래 전부 다시", LINE, SOFT),
        ("user", "pager.py에 타입 힌트를 달아 줘.", LINE, "#FFFFFF"),
        ("assistant", "tool_use: read_file(pager.py)", LINE, "#FFFFFF"),
        ("user", "tool_result: (파일 내용)", LINE, "#FFFFFF"),
        ("", "+ <system-reminder> pager.py changed on disk …", INK, TINT)]
b = []
for i, (role, s, c, fill) in enumerate(rows):
    y = i * 86
    b.append(rect(0, y, W, 72, c, fill, 4 if c == INK else 3, 10))
    b.append(text(22, y + 46, role, 26, INK, weight="bold", mono=True))
    b.append(text(190 if role else 22, y + 46, s, 25, INK if c == INK else TXT, weight="bold" if c == INK else "normal", mono=role != "system"))
b.append(text(0, 5 * 86 + 34, "새 소식은 언제나 맨 아래, 사용자 쪽 메시지 끝에", 28, INK, weight="bold"))
figs["reminder-where"] = svg(5 * 86 + 50, "\n".join(b))

# ---------- 배열 끝 열어 보기 (l9-reminder 세션 실측) ----------
msg = json.load(open(LAB / "runs/l9-reminder-session.json", encoding="utf-8"))[4]
tr, tx = msg["content"]
short = {"role": msg["role"], "content": [{"type": "tool_result", "tool_use_id": tr["tool_use_id"][:14] + "…",
                                           "content": tr["content"][:38] + "…"}, tx]}
p = LAB / "runs/l9-reminder-message.txt"
p.write_text(json.dumps(short, ensure_ascii=False, indent=2).replace("\\n", "\\n\n" + " " * 14) + "\n", encoding="utf-8")
figs["reminder-json"] = code(p, 1, len(p.read_text(encoding="utf-8").splitlines()), hl_substr=("system-reminder", "changed on disk"), cols=60)

# ---------- 너무 자주 알리기 ----------
b = [box(0, 0, 440, 300, "피할 것", ["매 바퀴 \"조심하세요\"", "시계에 맞춘 알림", "모델이 방금 한 일까지 알림"], False, 32),
     box(464, 0, 440, 300, "할 것", ["사건이 생겼을 때만", "구체적인 사실만", "늘 필요한 말은 시스템 프롬프트로"], True, 32),
     text(0, 356, "제 첫 버전: 모델이 sed 로 고친 파일까지 '바뀌었다'고 알렸다", 25, BAD, weight="bold"),
     text(0, 396, "→ 모델 자신이 바꾼 것은 알리지 않게 고쳤다", 25, GRAY)]
figs["oversteer"] = svg(410, "\n".join(b))

# ---------- 동기 루프의 한계 ----------
h, b = table([("끝까지 기다린다", "그동안 아무것도 못 한다"),
              ("시간 제한으로 끊는다", "모델은 \"여기선 실패한다\"고 배운다"),
              ("sleep 하고 확인, 또 확인", "비싼 뇌가 주방 타이머 노릇 (폴링)")],
             [340, 564], head=("30초 걸리는 테스트 앞에서", "그 결과"), size=26, rh=100, accent=(2,))
figs["sync-limits"] = svg(h, b)

# ---------- sleep 차단 ----------
b = [text(0, 30, "모델이 보낸 명령", 25, GRAY, weight="bold"),
     rect(0, 46, W, 76, LINE, "#1B1D21", 0, 10), text(22, 94, 'run_command("sleep 30 && cat result.txt")', 26, "#C3E88D", mono=True),
     arrow(W / 2, 132, W / 2, 178),
     text(0, 214, "몸이 돌려주는 도구 결과", 25, GRAY, weight="bold"),
     rect(0, 230, W, 110, BAD, PINK, 3, 10),
     text(22, 276, "BLOCKED: don't wait in the foreground.", 25, BAD, mono=True),
     text(22, 318, "Use background=true and you'll be notified.", 25, BAD, mono=True),
     text(0, 396, "좋은 길을 쉬운 길로 만드는 건 몸의 몫 (위 명령은 예시)", 26, INK, weight="bold")]
figs["sleep-guard"] = svg(416, "\n".join(b))

# ---------- 2편 정리 ----------
h, b = table([("예산", "자르고, 잘랐다고 말한다"), ("서브에이전트", "빈 배열에 맡기고 답만 받는다"),
              ("리마인더", "배열 맨 아래에 붙인다"), ("백그라운드", "몸이 기다리고, 끝나면 깨운다")],
             [260, 644], size=28, rh=96)
b += "\n" + text(0, h + 40, "전부 1편의 배열 · 루프 · 디스패치 표를 다시 쓴 것", 28, INK, weight="bold")
figs["recap-2"] = svg(h + 60, b)

if __name__ == "__main__":
    for name, s in figs.items():
        (HERE / f"{name}.svg").write_text(s, encoding="utf-8")
        print(name)
