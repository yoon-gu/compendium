#!/usr/bin/env python3
"""'예측을 넘어 결정과 발견으로' 회차 화면용 다이어그램을 SVG 로 그린다(원문 그림 없이 개념을 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT = "#3F7A66", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
OK, OKT, WARN, WARNT, BAD, BADT, INKT = "#4E8F76", "#EAF3EE", "#C9963A", "#F8F0E0", "#C0605A", "#F6E7E5", "#E3EEEA"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
MONO = 'font-family="NanumGothicCoding, monospace"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal", mono=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'{MONO if mono else F} xml:space="preserve">{escape(s, quote=False)}</text>')


def rect(x, y, w, h, stroke=LINE, fill=FILL, sw=3, rx=14, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def arrow(x1, y1, x2, y2, color=INK, sw=4):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#a)"/>'


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


figs = {}

# 질문이 바뀌었다: 점수 하나 → 무엇을 보여 줄까
b = [rect(0, 0, 400, 260, LINE, SOFT, 0, 18), text(200, 52, "예전 질문", 28, GRAY, "middle", "bold"),
     text(200, 120, "이 고객이 누를", 28, TXT, "middle"), text(200, 166, "확률은 얼마?", 28, TXT, "middle"),
     text(200, 226, "CTR · CVR 점수", 24, GRAY, "middle"),
     arrow(412, 130, 474, 130),
     rect(488, 0, 400, 260, INK, INKT, 4, 18), text(688, 52, "지금 질문", 28, INK, "middle", "bold"),
     text(688, 120, "이 고객에게 지금", 28, TXT, "middle", "bold"), text(688, 166, "무엇을 보여 줄까?", 28, TXT, "middle", "bold"),
     text(688, 226, "점수 + 제약 → 결정", 24, INK, "middle")]
chans = ["검색", "추천", "광고", "앱 푸시", "쿠폰", "배너"]
for i, c in enumerate(chans):
    x = i * 148
    b += [rect(x, 330, 130, 64, LINE, FILL, 3, 32), text(x + 65, 372, c, 24, TXT, "middle"),
          arrow(x + 65, 404, 444, 470, LINE, 2)]
b += [rect(244, 480, 400, 80, INK, FILL, 3, 40), text(444, 530, "하나의 질문으로 모인다", 26, INK, "middle", "bold")]
figs["question"] = svg(570, "\n".join(b))

# 자원에는 늘 한계가 있다
rows = [("하루 푸시", 5, 2, "보낼 수 있는 통수"), ("이달 쿠폰 예산", 5, 3, "쓸 수 있는 금액"), ("한 화면 상품 칸", 5, 4, "들어가는 상품 수")]
b = []
for i, (h, n, used, sub) in enumerate(rows):
    y = i * 180
    b += [text(0, y + 40, h, 30, TXT, weight="bold"), text(W, y + 40, sub, 24, GRAY, "end")]
    for k in range(n):
        x = k * 178
        full = k < used
        b.append(rect(x, y + 64, 158, 80, INK if full else LINE, INKT if full else FILL, 3, 12))
b += [rect(0, 560, W, 96, WARN, WARNT, 3, 16), text(444, 618, "확률을 구한 뒤에도 누구에게 줄지는 따로 정한다", 26, WARN, "middle", "bold")]
figs["limits"] = svg(660, "\n".join(b))

# 업리프트: 두 세계
b = [text(444, 34, "같은 고객 B, 두 세계", 30, TXT, "middle", "bold"),
     rect(0, 70, 410, 250, INK, INKT, 4, 18), text(205, 122, "푸시를 받은 세계", 28, INK, "middle", "bold"),
     text(205, 220, "10%", 64, INK, "middle", "bold"), text(205, 284, "구매 확률", 24, GRAY, "middle"),
     rect(478, 70, 410, 250, LINE, SOFT, 3, 18), text(683, 122, "받지 않은 세계", 28, GRAY, "middle", "bold"),
     text(683, 220, "2%", 64, GRAY, "middle", "bold"), text(683, 284, "구매 확률", 24, GRAY, "middle"),
     text(444, 210, "−", 56, TXT, "middle", "bold"),
     arrow(444, 340, 444, 392),
     rect(144, 400, 600, 110, OK, OKT, 4, 18), text(444, 452, "증분 효과 = 8%p", 34, OK, "middle", "bold"),
     text(444, 492, "푸시가 실제로 만든 차이", 24, GRAY, "middle"),
     text(0, 570, "한 사람이 두 세계를 다 살 수는 없다", 26, TXT, weight="bold"),
     text(0, 616, "→ 비슷한 고객들의 데이터로 모델이 추정한다 (업리프트 모델링)", 24, GRAY),
     text(W, 666, "숫자는 설명용 가상 값", 20, GRAY, "end")]
figs["two-worlds"] = svg(680, "\n".join(b))

# 축적: 한 번 만든 이해를 다른 문제에 다시 쓴다
b = [rect(0, 0, 360, 120, LINE, FILL, 3, 16), text(180, 52, "광고", 30, TXT, "middle", "bold"), text(180, 94, "고객 표현을 배운다", 22, GRAY, "middle"),
     rect(0, 170, 360, 120, LINE, FILL, 3, 16), text(180, 222, "추천", 30, TXT, "middle", "bold"), text(180, 264, "상품 임베딩을 배운다", 22, GRAY, "middle"),
     arrow(370, 60, 440, 150), arrow(370, 230, 440, 160),
     rect(450, 80, 438, 150, INK, INKT, 4, 18), text(669, 140, "쌓아 둔 이해", 32, INK, "middle", "bold"),
     text(669, 188, "고객 표현 · 상품 임베딩", 24, GRAY, "middle"),
     arrow(560, 240, 400, 370), arrow(778, 240, 760, 370),
     rect(150, 380, 340, 110, OK, OKT, 3, 16), text(320, 430, "푸시 평가", 30, OK, "middle", "bold"), text(320, 470, "고객 표현을 다시 쓴다", 22, GRAY, "middle"),
     rect(548, 380, 340, 110, OK, OKT, 3, 16), text(718, 430, "검색 순위", 30, OK, "middle", "bold"), text(718, 470, "임베딩을 다시 쓴다", 22, GRAY, "middle"),
     rect(0, 540, W, 110, LINE, SOFT, 0, 16),
     text(28, 586, "임베딩: 상품을 숫자 여러 개로 된 좌표로 바꾼 것", 25, TXT, weight="bold"),
     text(28, 626, "비슷한 상품은 좌표도 가깝다", 23, GRAY)]
figs["reuse"] = svg(660, "\n".join(b))

# 같은 밴딧, 다른 문제
b = [rect(294, 0, 300, 110, INK, INKT, 4, 18), text(444, 50, "밴딧", 32, INK, "middle", "bold"),
     text(444, 88, "조금씩 시도 → 반응 좋은 쪽으로", 20, GRAY, "middle"),
     arrow(380, 120, 210, 200), arrow(508, 120, 678, 200),
     rect(0, 210, 420, 300, WARN, WARNT, 4, 18), text(210, 258, "결정 문제", 30, WARN, "middle", "bold"),
     text(210, 314, "푸시 문구 셋 중 하나", 25, TXT, "middle"), text(210, 360, "쓰는 자원: 발송 한 통", 23, GRAY, "middle"),
     text(210, 404, "보상: 실제로 달라진 행동", 23, GRAY, "middle"), text(210, 470, "→ DeciML", 28, WARN, "middle", "bold"),
     rect(468, 210, 420, 300, OK, OKT, 4, 18), text(678, 258, "발견 문제", 30, OK, "middle", "bold"),
     text(678, 314, "홈 피드에 올릴 상품", 25, TXT, "middle"), text(678, 360, "쓰는 자원: 고객의 시간", 23, GRAY, "middle"),
     text(678, 404, "보상: 세션 안에서 찾았나", 23, GRAY, "middle"), text(678, 470, "→ NeXA", 28, OK, "middle", "bold"),
     text(444, 580, "보상 · 학습 신호 · 내보내는 꼴이 달라진다", 26, TXT, "middle", "bold"),
     text(444, 626, "같은 기술에서 출발해도 다른 모델이 된다", 24, GRAY, "middle")]
figs["bandit"] = svg(650, "\n".join(b))

# 이름 풀이
b = [rect(0, 0, W, 290, WARN, WARNT, 4, 18),
     f'<text x="40" y="70" font-size="60" font-weight="bold" {F}><tspan fill="{WARN}">Deci</tspan><tspan fill="{TXT}">ML</tspan></text>',
     text(40, 128, "Decision + Machine Learning", 26, TXT, mono=True),
     text(40, 182, "읽으면 'decimal'(데시멀)", 26, GRAY),
     text(40, 240, "결정 · 광고 · 푸시 · 쿠폰 · 배너", 26, WARN, weight="bold"),
     rect(0, 330, W, 290, OK, OKT, 4, 18),
     text(40, 400, "NeXA", 60, OK, weight="bold"), text(250, 400, "넥사", 40, GRAY),
     text(40, 458, "Next eXploration Architecture", 26, TXT, mono=True),
     text(40, 512, "탐색(eXploration) + 노출 구조(Architecture)", 26, GRAY),
     text(40, 570, "발견 · 추천 · 검색 · 큐레이션", 26, OK, weight="bold")]
figs["names"] = svg(630, "\n".join(b))

# 프로젝트마다 같은 논의 → 표준 경로
topics = ["서빙 API 연결", "장애 처리", "배포 절차", "트래픽 감당", "서빙 자원"]
b = [text(0, 34, "예전: 모델마다 처음부터", 28, BAD, weight="bold")]
for p in range(3):
    x = p * 296
    b += [rect(x, 56, 272, 300, BAD, BADT, 3, 16), text(x + 136, 96, f"모델 {p + 1}", 26, BAD, "middle", "bold")]
    for k, tpc in enumerate(topics):
        b.append(text(x + 136, 146 + k * 46, tpc, 22, TXT, "middle"))
b += [text(0, 420, "지금: 표준 경로를 깔아 둔다", 28, OK, weight="bold"),
      rect(0, 444, W, 90, OK, OKT, 4, 45), text(444, 500, "서빙 → 배포 → 운영 (한 번 만든 길)", 28, OK, "middle", "bold"),
      text(0, 596, "성적표: 문제 정의 → 서비스 반영까지 걸린 시간", 26, INK, weight="bold")]
figs["repeat"] = svg(610, "\n".join(b))

# 기억 vs 읽을 수 있는 기록
b = [rect(0, 0, 410, 330, LINE, SOFT, 3, 18), text(205, 52, "담당자 머릿속", 30, GRAY, "middle", "bold"),
     text(205, 120, "왜 이렇게 풀었나", 24, GRAY, "middle"), text(205, 170, "어떤 조건에서 배포해도 되나", 22, GRAY, "middle"),
     rect(60, 210, 290, 80, BAD, BADT, 3, 40), text(205, 260, "에이전트는 못 읽는다", 24, BAD, "middle", "bold"),
     rect(478, 0, 410, 330, INK, INKT, 4, 18), text(683, 52, "플랫폼에 남긴 기록", 30, INK, "middle", "bold"),
     text(683, 120, "무엇을 바꿨나", 24, TXT, "middle"), text(683, 170, "어떤 테스트를 통과했나", 24, TXT, "middle"),
     text(683, 220, "왜 그렇게 골랐나", 24, TXT, "middle"),
     rect(538, 250, 290, 60, OK, OKT, 3, 30), text(683, 290, "사람도 에이전트도 읽는다", 22, OK, "middle", "bold"),
     text(0, 400, "같은 규칙", 28, TXT, weight="bold"),
     rect(0, 424, 410, 90, LINE, FILL, 3, 16), text(205, 480, "사람", 30, TXT, "middle", "bold"),
     rect(478, 424, 410, 90, LINE, FILL, 3, 16), text(683, 480, "에이전트", 30, TXT, "middle", "bold"),
     text(444, 570, "같은 기준으로 검증받고 같은 꼴로 남긴다", 25, INK, "middle", "bold"),
     text(444, 616, "담당자가 바뀌어도 맥락을 다시 캐지 않는다", 23, GRAY, "middle")]
figs["memory"] = svg(640, "\n".join(b))

# 바닥은 플랫폼, 그 위는 사람
b = [rect(0, 0, W, 250, LINE, FILL, 3, 18, "10 8"), text(444, 48, "그 위: DS · MLE의 몫", 30, INK, "middle", "bold")]
for i, s in enumerate(["어떤 문제를 풀까", "어떤 접근이 나을까", "동료와 쌓는 지식"]):
    b += [rect(40 + i * 274, 80 + (2 - i) * 40, 254, 84, INK, INKT, 3, 14), text(167 + i * 274, 130 + (2 - i) * 40, s, 23, INK, "middle", "bold")]
b += [rect(0, 270, W, 190, OK, OKT, 4, 18), text(444, 318, "바닥: 플랫폼이 책임지는 품질 하한", 30, OK, "middle", "bold")]
for i, s in enumerate(["서빙 계약", "재시도·과부하 차단", "배포·롤백 경로", "관측 규약"]):
    x = 20 + i * 214
    b += [rect(x, 352, 200, 80, OK, FILL, 3, 12), text(x + 100, 400, s, 21, TXT, "middle")]
b += [text(444, 520, "누가 어떤 모델을 만들어도 기본 품질은 같다", 25, TXT, "middle", "bold")]
figs["floor"] = svg(540, "\n".join(b))

# 맞물리는 플랫폼들
b = [rect(0, 0, 420, 110, WARN, WARNT, 4, 18), text(210, 66, "DeciML", 34, WARN, "middle", "bold"),
     rect(468, 0, 420, 110, OK, OKT, 4, 18), text(678, 66, "NeXA", 34, OK, "middle", "bold"),
     text(444, 148, "학습 · 서빙 → 결과를 넘긴다", 23, GRAY, "middle"),
     arrow(210, 120, 210, 190), arrow(678, 120, 678, 190),
     rect(0, 200, W, 140, INK, INKT, 4, 18), text(444, 254, "오케스트레이션 레이어", 30, INK, "middle", "bold"),
     text(444, 300, "A/B 테스트 · 결과 섞기 · 단계적 전환", 23, TXT, "middle"),
     arrow(444, 350, 444, 410),
     rect(244, 420, 400, 90, LINE, FILL, 3, 16), text(444, 476, "백엔드 서버 → 고객", 28, TXT, "middle", "bold"),
     rect(0, 560, 420, 100, LINE, SOFT, 0, 16), text(210, 604, "피처 스토어", 26, TXT, "middle", "bold"), text(210, 640, "피처를 실시간 관리", 21, GRAY, "middle"),
     rect(468, 560, 420, 100, LINE, SOFT, 0, 16), text(678, 604, "모델 레지스트리", 26, TXT, "middle", "bold"), text(678, 640, "등록 · 버전 · 모니터링", 21, GRAY, "middle")]
figs["ecosystem"] = svg(670, "\n".join(b))

if __name__ == "__main__":
    here = Path(__file__).parent
    for name, s in figs.items():
        (here / f"{name}.svg").write_text(s, encoding="utf-8")
    print(len(figs), "개:", ", ".join(figs))
