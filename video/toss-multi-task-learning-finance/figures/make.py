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


def card(x, y, w, h, head, sub, stroke=LINE, fill=FILL, hc=TXT):
    return [rect(x, y, w, h, stroke, fill, 3, 16), text(x + w / 2, y + h / 2 - 6, head, 28, hc, "middle", "bold"),
            text(x + w / 2, y + h / 2 + 34, sub, 22, GRAY, "middle")]


figs = {}

# 모델이 많으면 생기는 비용 네 가지
rows = [("운영", "모델마다 데이터 준비 · 학습 · 배포 · 모니터링"), ("재학습", "수백 개를 자주 못 돌려 오래 그대로 남는다"),
        ("실험", "새 데이터 효과를 보려면 모델마다 다시 학습"), ("드문 과제", "혼자 배우기엔 데이터가 모자라다 · 새 상품은 모델이 없다")]
b = []
for i, (h, sub) in enumerate(rows):
    y = i * 130
    b += [rect(0, y, W, 110, WARN if i == 0 else LINE, WARNT if i == 0 else FILL, 3, 16),
          text(32, y + 66, h, 30, WARN if i == 0 else TXT, weight="bold"), text(220, y + 66, sub, 24, GRAY)]
figs["costs"] = svg(510, "\n".join(b))

# 멀티태스크 학습의 두 쓰임새
b = [rect(0, 0, 420, 420, LINE, SOFT, 0, 18), text(210, 52, "공유 표현을 넘긴다", 28, TXT, "middle", "bold"),
     *card(60, 90, 300, 90, "멀티태스크 모델", "여러 행동을 함께 학습"),
     arrow(210, 190, 210, 244),
     *card(60, 254, 300, 90, "다른 서비스 모델", "표현을 가져다 쓴다"),
     text(210, 392, "지난 글 TASTE", 24, GRAY, "middle"),
     rect(468, 0, 420, 420, INK, INKT, 4, 18), text(678, 52, "예측값 자체를 맞힌다", 28, INK, "middle", "bold"),
     *card(528, 90, 300, 90, "멀티태스크 모델", "여러 과제를 함께 학습", INK),
     arrow(678, 190, 678, 244),
     *card(528, 254, 300, 90, "마케팅 · 서비스", "예측을 바로 쓴다", INK),
     text(678, 392, "이번 글", 24, INK, "middle", "bold")]
figs["two-uses"] = svg(430, "\n".join(b))

# 드문 과제가 큰 과제에서 배운다 + 입력 모양
b = [text(0, 34, "공유 부분은 모든 과제의 데이터로 배운다", 28, TXT, weight="bold")]
for i, (name, n) in enumerate([("흔한 과제", 9), ("보통 과제", 5), ("드문 과제", 1)]):
    x = i * 300
    b += [rect(x, 64, 270, 120, OK if i == 2 else LINE, OKT if i == 2 else FILL, 3, 16), text(x + 135, 106, name, 26, TXT, "middle", "bold")]
    b += [f'<circle cx="{x + 30 + k * 26}" cy="152" r="9" fill="{INK}"/>' for k in range(n)]
    b.append(arrow(x + 135, 194, 444, 262, LINE, 3))
b += [rect(144, 270, 600, 90, INK, INKT, 4, 18), text(444, 326, "공유 인코더 · 공유 전문가", 30, INK, "middle", "bold"),
      text(0, 420, "입력도 넓어진다", 28, TXT, weight="bold"),
      *card(0, 446, 420, 110, "트리 모델", "표 한 줄 · 순서는 집계해 편다"),
      *card(468, 446, 420, 110, "신경망", "시간 순 기록 · 상품 묶음 그대로", INK, INKT, INK)]
figs["share"] = svg(566, "\n".join(b))

# 사례 1 구조
b = [*card(0, 470, 420, 100, "최근 행동 기록", "시간 순서대로 읽는다"), *card(468, 470, 420, 100, "유저 프로필", "동의 기반 정보만"),
     arrow(210, 460, 380, 400), arrow(678, 460, 508, 400),
     rect(144, 320, 600, 76, INK, INKT, 4, 16), text(444, 370, "두 요약을 섞는다", 28, INK, "middle", "bold"),
     arrow(444, 312, 444, 262),
     rect(0, 170, 420, 84, INK, INKT, 3, 16), text(210, 222, "공유 전문가", 28, INK, "middle", "bold"),
     rect(468, 170, 420, 84, WARN, WARNT, 3, 16), text(678, 222, "행동별 전문가", 28, TXT, "middle", "bold"),
     arrow(444, 162, 444, 116)]
