#!/usr/bin/env python3
"""Scion 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#5B3F8C", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
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
# 병목이 옮겨 갔다
b = []
for i, (t, sub, hot) in enumerate([("코딩", "Claude가 빠르게", False), ("소스 컨트롤", "git", True), ("빌드", "", True), ("CI", "테스트", True)]):
    x = i * 222
    b += [rect(x, 40, 200, 150, INK if hot else LINE, FILL, 4 if hot else 3), text(x + 100, 108, t, 30, INK if hot else GRAY, "middle", "bold"),
          text(x + 100, 152, sub, 22, GRAY, "middle")]
    if i < 3:
        b.append(arrow(x + 202, 115, x + 220, 115))
b += [text(111, 26, "더 이상 병목 아님", 22, GRAY, "middle"),
      f'<path d="M 222 220 L 888 220" stroke="{BAD}" stroke-width="6"/>', text(555, 262, "사람 규모로 만든 개발 인프라 = 새 병목", 28, BAD, "middle", "bold"),
      text(0, 340, "병목 하나를 없애면 산출이 더 늘어난다", 28, TXT),
      text(0, 388, "→ 병합량 증가는 계속될 것", 28, GRAY)]
figs["t-bottleneck"] = svg(408, "\n".join(b))

# 모노레포
b = [rect(0, 0, W, 330, INK, FILL, 4), text(28, 50, "저장소 하나 (monorepo)", 30, INK, weight="bold")]
for i, name in enumerate(["services/billing", "services/search", "libs/auth", "research/train", "infra/ci", "tools/…"]):
    x, y = 28 + (i % 3) * 282, 84 + (i // 3) * 112
    b += [rect(x, y, 262, 90, LINE, SOFT, 3, 10), text(x + 131, y + 54, name, 24, TXT, "middle", mono=True)]
b += [text(0, 390, "변경 하나로 여러 프로젝트를 함께 고친다", 28, TXT),
      text(0, 438, "예: 구글, 메타 — 그리고 Anthropic", 26, GRAY)]
figs["t-monorepo"] = svg(458, "\n".join(b))

# 분산 git
b = [rect(334, 0, 220, 110, LINE, SOFT, 3), text(444, 50, "서버", 30, TXT, "middle", "bold"), text(444, 88, "전체 이력", 24, GRAY, "middle")]
for i in range(3):
    x = i * 334
    b += [arrow(444, 116, x + 110, 236), rect(x, 244, 220, 150, INK, FILL, 4), text(x + 110, 296, "내 컴퓨터", 26, INK, "middle", "bold"),
          text(x + 110, 336, "전체 이력 복사본", 22, GRAY, "middle"), text(x + 110, 370, "오프라인 커밋 OK", 22, GRAY, "middle")]
b += [text(444, 190, "git clone", 26, INK, "middle", mono=True), text(0, 450, "사람이 노트북으로 일할 때는 장점", 28, TXT)]
figs["t-git"] = svg(470, "\n".join(b))

# CI 체크아웃
h, b = stack([("① 코드가 바뀐다", ["변경 하나 병합"], False),
              ("② CI 작업이 저장소를 받고 파일을 꺼낸다", ["= 체크아웃 (변경마다, 작업마다)"], True),
              ("③ 빌드하고 테스트한다", [], False)])
figs["t-ci"] = svg(h, b)

# 규모
b = []
for i, (num, lab) in enumerate([("≈100GB", "main 이력"), ("25GB+", "압축 작업 사본"), ("2,500만", "하루 CI 체크아웃")]):
    x = i * 300
    b += [text(x, 60, num, 50, INK, weight="bold"), text(x, 104, lab, 24, GRAY)]
b += [rect(0, 150, W, 140, INK, FILL, 4), text(W / 2, 212, "25GB × 2,500만 회 ≈ 625PB", 40, INK, "middle", "bold", mono=True),
      text(W / 2, 260, "하루에, 아무 요령 없이 git으로 받는다면", 26, GRAY, "middle"),
      text(0, 350, "→ 원문: “하루 600PB가 넘는 git 트래픽”", 28, TXT)]
figs["ex-scale"] = svg(370, "\n".join(b))

# 미러
b = [rect(334, 0, 220, 90, LINE, SOFT, 3), text(444, 56, "원본 git", 28, TXT, "middle", "bold")]
for i in range(6):
    x = i * 148
    b += [arrow(444, 96, x + 64, 176, color=LINE), rect(x, 182, 128, 70, INK, FILL, 3, 10), text(x + 64, 226, "미러", 24, INK, "middle")]
for i in range(30):
    x, y = (i % 15) * 59 + 10, 300 + (i // 15) * 44
    b.append(f'<rect x="{x}" y="{y}" width="40" height="30" rx="5" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>')
b += [text(0, 440, "얕은 클론 · 희소 체크아웃 · promisor 원격 · 시드", 26, GRAY),
      text(0, 486, "가장 많을 때 미러 수백 대 → 병합이 늘수록 운영이 버거워졌다", 26, TXT)]
figs["t-mirrors"] = svg(506, "\n".join(b))

# ---------- Scion ----------
# 커밋 vs 체인지셋
b = [box(0, 0, 420, 420, "git 커밋", []), text(26, 100, "→ 트리 전체", 26, GRAY)]
for i, f in enumerate(["a.py", "b.py", "c.py", "d.py", "e.py"]):
    b += [rect(26, 130 + i * 54, 200, 42, LINE, SOFT, 2, 6), text(40, 160 + i * 54, f, 22, TXT, mono=True)]
b += [box(468, 0, 420, 420, "Scion 체인지셋", [], True), text(494, 100, "→ 바뀐 파일만", 26, GRAY)]
for i, (f, h_) in enumerate([("b.py", "9f2c…"), ("d.py", "41ae…")]):
    y = 130 + i * 70
    b += [rect(494, y, 160, 50, INK, FILL, 3, 6), text(510, y + 33, f, 22, INK, mono=True), arrow(658, y + 25, 712, y + 25),
          rect(716, y, 150, 50, LINE, SOFT, 2, 6), text(730, y + 33, h_, 22, GRAY, mono=True)]
b += [text(494, 320, "첫 번째 부모와의 차이", 24, GRAY), text(494, 360, "내용 = 해시가 이름", 24, GRAY), text(494, 396, "→ 한번 저장되면 안 바뀐다", 24, GRAY)]
figs["t-changeset"] = svg(420, "\n".join(b))

# 비교 후 교환
b = [rect(334, 0, 220, 110, INK, FILL, 4), text(444, 50, "main →", 28, INK, "middle", "bold", mono=True), text(444, 90, "c41", 30, INK, "middle", mono=True),
     box(0, 190, 400, 210, "변경 A", ["“지금 c41이면", " → c42로”"]), box(488, 190, 400, 210, "변경 B", ["“지금 c41이면", " → c43으로”"]),
     arrow(200, 186, 380, 114), arrow(688, 186, 508, 114, color=LINE),
     text(200, 450, "✓ 먼저 도착 → 성공", 26, INK, "middle", "bold"), text(688, 450, "✗ 이미 c42 → 실패, 다시", 26, BAD, "middle", "bold"),
     text(0, 520, "전체를 잠그지 않아도 서로 덮어쓰지 않는다", 28, TXT)]
figs["t-cas"] = svg(540, "\n".join(b))

# 결과
b = []
for i, (lab, big, note_) in enumerate([("인프라 CPU·메모리", "1/200", "예전 git 미러 대비"), ("체크아웃 시간", "분 → 초", "약 100배"), ("CI CPU 용량", "+25%", "여유가 생김")]):
    y = i * 130
    b += [rect(0, y, W, 110, INK if i == 0 else LINE, FILL, 4 if i == 0 else 3), text(28, y + 48, lab, 28, TXT, weight="bold"),
          text(28, y + 88, note_, 22, GRAY), text(860, y + 72, big, 50, INK, "end", "bold")]
b += [text(0, 420, "층마다 캐시 적중률 99% 이상, 오래 남는 상태 없음", 24, GRAY)]
figs["ex-results"] = svg(440, "\n".join(b))

# ---------- 배운 것 ----------
b = [box(0, 0, 420, 300, "Claude", ["코드를 쓴다", "(엔지니어보다 잘 쓴다고", "팀은 판단)"]),
     box(468, 0, 420, 300, "엔지니어", ["설계를 판단한다", "과한 설계 → “아니오”", "제약 위반 → “아니오”"], True),
     text(0, 360, "리뷰는 모든 줄이 아니라 변경의 의도를 본다", 28, TXT)]
figs["ex-no"] = svg(380, "\n".join(b))

b = [text(0, 34, "git → Scion 데이터 이전 프로그램", 28, TXT, weight="bold"),
     text(0, 100, "메모리", 26, GRAY), bar(140, 76, 600, 40, 1.0, LINE), text(760, 106, "손으로 짠 시제품", 22, GRAY),
     bar(140, 126, 600, 40, 0.05), text(760, 156, "1/20", 26, INK, weight="bold"),
     text(0, 260, "속도", 26, GRAY), bar(140, 236, 600, 40, 0.25, LINE), text(760, 266, "1×", 22, GRAY),
     bar(140, 286, 600, 40, 1.0), text(760, 316, "4×", 26, INK, weight="bold"),
     text(0, 400, "Claude Mythos Preview 초기 내부 버전이 다시 씀", 26, TXT),
     text(0, 444, "지켜야 할 처리 순서 규칙은 그대로", 24, GRAY)]
figs["ex-ingest"] = svg(464, "\n".join(b))

b = []
for i, (ch, comp) in enumerate([("#scion-daemon", "노드마다 도는 daemon"), ("#scion-cache", "지역 캐시"), ("#antique-merge-queue", "병합 큐")]):
    y = i * 120
    b += [rect(0, y, W, 100, LINE, FILL, 3), text(28, y + 44, ch, 26, INK, weight="bold", mono=True), text(28, y + 80, comp, 22, GRAY),
          f'<circle cx="820" cy="{y + 50}" r="28" fill="{INK}"/>', text(820, y + 60, "C", 28, FILL, "middle", "bold")]
b += [text(0, 410, "채널마다 Claude 하나가 그 구성 요소만 지켜본다", 26, TXT),
      text(0, 454, "텔레메트리·로그 → 알림이 놓치는 미묘한 문제", 24, GRAY)]
figs["ex-superfan"] = svg(474, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
