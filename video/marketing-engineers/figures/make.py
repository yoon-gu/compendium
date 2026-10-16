#!/usr/bin/env python3
"""마케팅 엔지니어 회차 화면용 다이어그램을 SVG 로 그린다(원문의 구조만 가져와 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT, BAD = "#2B4C7E", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8", "#A23B3B"
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

# ---------- 배경: 코딩 에이전트 + MCP ----------
b = [rect(0, 0, 420, 330, INK, FILL, 4), text(26, 54, "내 폴더", 34, INK, weight="bold"),
     text(26, 110, "코딩 에이전트", 30, TXT, weight="bold"),
     text(26, 160, "파일을 읽고 쓴다", 26, GRAY), text(26, 206, "코드를 돌린다", 26, GRAY), text(26, 252, "예약해 두면 밤에도", 26, GRAY),
     text(26, 296, "= 아주 빠른 신입", 26, INK, weight="bold")]
for i, t in enumerate(["CRM", "결제·매출", "슬랙", "광고 관리자"]):
    y = 10 + i * 82
    b += [rect(560, y, 328, 66, LINE, SOFT, 3), text(724, y + 43, t, 28, TXT, "middle"),
          f'<line x1="424" y1="{165}" x2="556" y2="{y + 33}" stroke="{INK}" stroke-width="3"/>']
b += [rect(450, 140, 84, 50, INK, INK, 0, 25), text(492, 174, "MCP", 22, FILL, "middle", "bold"),
      text(444, 380, "MCP = 에이전트에 도구를 꽂는 만능 플러그", 26, GRAY, "middle")]
figs["agent"] = svg(400, "\n".join(b))

# ---------- 배경: 캠페인 ID ----------
b = [text(0, 34, "같은 ID를 모든 곳에", 28, TXT, weight="bold")]
for i, (k, v) in enumerate([("광고 링크", "?utm_campaign=BK014"), ("광고 이름", "BK014_dinner-angle_v2"),
                            ("이메일 이름", "BK014_followup"), ("CRM 거래", "campaign: BK014")]):
    y = 60 + i * 74
    b += [rect(0, y, W, 60, LINE, FILL, 3), text(22, y + 39, k, 26, TXT), text(W - 22, y + 39, v, 24, INK, "end", mono=True)]
b += [arrow(444, 362, 444, 412)]
cols = ["ID", "지출", "리드", "거래", "매출", "이탈"]
vals = ["BK014", "$2,000", "41", "6", "$18,000", "0"]
for j, (c, v) in enumerate(zip(cols, vals)):
    x = j * 148
    b += [rect(x, 420, 140, 50, INK, SOFT, 2, 6), text(x + 70, 453, c, 22, INK, "middle", "bold"),
          rect(x, 474, 140, 50, LINE, FILL, 2, 6), text(x + 70, 507, v, 22, TXT, "middle")]
b += [text(0, 570, "한 줄에 놓이면: 어떤 마케팅이 남는 고객을 데려왔나?", 25, INK, weight="bold"),
      text(0, 610, "표의 숫자는 설명을 위한 예시 값", 22, GRAY)]
figs["campaign-id"] = svg(625, "\n".join(b))

# ---------- 회사의 금더미 ----------
b = []
for i, (t, s) in enumerate([("영업", "매주 듣는 반론 다섯 가지"), ("고객 지원", "환불로 이어지는 약속"),
                            ("창업자", "업계에 대한 강한 의견"), ("분석 도구", "오래 남는 고객이 오는 페이지")]):
    x, y = (i % 2) * 468, (i // 2) * 160
    b.append(box(x, y, 420, 140, t, [s]))
b += [rect(0, 350, W, 90, BAD, FILL, 3), text(444, 405, "흩어져 있어서 캠페인에는 분기에 한 번", 28, BAD, "middle", "bold"),
      arrow(444, 448, 444, 500), rect(0, 506, W, 90, INK, SOFT, 4),
      text(444, 561, "마케팅 엔지니어: 오후 한나절에 캠페인으로", 28, INK, "middle", "bold")]
figs["gold"] = svg(600, "\n".join(b))

# ---------- 고객의 말 vs 기능 이름 ----------
b = [box(0, 0, W, 170, "기능 이름으로 쓴 광고", ["\"자동 예약 시스템\""]),
     box(0, 210, W, 210, "고객의 말로 쓴 광고", ["\"저녁 먹다가 전화 받는 거, 이제 그만\"", "영업 통화에서 사장들이 자꾸 하던 말"], True),
     text(0, 480, "고객 언어 에이전트: 통화 20-50개에서 이런 말을 뽑는다", 25, GRAY)]
figs["dinner"] = svg(500, "\n".join(b))

# ---------- 안전장치 ----------
b = [box(0, 0, W, 150, "프롬프트 속 문장", ["\"보내기 전에 꼭 물어봐\" → 공손한 제안일 뿐"]),
     text(0, 200, "도구에 박은 안전장치", 28, INK, weight="bold")]
for i, (t, s) in enumerate([("메일", "초안 쓰기 권한만"), ("광고", "일시정지 상태로만 올린다, 켜는 건 사람"),
                            ("예산", "사람이 쥔다"), ("정확한 규칙", "지출 상한·수신 거부·중복 제거 = 평범한 코드"),
                            ("판단", "맞는 고객인가, 우리 말투인가 = 모델")]):
    y = 224 + i * 80
    b += [rect(0, y, W, 66, INK if i < 3 else LINE, FILL, 3), text(24, y + 43, t, 26, TXT, weight="bold"),
          text(W - 24, y + 43, s, 24, GRAY, "end")]
figs["guard"] = svg(630, "\n".join(b))

# ---------- 주간 루프 ----------
b = []
for i, (d, s) in enumerate([("월", "성과 메모 읽고 유지·중단·변경"), ("화·수", "만들고, 약했던 워크플로 고치고, 새 시험"),
                            ("목", "영업·고객 지원 통화에 들어간다"), ("금", "에이전트가 만든 것 검토, 파일 고치기")]):
    y = i * 104
    b += [rect(0, y, 140, 90, INK, INK, 0), text(70, y + 56, d, 32, FILL, "middle", "bold"),
          rect(156, y, W - 156, 90, LINE, FILL, 3), text(180, y + 56, s, 26, TXT)]
b += [text(0, 470, "하루 종일 결과물을 고치고 있다면? 문제는 위쪽", 26, BAD, weight="bold"),
      text(0, 512, "거의 언제나 두뇌 아니면 지시문", 24, GRAY)]
figs["loop"] = svg(530, "\n".join(b))


# ================= 대화편(가상 카드사 토의) =================
# 둘러앉은 다섯 사람
import math
b = [f'<ellipse cx="444" cy="250" rx="250" ry="120" fill="{SOFT}" stroke="{LINE}" stroke-width="3"/>',
     text(444, 260, "가상의 카드사", 30, GRAY, "middle", "bold")]
for i, (r, d) in enumerate([("사회", "진행"), ("기획", "마케팅기획부"), ("모델", "타깃군 모델 학습·운영부"),
                            ("실행", "마케팅실행부"), ("플랫폼", "사내 플랫폼 기획·개발부")]):
    a = math.radians(-90 + i * 72)
    x, y = 444 + 340 * math.cos(a), 250 + 200 * math.sin(a)
    w = 250 if i else 170
    b += [rect(x - w / 2, y - 46, w, 92, INK if i == 0 else LINE, INK if i == 0 else FILL, 3, 46),
          text(x, y - 4, r, 30, FILL if i == 0 else INK, "middle", "bold"), text(x, y + 30, d, 19, FILL if i == 0 else GRAY, "middle")]
b += [text(444, 520, "회사·인물은 가상, 규제 설명은 일반 안내(법률 자문 아님)", 22, GRAY, "middle")]
figs["p-table"] = svg(540, "\n".join(b))

# 병목: 아이디어에서 발송까지
h, b = stack([("브리프", ["기획부가 쓴다"], False), ("타깃 추출 대기열", ["한 주에 수십 건, 급한 것부터"], False),
              ("문구 심의", ["내보내기 전 내부 심의"], False), ("발송 칸", ["고객당 주간 광고 수 제한"], True)], gap=44)
b += text(W, h + 50, "짧으면 3주, 보통 6주", 30, BAD, "end", "bold")
figs["p-queue"] = svg(h + 70, b)

# 두뇌 폴더 카드사판
b = []
for i, (t, s1, s2) in enumerate([("고객 정의", "해외 결제 월 3회 이상 + 해외 수수료 혜택 카드 없음", "→ 모델 세그먼트 정의와 같은 말로"),
                                 ("제안", "심의를 통과한 문구만", "→ 약속해도 되는 말 = 심의필"),
                                 ("실패 기록", "무이자 할부 혜택만 쓰고 떠난 고객", "→ 같은 실수를 막는 한 줄")]):
    y = i * 180
    b += [rect(0, y, W, 160, INK if i == 1 else LINE, FILL, 4 if i == 1 else 3), text(26, y + 50, t, 30, INK, weight="bold"),
          text(26, y + 98, s1, 25, TXT), text(26, y + 138, s2, 23, GRAY)]
figs["p-brain"] = svg(530, "\n".join(b))

# 발송부터 6개월 유지까지 한 줄
steps = ["발송", "반응", "발급", "첫 이용", "6개월 유지"]
b = [text(0, 34, "캠페인 ID 하나로 한 줄에", 28, TXT, weight="bold")]
for i, t in enumerate(steps):
    x = i * 178
    b += [rect(x, 60, 160, 90, INK if i >= 2 else LINE, INK if i >= 2 else SOFT, 3, 12), text(x + 80, 115, t, 26, FILL if i >= 2 else TXT, "middle", "bold")]
    if i < 4:
        b.append(arrow(x + 162, 105, x + 176, 105))
b += [text(0, 200, "지금은 따로 있다", 24, GRAY), text(0, 240, "반응률 = 실행부 · 발급 = 영업 · 이용액 = 다른 시스템", 24, BAD),
      text(0, 300, "진짜 성과는 반응률이 아니라 발급 뒤 이용과 유지", 26, INK, weight="bold")]
figs["p-line"] = svg(320, "\n".join(b))

# 망분리
b = [text(0, 34, "망분리 개선 (금융당국)", 28, TXT, weight="bold")]
for i, (d, t, st) in enumerate([("2024년 8월", "개선 로드맵: 가명처리 정보부터 생성형 AI 처리 허용 시작", False),
                                ("2026년", "전면 해제 추진 방침 — 아직 방침 단계", True)]):
    y = 60 + i * 100
    b += [rect(0, y, 190, 80, INK, INK, 0, 10), text(95, y + 50, d, 24, FILL, "middle", "bold"),
          rect(204, y, W - 204, 80, BAD if st else LINE, FILL, 3, 10), text(224, y + 50, t, 22, TXT)]
b += [text(0, 300, "우리 회사 원칙(토의)", 26, INK, weight="bold")]
for i, t in enumerate(["가명처리한 데이터와 집계된 표부터", "읽기 전용으로", "원본을 고칠 권한은 아주 나중에"]):
    b += [rect(0, 320 + i * 64, W, 54, INK, SOFT, 2, 8), text(24, 356 + i * 64, t, 24, TXT)]
figs["p-netsep"] = svg(520, "\n".join(b))

# 에이전트를 우리 업무에
b = []
for i, (t, s1, s2) in enumerate([("고객 언어", "상담 녹취·고객의 소리", "마스킹은 파이프라인에 박는다"),
                                 ("구매 계기", "해외 항공권 결제 같은 순간", "고객이 동의한 이용 목적 안에서만"),
                                 ("놓친 거래", "발급 신청 중 멈춘 고객", "바로 쓰고 싶은 첫 후보")]):
    y = i * 170
    b += [rect(0, y, W, 150, LINE, FILL, 3), text(26, y + 48, t + " 에이전트", 30, INK, weight="bold"),
          text(26, y + 94, s1, 25, TXT), text(26, y + 132, s2, 23, BAD if i == 1 else GRAY)]
figs["p-agents"] = svg(500, "\n".join(b))

# 모집 혜택 한도
b = [box(0, 0, W, 190, "여신전문금융업법", ["회원 모집 때 줄 수 있는 경제적 이익에 한도", "오프라인 모집: 연회비의 10%가 기준"], True),
     rect(0, 230, W, 90, INK, SOFT, 3), text(444, 286, "혜택 크기도 에이전트가 아니라 코드가 계산", 28, INK, "middle", "bold")]
figs["p-benefit"] = svg(330, "\n".join(b))

# 승인 대기열 = 심의 대기열
b = [text(0, 34, "크리에이티브 에이전트가 문구를 만들면", 26, TXT, weight="bold"),
     box(0, 60, 420, 220, "심의 통과 문구 조합", ["이미 심의를 거친 조각만", "→ 빠르게 내보낸다"], True),
     box(468, 60, 420, 220, "새 표현", ["심의 대기열로", "준법감시인 내부 심의", "업권 따라 협회 심의"]),
     text(0, 340, "금융소비자보호법: 광고 전 내부 심의", 24, GRAY),
     text(0, 382, "원문의 승인 대기열이 카드사에서는 심의 대기열", 26, INK, weight="bold")]
figs["p-review"] = svg(400, "\n".join(b))

# 자동화된 결정
b = [box(0, 0, 420, 250, "광고 대상 고르기", ["누구에게 보낼까", "중대한 영향으로 보긴", "어려울 수 있다"]),
     box(468, 0, 420, 250, "권리·의무에 닿는 결정", ["한도 상향 · 금리 우대", "→ 거부·설명 요구 대상", "(개인정보보호법 2024.3)"], True),
     text(0, 300, "신용정보법: 자동화평가 설명 요구권", 24, GRAY),
     rect(0, 330, W, 150, BAD, FILL, 3), text(26, 376, "에이전트가 손대지 않는 목록", 28, BAD, weight="bold"),
     text(26, 420, "대출성 상품 권유 · 한도 · 금리", 25, TXT), text(26, 458, "+ 왜 이 고객이 뽑혔는지 기록을 남긴다", 23, GRAY)]
figs["p-decision"] = svg(490, "\n".join(b))

# 우리 회사의 일주일
b = []
for i, (d, s1, s2) in enumerate([("월", "고객 언어: \"해외 수수료가 얼마 나갔는지 모르겠다\"", "제안: 해외 결제 수수료 우대 카드 (심의필 문구)"),
                                 ("화", "해외 결제 잦고 우대 카드 없는 고객 목록", "캠페인 ID를 붙인다"),
                                 ("수", "발송 엔진이 동의·야간 시간대를 걸러 낸다", "새 문구 두 개는 심의 대기열로"),
                                 ("2주 뒤", "발급 → 첫 이용 → 해외 결제 이용액", "표본이 작으면 작다고 적는다")]):
    y = i * 130
    b += [rect(0, y, 150, 116, INK, INK, 0, 10), text(75, y + 70, d, 28, FILL, "middle", "bold"),
          rect(164, y, W - 164, 116, LINE, FILL, 3, 10), text(184, y + 48, s1, 22, TXT), text(184, y + 90, s2, 21, GRAY)]
figs["p-week"] = svg(520, "\n".join(b))

# 내일부터
b = []
for i, (r, t) in enumerate([("기획", "상담 녹취 스무 건 마스킹 → 고객 언어 에이전트, 심의 통과 문구 목록"),
                            ("모델", "캠페인 ID 표: 발송부터 6개월 유지까지 한 줄"),
                            ("실행", "동의·야간·광고 표기·발송 횟수를 엔진 규칙으로"),
                            ("플랫폼", "에이전트 권한 표: 읽기 전용·가명·초안만·일시정지만")]):
    y = i * 112
    b += [rect(0, y, 150, 96, INK, INK, 0, 10), text(75, y + 58, r, 26, FILL, "middle", "bold"),
          rect(164, y, W - 164, 96, LINE, FILL, 3, 10), text(184, y + 58, t, 21, TXT)]
figs["p-todo"] = svg(450, "\n".join(b))

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
