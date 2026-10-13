#!/usr/bin/env python3
"""Unsloth 결정 모델 화면용 다이어그램을 SVG 로 그린다(원문·공식 문서의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#8A4B2A", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def box(x, y, w, h, title, lines=(), accent=False, size=34, color=None):
    out = [rect(x, y, w, h, INK if accent else LINE, sw=4 if accent else 3),
           text(x + 26, y + 54, title, size, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 26, y + 106 + i * 50, ln, 28, color or GRAY))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label="", color=INK, lx=None, ly=None, anchor="start"):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text(lx if lx is not None else (x1 + x2) / 2 + 16, ly if ly is not None else (y1 + y2) / 2 + 10, label, 25, GRAY, anchor))
    return "\n".join(out)


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def stack(items, gap=52, top=0):
    """세로로 쌓은 상자들 + 사이 화살표. items: (title, lines, accent)"""
    y, out = top, []
    for i, (t, ls, acc) in enumerate(items):
        h = 84 + 50 * len(ls) + (14 if ls else 0)
        out.append(box(0, y, W, h, t, ls, acc))
        y += h
        if i < len(items) - 1:
            out.append(arrow(W / 2, y + 4, W / 2, y + gap - 4)); y += gap
    return y, "\n".join(out)


def bar(x, y, w, h, frac, color=INK, back=SOFT):
    return rect(x, y, w, h, back, back, 0, 6) + rect(x, y, max(w * frac, 4), h, color, color, 0, 6)


figs = {}

# ---------- 배경 ----------
# 보통의 방식: 생성 → 파싱
h, b = stack([("① 프롬프트", ["“Answer with one of:", "  billing / technical / sales”"], False),
              ("② 토큰을 하나씩 생성", ["“Billing.”  “The billing team.”  …"], False),
              ("③ 글자를 파싱", ["형식이 깨지면 실패, 질문마다 다시 호출", "확률 없음: 망설였는지 확신했는지 모른다"], True)])
figs["t-generate"] = svg(h, b)

# 헤드
b = [rect(0, 0, W, 250, LINE, SOFT, 3), text(28, 54, "몸통 (트랜스포머 층들)", 32, TXT, weight="bold"),
     text(28, 106, "입력을 읽고 위치마다 은닉 상태(벡터)를 만든다", 28, GRAY)]
for i in range(10):
    b.append(rect(28 + i * 84, 150, 64, 64, LINE, FILL, 3, 8))
b += [arrow(220, 258, 220, 330), arrow(668, 258, 668, 330),
      box(0, 336, 420, 260, "언어 모델 헤드", ["다음 단어 후보", "수십만 개에 점수", "→ 글을 쓴다"]),
      box(468, 336, 420, 260, "결정 헤드", ["선택지마다 점수", "billing · technical · sales", "→ 고른다"], True),
      text(0, 650, "헤드 = 몸통 끝에 붙는 작은 출력 층", 30, TXT, weight="bold")]
figs["t-head"] = svg(670, "\n".join(b))

# LoRA
b = [rect(0, 40, 400, 400, LINE, SOFT, 3), text(200, 230, "원래 가중치 W", 32, TXT, "middle", "bold"),
     text(200, 280, "얼려 둔다 (학습 안 함)", 26, GRAY, "middle"), text(200, 330, "수십억 개", 26, GRAY, "middle"),
     text(440, 250, "+", 60, INK, "middle", "bold"),
     rect(490, 40, 60, 400, INK, FILL, 4, 8), text(520, 476, "A", 30, INK, "middle", "bold"),
     text(586, 250, "×", 44, INK, "middle", "bold"),
     rect(620, 210, 268, 60, INK, FILL, 4, 8), text(754, 306, "B", 30, INK, "middle", "bold"),
     text(0, 540, "작은 행렬 두 개(어댑터)만 학습한다", 30, TXT, weight="bold"),
     text(0, 590, "rank 16 = 작은 행렬의 폭이 16", 28, GRAY),
     text(0, 640, "→ 큰 모델도 GPU 하나로 파인튜닝", 28, GRAY)]
figs["t-lora"] = svg(660, "\n".join(b))

# ---------- 결정 모델 ----------
# 질문 타입 세 가지
rows = [("noul", "예 / 아니요", "‘예’일 확률 0-1"),
        ("choice", "선택지 중 하나", "선택지마다 확률"),
        ("score", "순서 있는 척도", "수준마다 확률")]
b = []
for i, (k, use, out) in enumerate(rows):
    y = i * 182
    b += [rect(0, y, W, 150, INK if i == 1 else LINE, sw=4 if i == 1 else 3),
          text(28, y + 62, k, 38, INK, weight="bold", mono=True), text(28, y + 118, use, 28, TXT),
          text(860, y + 118, out, 28, GRAY, "end")]
b += [text(0, 600, "한 요청에 질문 최대 64개", 28, TXT, weight="bold"),
      text(0, 648, "choice 선택지 최대 255개, score 최대 10단계", 26, GRAY)]
figs["t-types"] = svg(668, "\n".join(b))

# 티켓 예시
b = [rect(0, 0, W, 150, LINE, SOFT, 3),
     text(28, 56, "“Hi, I was charged twice for invoice #4411.", 28, TXT),
     text(28, 106, "  Please refund the duplicate today.”", 28, TXT),
     arrow(W / 2, 158, W / 2, 214)]
y = 222
for title, opts in [("어느 팀?  (choice)", [("billing", 0.99), ("technical", 0.0), ("sales", 0.0)]),
                    ("환불 요청?  (noul)", [("yes", 0.98)]),
                    ("얼마나 급한가?  (score)", [("not urgent", 0.0), ("soon", 0.09), ("today", 0.90)])]:
    hh = 70 + 46 * len(opts)
    b += [rect(0, y, W, hh, LINE), text(28, y + 46, title, 28, TXT, weight="bold")]
    for j, (lab, p) in enumerate(opts):
        yy = y + 70 + j * 46
        b += [text(28, yy + 26, lab, 26, GRAY, mono=True), bar(220, yy + 4, 520, 28, p), text(860, yy + 28, f"{p:.2f}", 26, INK if p > 0.5 else GRAY, "end", "bold")]
    y += hh + 20
b += [text(0, y + 30, "생성 토큰 0개 · 순전파 한 번", 28, INK, weight="bold")]
figs["ex-ticket"] = svg(y + 50, "\n".join(b))

# threshold
b = [text(0, 34, "technical 확률", 28, TXT, weight="bold")]
b += [bar(0, 60, W, 50, 1.0, SOFT, SOFT), rect(W * 0.8, 60, W * 0.2, 50, INK, INK, 0, 6),
      f'<line x1="{W * 0.8}" y1="44" x2="{W * 0.8}" y2="130" stroke="{TXT}" stroke-width="4"/>',
      text(W * 0.8, 160, "0.8", 28, TXT, "middle", "bold"), text(0, 160, "0", 26, GRAY), text(W, 160, "1", 26, GRAY, "end"),
      box(0, 210, 420, 210, "0.8 미만", ["사람이 한 번 본다"]),
      box(468, 210, 420, 210, "0.8 이상", ["버그 리포트 자동 생성"], True),
      text(0, 480, "threshold는 선택지 확률에 건다", 30, TXT, weight="bold"),
      text(0, 528, "confidence는 계산식이 모델마다 다르다", 28, GRAY)]
figs["ex-threshold"] = svg(548, "\n".join(b))

# ---------- 학습 결과 ----------
b = [text(0, 34, "Qwen3.5 8억(0.8B) · 정확도", 30, TXT, weight="bold"),
     rect(0, 56, 24, 24, SOFT, SOFT, 0, 4), text(34, 77, "학습 전", 24, GRAY),
     rect(170, 56, 24, 24, INK, INK, 0, 4), text(204, 77, "학습 후", 24, GRAY)]
y = 120
for name, a, c in [("typed-decisions", 36, 73), ("BANKING77 (의도 77개)", 7, 74), ("CLINC150 (의도 150개)", 19, 76)]:
    b += [text(0, y + 30, name, 28, TXT, weight="bold"),
          bar(0, y + 50, 760, 40, a / 100, LINE), text(W, y + 82, f"{a}%", 28, GRAY, "end"),
          bar(0, y + 100, 760, 40, c / 100), text(W, y + 132, f"{c}%", 28, INK, "end", "bold")]
    y += 190
b += [text(0, y + 20, "테스트 세트는 학습 데이터와 겹치지 않게 걸렀다", 26, GRAY)]
figs["ex-results"] = svg(y + 40, "\n".join(b))

b = [text(0, 34, "정확도 · GPU 메모리 · 학습 시간", 30, TXT, weight="bold")]
y = 70
for name, acc, vram, t in [("Qwen3.5 0.8B", 78, 4, 42), ("Qwen3.5 2B", 81, 8, 40), ("Llama 3.2 3B", 79, 4.1, 30),
                           ("Gemma 4 E4B", 77, 14.4, 49), ("Laya 추가 학습", 77, 2.5, 10)]:
    hl = name.startswith(("Qwen3.5 0.8B", "Laya"))
    b += [text(0, y + 30, name, 28, INK if hl else TXT, weight="bold"), text(W, y + 30, f"{acc}%  ·  {t}분", 28, INK if hl else GRAY, "end", "bold" if hl else "normal"),
          bar(0, y + 46, 760, 28, vram / 16, INK if hl else LINE), text(W, y + 70, f"{vram:g}GB", 24, GRAY, "end")]
    y += 120
b += [text(0, y + 20, "막대 = GPU 메모리", 24, GRAY)]
figs["ex-size"] = svg(y + 40, "\n".join(b))

# ---------- 학습하기 ----------
b = [box(0, 0, 280, 330, "앱", ["모델 고르고", "Decision", "model로", "Start"]),
     box(304, 0, 280, 330, "노트북", ["Colab·Kaggle", "무료 GPU", "단계별 안내"]),
     box(608, 0, 280, 330, "코드", ["FastDecision", "Model", "+ Decision", "Trainer"])]
for x in (140, 444, 748):
    b.append(arrow(x, 338, W / 2, 420))
b += [box(0, 426, W, 200, "학습 → 보정 → 저장", ["홀드아웃으로 정확도·보정 오차 확인"], True),
      arrow(W / 2, 634, W / 2, 690),
      box(0, 696, W, 150, "Decision API로 서빙", []),
      text(0, 900, "재현 설정: 에폭 2 · LoRA rank 16 · 학습률 2e-4", 28, GRAY)]
figs["ex-paths"] = svg(920, "\n".join(b))

# 보정: 일기예보 비유
b = [text(0, 34, "“비 올 확률 80%”라고 한 날 10일", 30, TXT, weight="bold")]
for row, (label, rain, ok) in enumerate([("보정이 잘 된 예보", 8, True), ("보정이 안 된 예보", 5, False)]):
    y = 80 + row * 250
    b += [text(0, y + 30, label, 28, INK if ok else BAD, weight="bold")]
    for i in range(10):
        cx = 40 + i * 84
        fill = (INK if ok else BAD) if i < rain else SOFT
        b.append(f'<circle cx="{cx}" cy="{y + 100}" r="30" fill="{fill}"/>')
    b += [text(0, y + 180, f"실제로 비 온 날 {rain}일" + (" → 믿을 만하다" if ok else " → 80%를 믿을 수 없다"), 28, GRAY)]
b += [text(0, 620, "모델도 같다: 80% 확신한 답은 80% 맞아야", 30, TXT, weight="bold"),
      text(0, 670, "그래야 확률에 threshold를 걸 수 있다", 28, GRAY)]
figs["t-calibration"] = svg(690, "\n".join(b))

# ECE 예시 계산
b = [text(0, 34, "예측 100개를 확신도 구간으로 묶으면", 28, TXT, weight="bold")]
for i, (lab, n, conf, acc) in enumerate([("90% 구간", 50, 0.9, 0.8), ("60% 구간", 50, 0.6, 0.6)]):
    y = 70 + i * 230
    b += [text(0, y + 30, f"{lab} · {n}개", 28, TXT, weight="bold"),
          text(0, y + 80, "확신", 26, GRAY), bar(90, y + 56, 640, 32, conf, LINE), text(W, y + 82, f"{conf:.0%}", 26, GRAY, "end"),
          text(0, y + 130, "실제", 26, GRAY), bar(90, y + 106, 640, 32, acc), text(W, y + 132, f"{acc:.0%}", 26, INK, "end", "bold"),
          text(0, y + 180, f"차이 {abs(conf - acc) * 100:.0f}%p", 26, BAD if conf != acc else GRAY)]
b += [rect(0, 540, W, 110, INK, FILL, 4),
      text(28, 608, "ECE = 0.5 × 0.10 + 0.5 × 0 = 0.05", 32, INK, weight="bold", mono=True),
      text(0, 700, "0에 가까울수록 확률을 믿을 수 있다", 28, GRAY)]
figs["ex-ece"] = svg(720, "\n".join(b))

# ---------- 서빙 ----------
b = [box(0, 0, W, 170, "Jev를 쓰던 코드", ["그대로 둔다"]),
     arrow(W / 2, 178, W / 2, 236, "서버 주소·키만 바꾼다", lx=W / 2 + 20, ly=216),
     box(0, 244, 420, 200, "TypeSafe Jev", ["클라우드"]),
     box(468, 244, 420, 200, "로컬 Unsloth", ["Decision API", "내가 학습한 모델"], True),
     text(0, 510, "주의: confidence 계산식이 다르다", 28, BAD, weight="bold"),
     text(0, 558, "→ Jev에서 맞춘 confidence threshold는 쓰지 말고", 28, GRAY),
     text(0, 606, "   선택지 확률에 threshold를 다시 건다", 28, GRAY)]
figs["ex-swap"] = svg(626, "\n".join(b))

# ---------- 동작 원리 ----------
toks = [("입력", 3, SOFT), ("질문1", 1, FILL), ("선택지", 3, FILL), ("질문2", 1, FILL), ("선택지", 2, FILL)]
b = [text(0, 34, "① 프롬프트 하나에 입력 + 질문 + 선택지", 28, TXT, weight="bold")]
x = 0
for lab, n, fill in toks:
    w = 64 * n + 8 * (n - 1)
    b += [rect(x, 60, w, 60, INK if fill == FILL and lab == "선택지" else LINE, fill, 3, 8), text(x + w / 2, 100, lab, 22, TXT, "middle")]
    x += w + 12
b += [arrow(W / 2, 130, W / 2, 186),
      rect(0, 192, W, 110, LINE, SOFT, 3), text(W / 2, 240, "② LLM이 한 번 읽는다 (LoRA)", 28, TXT, "middle", "bold"),
      text(W / 2, 280, "자리마다 은닉 상태", 24, GRAY, "middle"),
      arrow(W / 2, 310, W / 2, 366),
      rect(0, 372, W, 110, INK, FILL, 4), text(W / 2, 420, "③ 결정 헤드 (Clef와 같은 설계)", 28, INK, "middle", "bold"),
      text(W / 2, 460, "질문·선택지 자리를 보고 모든 질문을 함께 채점", 24, GRAY, "middle"),
      arrow(W / 2, 490, W / 2, 546)]
for i, (lab, p) in enumerate([("billing", 0.99), ("technical", 0.01), ("sales", 0.0)]):
    y = 560 + i * 54
    b += [text(0, y + 30, lab, 26, TXT, mono=True), bar(200, y + 6, 560, 30, p), text(W, y + 32, f"{p:.2f}", 26, INK, "end")]
b += [text(0, 760, "글자는 하나도 쓰지 않는다", 28, INK, weight="bold")]
figs["t-decision"] = svg(780, "\n".join(b))

# 어휘 vs 선택지
b = [text(0, 34, "글을 쓰는 LLM: 위치마다 단어 후보 전부", 28, TXT, weight="bold")]
for i in range(240):
    x, y = (i % 30) * 29.6, 60 + (i // 30) * 26
    b.append(f'<rect x="{x}" y="{y}" width="24" height="20" rx="3" fill="{LINE}"/>')
b += [text(0, 300, "… 수십만 개 × 위치 수", 28, GRAY),
      text(0, 400, "결정 모델: 선택지 개수만큼", 28, INK, weight="bold")]
for i in range(3):
    b.append(f'<rect x="{i * 60}" y="430" width="48" height="40" rx="5" fill="{INK}"/>')
b += [text(200, 460, "3개", 28, INK, weight="bold"),
      text(0, 550, "단어 예측에 메모리를 쓰지 않는다", 28, TXT)]
figs["ex-vocab"] = svg(570, "\n".join(b))

# ---------- 해설 ----------
b = [f'<line x1="20" y1="120" x2="868" y2="120" stroke="{LINE}" stroke-width="6"/>']
for x, title, l1, l2, acc in [(20, "분류기", "BERT + 분류 헤드", "정해진 레이블만", False),
                              (444, "결정 모델", "LLM + 결정 헤드", "선택지를 글로 받는다", True),
                              (868, "생성기", "LLM + 언어 모델 헤드", "아무 말이나 한다", False)]:
    anchor = "start" if x < 100 else "end" if x > 800 else "middle"
    b += [f'<circle cx="{x}" cy="120" r="{22 if acc else 16}" fill="{INK if acc else GRAY}"/>',
          text(x, 60, title, 32, INK if acc else TXT, anchor, "bold"),
          text(x, 190, l1, 24, GRAY, anchor), text(x, 230, l2, 24, GRAY, anchor)]
b += [box(0, 300, W, 250, "가운데 자리의 이점", ["못 본 선택지도 설명만 바꿔 넣으면 고른다", "질문 문장과 선택지 설명을 읽고 이해한다"], True)]
figs["ex-spectrum"] = svg(570, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