for k in range(12):
    x = 14 + k * 72
    b += [rect(x, 30, 58, 70, INK if k % 4 == 0 else LINE, FILL, 3, 10), text(x + 29, 74, "%", 22, GRAY, "middle")]
b.append(text(444, 18, "수십 개 행동 확률을 한 번에", 24, GRAY, "middle"))
figs["case1"] = svg(580, "\n".join(b))

# AUC 는 그대로, AP 는 크게: 상위 N명
b = [text(0, 34, "목적별 트리 모델 대비 (상대값)", 26, GRAY)]
for i, (name, v, note) in enumerate([("AP", 54, "약 54% 개선"), ("상위 N명 재현율", 20, "약 20% 개선"), ("AUC", 1, "거의 같음")]):
    y = 70 + i * 100
    b += [text(0, y + 48, name, 28, TXT, weight="bold"), rect(250, y + 10, 420, 56, LINE, SOFT, 0, 10),
          rect(250, y + 10, max(10, v * 7), 56, INK, INK if v > 1 else LINE, 0, 10), text(W, y + 48, note, 24, INK if v > 1 else GRAY, "end", "bold")]
b += [rect(0, 400, W, 150, LINE, FILL, 3, 16), text(30, 446, "AUC  전체 순위가 잘 섰나", 26, TXT, weight="bold"),
      text(30, 500, "AP · 상위 재현율  맨 위 N명이 정확한가", 26, INK, weight="bold"),
      text(30, 536, "마케팅이 실제로 쓰는 건 맨 위 N명", 22, GRAY)]
figs["topn"] = svg(560, "\n".join(b))

# 온라인 결과
b = [rect(0, 0, 420, 400, INK, INKT, 4, 18), text(210, 54, "상품군 1", 30, INK, "middle", "bold"),
     text(210, 160, "−35%", 72, INK, "middle", "bold"), text(210, 206, "불필요한 발송", 24, GRAY, "middle"),
     text(210, 300, "약 2배", 52, INK, "middle", "bold"), text(210, 344, "발송 대비 효율", 24, GRAY, "middle"),
     rect(468, 0, 420, 400, INK, INKT, 4, 18), text(678, 54, "상품군 2", 30, INK, "middle", "bold"),
     text(678, 160, "1.7배", 72, INK, "middle", "bold"), text(678, 206, "클릭률", 24, GRAY, "middle"),
     text(678, 300, "수 배", 52, INK, "middle", "bold"), text(678, 344, "최종 전환율", 24, GRAY, "middle"),
     text(444, 452, "기존 모델 세그먼트와 A/B 테스트 · 둘 다 p < 0.001", 24, GRAY, "middle")]
figs["online"] = svg(470, "\n".join(b))

# 사례 2 구조
b = [*card(0, 470, 300, 90, "유저", "한 번 요약"), *card(588, 470, 300, 90, "상품들", "상품마다 요약"),
     arrow(150, 460, 360, 410), arrow(738, 460, 528, 410),
     rect(194, 330, 500, 76, INK, INKT, 4, 16), text(444, 380, "이 유저 × 이 상품", 28, INK, "middle", "bold"),
     arrow(444, 322, 444, 276),
     rect(0, 186, 280, 84, INK, INKT, 3, 16), text(140, 238, "공유 전문가", 26, INK, "middle", "bold"),
     rect(304, 186, 280, 84, WARN, WARNT, 3, 16), text(444, 238, "과제별 전문가", 26, TXT, "middle", "bold"),
     rect(608, 186, 280, 84, OK, OKT, 3, 16), text(748, 238, "상품 종류별 전문가", 24, OK, "middle", "bold"),
     arrow(444, 178, 444, 132)]
