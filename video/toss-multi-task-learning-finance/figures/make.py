#!/usr/bin/env python3
"""'목적마다, 상품마다 늘던 모델을 하나로' 회차 화면용 다이어그램을 SVG 로 그린다(원문 그림 없이 개념을 새로 그림).  python3 make.py
모션 그래픽 네 편(explosion·ple·mask·shortcut)은 ../../remotion/src/toss/ 의 Remotion 컴포지션."""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT = "#3F7A66", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
OK, OKT, WARN, WARNT, BAD, BADT, INKT = "#4E8F76", "#EAF3EE", "#C9963A", "#F8F0E0", "#C0605A", "#F6E7E5", "#E3EEEA"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def arrow(x1, y1, x2, y2, color=INK, sw=4):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#a)"/>'


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def card(x, y, w, h, head, sub, stroke=LINE, fill=FILL, hc=TXT, hs=32, ss=26):
    """머리글 + 설명(문자열 또는 줄 목록). 줄 간격 40px, 전체를 상자 가운데에."""
    subs = [sub] if isinstance(sub, str) else sub
    top = y + h / 2 - (hs + 14 + 40 * len(subs)) / 2 + hs - 4
    return [rect(x, y, w, h, stroke, fill, 3, 16), text(x + w / 2, top, head, hs, hc, "middle", "bold"),
            *[text(x + w / 2, top + 14 + 40 * (k + 1) - 6, s, ss, GRAY, "middle") for k, s in enumerate(subs)]]


figs = {}
# 세로 영상 본문 폭 888px 에 그대로 놓인다(1px = 화면 1px). 높이는 700 이하, 약어 각주가 붙는 화면(topn·case2-results·seesaw)은 600 안팎.

# 모델이 많으면 생기는 비용 네 가지
rows = [("운영", "모델마다 데이터 준비 · 학습 · 배포 · 모니터링"), ("재학습", "수백 개를 자주 못 돌려 오래 그대로 남는다"),
        ("실험", "새 데이터 효과를 보려면 모델마다 다시 학습"), ("드문 과제", "데이터가 모자라다 · 새 상품은 모델이 없다")]
b = []
for i, (h, sub) in enumerate(rows):
    y = i * 176
    b += [rect(0, y, W, 156, WARN if i == 0 else LINE, WARNT if i == 0 else FILL, 3, 16),
          text(32, y + 62, h, 36, WARN if i == 0 else TXT, weight="bold"), text(32, y + 118, sub, 28, GRAY)]
figs["costs"] = svg(684, "\n".join(b))

# 멀티태스크 학습의 두 쓰임새
b = []
for x, title, c1, c2, tag, col, fill in [(0, "공유 표현을 넘긴다", ("멀티태스크 모델", ["여러 행동을", "함께 학습"]), ("다른 서비스 모델", ["표현을", "가져다 쓴다"]), "지난 글 TASTE", LINE, SOFT),
                                         (468, "예측값을 바로 쓴다", ("멀티태스크 모델", ["여러 과제를", "함께 학습"]), ("마케팅 · 서비스", ["예측을", "바로 쓴다"]), "이번 글", INK, INKT)]:
    hc = INK if col == INK else TXT
    b += [rect(x, 0, 420, 690, col, fill, 4 if col == INK else 0, 18), text(x + 210, 62, title, 32, hc, "middle", "bold"),
          *card(x + 30, 106, 360, 190, *c1, col, FILL, hc), arrow(x + 210, 308, x + 210, 372, INK, 5),
          *card(x + 30, 384, 360, 190, *c2, col, FILL, hc), text(x + 210, 640, tag, 30, hc, "middle", "bold")]
figs["two-uses"] = svg(690, "\n".join(b))

# 드문 과제가 큰 과제에서 배운다 + 입력 모양
b = [text(0, 38, "공유 부분은 모든 과제의 데이터로 배운다", 32, TXT, weight="bold")]
for i, (name, n) in enumerate([("흔한 과제", 9), ("보통 과제", 5), ("드문 과제", 1)]):
    x = i * 304
    b += [rect(x, 70, 280, 140, OK if i == 2 else LINE, OKT if i == 2 else FILL, 3, 16), text(x + 140, 122, name, 30, TXT, "middle", "bold")]
    b += [f'<circle cx="{x + 28 + k * 28}" cy="172" r="11" fill="{INK}"/>' for k in range(n)]
    b.append(arrow(x + 140, 220, 444, 282, LINE, 4))