for k, (h, sub) in enumerate([("① 분류", "예 / 아니오"), ("② 수치", "①이 예일 때만"), ("③ 수치", "①이 예일 때만")]):
    x = k * 304
    b += [rect(x, 30, 280, 90, LINE, FILL, 3, 16), text(x + 140, 70, h, 26, TXT, "middle", "bold"), text(x + 140, 104, sub, 20, GRAY, "middle")]
    if k:
        b.append(arrow(x - 22, 75, x - 4, 75, GRAY, 3))
figs["case2"] = svg(570, "\n".join(b))

# 사례 2 결과
b = [text(0, 34, "상품별 트리 모델 대비", 26, GRAY)]
for i, (name, v, note, good) in enumerate([("수치 과제 ① 오차", 21, "MAE 약 79% 감소", True), ("수치 과제 ② 오차", 34, "MAE 약 66% 감소", True)]):
    y = 70 + i * 150
    b += [text(0, y + 30, name, 28, TXT, weight="bold"), text(W, y + 30, note, 26, INK, "end", "bold"),
          rect(0, y + 50, W, 40, LINE, SOFT, 0, 10), text(W - 10, y + 80, "기존 100", 20, GRAY, "end"),
          rect(0, y + 96, W * v / 100, 40, INK, INK, 0, 10), text(W * v / 100 + 12, y + 126, f"{v}", 22, INK, weight="bold")]
b += [rect(0, 380, W, 110, OK, OKT, 3, 16), text(444, 446, "분류 과제 AUC 약 10% 향상 (상대값)", 30, OK, "middle", "bold"),
      text(444, 536, "같은 유저 · 같은 상품만 모아 같은 실제 결과로 채점", 22, GRAY, "middle")]
figs["case2-results"] = svg(550, "\n".join(b))

# 시소: 부정적 전이
b = [f'<polygon points="444,330 404,400 484,400" fill="{GRAY}"/>',
     f'<line x1="104" y1="380" x2="784" y2="280" stroke="{TXT}" stroke-width="10" stroke-linecap="round"/>',
     rect(54, 296, 200, 80, OK, OKT, 3, 16), text(154, 346, "과제 A ↑", 28, OK, "middle", "bold"),
     rect(634, 196, 200, 80, BAD, BADT, 3, 16), text(734, 246, "과제 B ↓", 28, BAD, "middle", "bold"),
     text(444, 60, "공유층을 거치는 한", 28, TXT, "middle", "bold"),
     text(444, 104, "한 과제를 위한 변경이 다른 과제를 해칠 수 있다", 24, GRAY, "middle"),
     rect(0, 450, W, 100, INK, INKT, 3, 16), text(444, 494, "부정적 전이 → PLE 의 과제별 전문가와 게이트로 줄인다", 26, INK, "middle", "bold"),
     text(444, 532, "손실은 과제마다 표준화하고 손실 함수도 분포에 맞게", 21, GRAY, "middle")]
figs["seesaw"] = svg(560, "\n".join(b))

# 무엇끼리 묶을까
b = [*card(0, 0, 420, 120, "같은 유저의 행동끼리", "사례 1 · 수십 개 금융 행동", INK, INKT, INK),
     *card(468, 0, 420, 120, "같은 상품의 과제끼리", "사례 2 · 분류 하나 + 수치 둘", INK, INKT, INK),
     rect(0, 160, W, 120, LINE, FILL, 3, 16), text(444, 208, "Meta Lattice (KDD 2026)", 28, TXT, "middle", "bold"),
     text(444, 252, "수천 개 광고 모델을 비슷한 것끼리 묶어 몇 개로 · 인프라 약 20% 절감", 22, GRAY, "middle"),
     rect(0, 320, W, 110, BAD, BADT, 3, 16), text(444, 386, "무작정 합치면 품질이 떨어진다", 30, BAD, "middle", "bold"),
     rect(0, 460, W, 110, WARN, WARNT, 3, 16), text(444, 506, "합치기 전에 과제별 평가 기준부터", 28, TXT, "middle", "bold"),
     text(444, 546, "평균은 좋아져도 일부 과제는 나빠질 수 있다", 22, GRAY, "middle")]
figs["group"] = svg(580, "\n".join(b))

if __name__ == "__main__":
    here = Path(__file__).parent
    for name, s in figs.items():
        (here / f"{name}.svg").write_text(s, encoding="utf-8")
    print(len(figs), "개:", ", ".join(figs))