b += [rect(104, 290, 680, 100, INK, INKT, 4, 18), text(444, 352, "공유 인코더 · 공유 전문가", 34, INK, "middle", "bold"),
      text(0, 472, "입력도 넓어진다", 32, TXT, weight="bold"),
      *card(0, 500, 420, 190, "트리 모델", ["표 한 줄로 편다", "순서는 집계해 넣는다"]),
      *card(468, 500, 420, 190, "신경망", ["시간 순 기록 그대로", "상품 묶음 그대로"], INK, INKT, INK)]
figs["share"] = svg(690, "\n".join(b))

# 사례 1 구조
b = [text(444, 34, "수십 개 행동 확률을 한 번에", 30, GRAY, "middle", "bold")]
for k in range(10):
    x = 4 + k * 88
    b += [rect(x, 58, 76, 84, INK if k % 4 == 0 else LINE, FILL, 3, 10), text(x + 38, 112, "%", 28, GRAY, "middle")]
b += [arrow(444, 202, 444, 152),
      rect(0, 212, 420, 100, INK, INKT, 3, 16), text(210, 274, "공유 전문가", 32, INK, "middle", "bold"),
      rect(468, 212, 420, 100, WARN, WARNT, 3, 16), text(678, 274, "행동별 전문가", 32, TXT, "middle", "bold"),
      arrow(444, 382, 444, 322),
      rect(124, 392, 640, 92, INK, INKT, 4, 16), text(444, 450, "두 요약을 섞는다", 32, INK, "middle", "bold"),
      arrow(210, 554, 330, 494), arrow(678, 554, 558, 494),
      *card(0, 562, 420, 138, "최근 행동 기록", "시간 순서대로 읽는다"), *card(468, 562, 420, 138, "유저 프로필", "동의 기반 정보만")]
figs["case1"] = svg(700, "\n".join(b))

# AUC 는 그대로, AP 는 크게: 상위 N명 (약어 각주 두 줄이 아래에 붙는다)
b = [text(0, 30, "목적별 트리 모델 대비 (상대값)", 28, GRAY)]
for i, (name, v, note) in enumerate([("AP", 54, "약 54% 개선"), ("상위 N명 재현율", 20, "약 20% 개선"), ("AUC", 1, "거의 같음")]):
    y = 54 + i * 104
    b += [text(0, y + 32, name, 32, TXT, weight="bold"), text(W, y + 32, note, 30, INK if v > 1 else GRAY, "end", "bold"),
          rect(0, y + 48, W, 44, LINE, SOFT, 0, 10), rect(0, y + 48, max(14, v * 12), 44, INK, INK if v > 1 else LINE, 0, 10)]
b += [rect(0, 374, W, 162, LINE, FILL, 3, 16), text(30, 424, "AUC  전체 순위가 잘 섰나", 30, TXT, weight="bold"),
      text(30, 474, "AP · 상위 재현율  맨 위 N명이 정확한가", 30, INK, weight="bold"),
      text(30, 516, "마케팅이 실제로 쓰는 건 맨 위 N명", 26, GRAY)]
figs["topn"] = svg(538, "\n".join(b))

# 온라인 결과
b = []
for x, name, big1, l1, big2, l2 in [(0, "상품군 1", "−35%", "불필요한 발송", "약 2배", "발송 대비 효율"), (468, "상품군 2", "1.7배", "클릭률", "수 배", "최종 전환율")]:
    c = x + 210
    b += [rect(x, 0, 420, 560, INK, INKT, 4, 18), text(c, 66, name, 36, INK, "middle", "bold"),
          text(c, 214, big1, 92, INK, "middle", "bold"), text(c, 270, l1, 30, GRAY, "middle"),
          text(c, 420, big2, 68, INK, "middle", "bold"), text(c, 476, l2, 30, GRAY, "middle")]
b += [text(444, 626, "기존 모델 세그먼트와 A/B 테스트", 30, GRAY, "middle"), text(444, 676, "둘 다 p < 0.001", 30, GRAY, "middle")]
figs["online"] = svg(690, "\n".join(b))

# 사례 2 구조
b = []
for k, (h, sub) in enumerate([("① 분류", "예 / 아니오"), ("② 수치", "①이 예일 때"), ("③ 수치", "①이 예일 때")]):
    x = k * 304
    b += [rect(x, 0, 280, 120, LINE, FILL, 3, 16), text(x + 140, 50, h, 32, TXT, "middle", "bold"), text(x + 140, 94, sub, 26, GRAY, "middle")]
    if k:
        b.append(arrow(x - 22, 60, x - 4, 60, GRAY, 3))
b += [arrow(444, 196, 444, 130),
      rect(0, 206, 280, 110, INK, INKT, 3, 16), text(140, 254, "공유", 30, INK, "middle", "bold"), text(140, 292, "전문가", 30, INK, "middle", "bold"),
      rect(304, 206, 280, 110, WARN, WARNT, 3, 16), text(444, 254, "과제별", 30, TXT, "middle", "bold"), text(444, 292, "전문가", 30, TXT, "middle", "bold"),
      rect(608, 206, 280, 110, OK, OKT, 3, 16), text(748, 254, "상품 종류별", 30, OK, "middle", "bold"), text(748, 292, "전문가", 30, OK, "middle", "bold"),
      arrow(444, 388, 444, 326),
      rect(144, 398, 600, 92, INK, INKT, 4, 16), text(444, 456, "이 유저 × 이 상품", 32, INK, "middle", "bold"),
      arrow(150, 562, 300, 500), arrow(738, 562, 588, 500),
      *card(0, 570, 300, 130, "유저", "한 번 요약"), *card(588, 570, 300, 130, "상품들", "상품마다 요약")]
figs["case2"] = svg(700, "\n".join(b))

# 사례 2 결과 (약어 각주 한 줄)
b = [text(0, 30, "상품별 트리 모델 대비", 28, GRAY)]
for i, (name, v, note) in enumerate([("수치 과제 ① 오차", 21, "MAE 약 79% 감소"), ("수치 과제 ② 오차", 34, "MAE 약 66% 감소")]):
    y = 60 + i * 176
    b += [text(0, y + 32, name, 32, TXT, weight="bold"), text(W, y + 32, note, 30, INK, "end", "bold"),
          rect(0, y + 52, W, 48, LINE, SOFT, 0, 10), text(W - 14, y + 86, "기존 100", 26, GRAY, "end"),
          rect(0, y + 108, W * v / 100, 48, INK, INK, 0, 10), text(W * v / 100 + 14, y + 142, f"{v}", 28, INK, weight="bold")]
b += [rect(0, 424, W, 120, OK, OKT, 3, 16), text(444, 498, "분류 과제 AUC 약 10% 향상 (상대값)", 34, OK, "middle", "bold"),
      text(444, 594, "같은 유저 · 같은 상품만 모아 같은 실제 결과로 채점", 26, GRAY, "middle")]
figs["case2-results"] = svg(610, "\n".join(b))

# 시소: 부정적 전이 (약어 각주 한 줄)
b = [text(444, 40, "공유층을 거치는 한", 34, TXT, "middle", "bold"),
     text(444, 90, "한 과제를 위한 변경이 다른 과제를 해칠 수 있다", 28, GRAY, "middle"),
     f'<polygon points="444,318 400,392 488,392" fill="{GRAY}"/>',
     f'<line x1="84" y1="370" x2="804" y2="266" stroke="{TXT}" stroke-width="12" stroke-linecap="round"/>',
     rect(34, 254, 240, 96, OK, OKT, 3, 16), text(154, 314, "과제 A ↑", 34, OK, "middle", "bold"),
     rect(614, 150, 240, 96, BAD, BADT, 3, 16), text(734, 210, "과제 B ↓", 34, BAD, "middle", "bold"),
     rect(0, 420, W, 190, INK, INKT, 3, 16), text(444, 470, "부정적 전이", 32, INK, "middle", "bold"),
     text(444, 518, "PLE의 과제별 전문가와 게이트로 줄인다", 28, INK, "middle"),
     text(444, 566, "손실은 과제마다 표준화, 손실 함수도 분포에 맞게", 26, GRAY, "middle")]
figs["seesaw"] = svg(610, "\n".join(b))

# 무엇끼리 묶을까
b = [*card(0, 0, 420, 150, "같은 유저의 행동끼리", ["사례 1", "수십 개 금융 행동"], INK, INKT, INK, 30),
     *card(468, 0, 420, 150, "같은 상품의 과제끼리", ["사례 2", "분류 하나 + 수치 둘"], INK, INKT, INK, 30),
     *card(0, 180, W, 170, "Meta Lattice (KDD 2026)", ["수천 개 광고 모델을 비슷한 것끼리 묶어 몇 개로", "인프라 약 20% 절감"]),
     rect(0, 380, W, 110, BAD, BADT, 3, 16), text(444, 447, "무작정 합치면 품질이 떨어진다", 34, BAD, "middle", "bold"),
     *card(0, 520, W, 170, "합치기 전에 과제별 평가 기준부터", "평균은 좋아져도 일부 과제는 나빠질 수 있다", WARN, WARNT)]
figs["group"] = svg(690, "\n".join(b))

if __name__ == "__main__":
    here = Path(__file__).parent
    for name, s in figs.items():
        (here / f"{name}.svg").write_text(s, encoding="utf-8")
    print(len(figs), "개:", ", ".join(figs))
