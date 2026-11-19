#!/usr/bin/env python3
"""'규칙은 코드로, 판단은 모델로' 회차 화면용 다이어그램을 SVG 로 그린다(원문 그림 없이 개념을 새로 그림).  python3 make.py"""
from html import escape
from pathlib import Path

INK, TXT, GRAY, LINE, FILL, SOFT = "#3F7A66", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF", "#ECECE8"
OK, OKT, WARN, WARNT, BAD, BADT = "#4E8F76", "#EAF3EE", "#C9963A", "#F8F0E0", "#C0605A", "#F6E7E5"
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


def chip(x, y, w, label, kind):
    """작은 꼬리표: 코드(좋음색)·결정(주의색)·모델(잉크)·없음."""
    c, t = {"code": (OK, OKT), "decide": (WARN, WARNT), "model": (BAD, BADT), "llm": (INK, "#E3EEEA")}[kind]
    return rect(x, y, w, 50, c, t, 3, 25) + text(x + w / 2, y + 34, label, 24, c, "middle", "bold")


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


figs = {}

# 시제품에서 생긴 버릇: 단계마다 LLM 이 붙는다
steps = ["입력 검사", "형식 바꾸기", "창구 고르기", "답장 쓰기"]
b = [text(0, 34, "시제품: 한 단계에 붙였더니 잘 돈다", 28, GRAY)]
for i, s in enumerate(steps):
    y = 70 + i * 130
    b += [rect(0, y, 380, 96, LINE, FILL, 3, 14), text(28, y + 60, s, 30, TXT, weight="bold"),
          arrow(400, y + 48, 470, y + 48, INK, 4), chip(490, y + 23, 160, "LLM 호출", "llm")]
    if i == 3:
        b.append(text(680, y + 58, "← 여기만 필요", 26, OK, weight="bold"))
    else:
        b.append(text(680, y + 58, "← 정말 필요?", 26, GRAY))
b.append(text(0, 620, "호출이 적을 땐 아무도 비용을 모른다", 28, INK, weight="bold"))
figs["creep"] = svg(640, "\n".join(b))

# 세 가지 값
items = [("돈", "값어치 낮은 단계도 요청 수만큼 과금", "요청 100만 건 × 단계 수"),
         ("시간", "호출 하나에 수백 밀리초, 사슬이면 누적", "300ms + 300ms + 300ms"),
         ("들쭉날쭉함", "같은 입력에 다른 답", "시험이 어렵고 감사가 느리다")]
b = []
for i, (h, s, ex) in enumerate(items):
    y = i * 196
    b += [rect(0, y, W, 170, BAD if i == 0 else LINE, FILL, 4 if i == 0 else 3, 16),
          text(28, y + 56, f"{i + 1}. {h}", 34, BAD if i == 0 else TXT, weight="bold"),
          text(28, y + 106, s, 26, TXT), text(28, y + 150, ex, 24, GRAY, mono=i == 1)]
figs["costs"] = svg(580, "\n".join(b))

# 모델 호출 세 번 → 한 번
rows = [("주문번호 형식 검사", "LLM", "정규식 한 줄", "code"),
        ("창구 고르기", "LLM", "키워드 → 결정 호출", "decide"),
        ("답장 쓰기", "LLM", "LLM", "llm")]
b = [text(170, 34, "보통 방식", 28, GRAY, "middle", "bold"), text(660, 34, "바꾼 방식", 28, INK, "middle", "bold")]
for i, (s, a, c, k) in enumerate(rows):
    y = 60 + i * 150
    b += [text(444, y + 30, s, 26, TXT, "middle", "bold"),
          chip(70, y + 52, 200, a, "llm"), arrow(300, y + 77, 420, y + 77, LINE, 3), chip(450, y + 52, 420, c, k)]
b += [rect(0, 520, 420, 90, INK, "#E3EEEA", 3, 14), text(210, 576, "한 건에 LLM 3번", 30, INK, "middle", "bold"),
      rect(468, 520, 420, 90, OK, OKT, 3, 14), text(678, 576, "대부분 LLM 1번", 30, OK, "middle", "bold")]
figs["calls"] = svg(620, "\n".join(b))

# 코드 vs 모델 비교표
rows = [("호출당 비용", "몇 자릿수 싸다", "토큰당 과금"),
        ("지연", "몇 ms 이하", "수백 ms"),
        ("규칙의 정확도", "적힌 그대로", "오류율 > 0"),
        ("감사", "저장소에 있다", "설명하기 어렵다"),
        ("시간이 지나면", "고치기 전까지 그대로", "버전 따라 바뀐다")]
b = [text(320, 40, "결정적 코드", 30, OK, "middle", "bold"), text(690, 40, "모델 호출", 30, BAD, "middle", "bold")]
for i, (k, c, m) in enumerate(rows):
    y = 70 + i * 104
    b += [rect(0, y, W, 88, LINE, FILL if i % 2 else SOFT, 0, 10), text(20, y + 56, k, 26, TXT, weight="bold"),
          text(320, y + 56, c, 26, OK, "middle"), text(690, y + 56, m, 26, BAD, "middle")]
figs["compare"] = svg(600, "\n".join(b))

# 온도 0이어도 같은 답을 보장하지 않는다
b = [text(0, 34, "같은 문의를 세 번 보낸다: \"카드가 두 번 긁혔어요\"", 26, GRAY),
     text(0, 100, "모델 (온도 0)", 30, BAD, weight="bold")]
for i, (ans, odd) in enumerate([("billing", False), ("billing", False), ("account", True)]):
    x = i * 296
    b += [rect(x, 124, 272, 90, BAD if odd else LINE, BADT if odd else FILL, 4 if odd else 3, 14),
          text(x + 136, 182, ans, 32, BAD if odd else TXT, "middle", "bold", mono=True)]
b += [text(0, 260, "덜 흔들릴 뿐, 똑같은 출력은 보장 못 한다", 26, BAD),
      text(0, 340, "규칙 (키워드 검사)", 30, OK, weight="bold")]
for i in range(3):
    x = i * 296
    b += [rect(x, 364, 272, 90, OK, OKT, 3, 14), text(x + 136, 422, "billing", 32, OK, "middle", "bold", mono=True)]
b += [text(0, 500, "언제나 같은 입력 → 같은 답", 26, OK),
      rect(0, 540, W, 110, LINE, SOFT, 0, 14),
      text(28, 584, "환각: 그럴듯하지만 틀린 답을 지어내는 것", 26, TXT, weight="bold"),
      text(28, 626, "규칙에는 들쭉날쭉함도, 환각도 없다", 26, GRAY)]
figs["temperature"] = svg(660, "\n".join(b))

# 보기에서 고르는 네 가지 방법
ways = [("작은 모델 + 구조화 출력", "답을 보기로 묶고 '모르겠음'을 둔다", "넘김 신호: 모델 스스로의 판단"),
        ("임베딩 유사도", "가장 가까운 정답 예시를 고른다", "넘김 신호: 유사도 점수"),
        ("Strands Decider", "실험 단계 오픈소스 결정 모델", "넘김 신호: 보정된 확신도"),
        ("직접 학습한 분류기", "라벨 데이터로 SageMaker에서 학습", "넘김 신호: 클래스별 확률")]
b = []
for i, (h, s, sig) in enumerate(ways):
    y = i * 168
    b += [rect(0, y, W, 148, LINE, FILL, 3, 16), text(28, y + 48, f"{i + 1}  {h}", 30, INK, weight="bold"),
          text(28, y + 92, s, 25, TXT), text(28, y + 130, sig, 23, GRAY)]
figs["four-ways"] = svg(660, "\n".join(b))

# 보정(calibration): 확신도 0.9 → 열에 아홉
b = [text(0, 34, "확신도 0.9라고 말한 답 열 개", 28, TXT, weight="bold")]
for i in range(10):
    x = i * 86
    ok = i < 9
    b += [rect(x, 60, 70, 70, OK if ok else BAD, OKT if ok else BADT, 3, 35),
          text(x + 35, 108, "✓" if ok else "✕", 34, OK if ok else BAD, "middle", "bold")]
b += [text(0, 180, "보정됐다 = 말한 확신도만큼 실제로 맞는다", 26, OK, weight="bold"),
      rect(0, 220, W, 150, WARN, WARNT, 3, 16),
      text(28, 270, "작은 모델이 고른 '모르겠음'", 28, WARN, weight="bold"),
      text(28, 318, "모델이 스스로 매긴 판단 — 보정된 점수가 아니다", 25, TXT),
      text(28, 352, "→ 라벨 데이터로 맞춰 본 뒤에 넘김 기준으로 쓴다", 23, GRAY),
      rect(0, 400, W, 150, LINE, FILL, 3, 16),
      text(28, 450, "Strands Decider README", 28, INK, weight="bold"),
      text(28, 498, "짧은 분류 과제, 확신도 0.9 이상 → 약 95% 정답", 25, TXT),
      text(28, 532, "실험 모델이니 내 데이터로 다시 확인", 23, GRAY),
      text(0, 600, "threshold는 내 라벨 데이터에서 정한다", 28, INK, weight="bold")]
figs["calibration"] = svg(620, "\n".join(b))

# 모델이 규칙을 한 번만 쓴다
b = [rect(0, 0, 250, 110, INK, "#E3EEEA", 3, 14), text(125, 48, "LLM", 30, INK, "middle", "bold"), text(125, 88, "정규식 초안 1번", 23, GRAY, "middle"),
     arrow(260, 55, 318, 55), rect(328, 0, 232, 110, WARN, WARNT, 3, 14), text(444, 48, "사람 검토", 30, WARN, "middle", "bold"),
     text(444, 88, "좋은/나쁜 입력으로 시험", 21, GRAY, "middle"),
     arrow(570, 55, 628, 55), rect(638, 0, 250, 110, OK, OKT, 3, 14), text(763, 48, "저장소에 커밋", 28, OK, "middle", "bold"),
     text(763, 88, "이후 매번 규칙 속도", 22, GRAY, "middle"),
     rect(0, 150, W, 92, LINE, SOFT, 0, 14), text(28, 207, r"TRACK = r'\b1Z[0-9A-Z]{16}\b'", 28, TXT, mono=True),
     text(0, 300, "피할 꼴: 반복을 겹친 정규식", 28, BAD, weight="bold"),
     rect(0, 324, W, 92, BAD, BADT, 3, 14), text(28, 381, "(a+)+$   ←  'aaaaaaaaaaaaaaaaaaaaaab'", 28, BAD, mono=True),
     text(0, 460, "어떤 입력에서는 검사가 한없이 느려진다 (ReDoS)", 25, TXT),
     text(0, 530, "설정 파일엔 정해진 부품만: 정규식·스키마·키워드·범위", 25, GRAY)]
figs["write-once"] = svg(550, "\n".join(b))

# 크기 맞추기: 품질 하한을 넘는 가장 작은 모델
models = [("아주 작은 모델", 0.62, 1), ("작은 모델", 0.86, 2), ("중간 모델", 0.89, 5), ("큰 모델", 0.90, 15), ("최신 최대 모델", 0.91, 40)]
base, top, floor = 560, 110, 0.85
b = []
sy = lambda q: base - (q - 0.5) / 0.5 * (base - top)
for i, (name, q, cost) in enumerate(models):
    x = 30 + i * 172
    pick = i == 1
    c = OK if pick else (LINE if q < floor else GRAY)
    b += [rect(x, sy(q), 130, base - sy(q), c, OKT if pick else (BADT if q < floor else SOFT), 4 if pick else 2, 8),
          text(x + 65, sy(q) - 14, f"{int(q * 100)}점", 24, c if q >= floor else BAD, "middle", "bold"),
          text(x + 65, base + 36, name, 20, TXT, "middle", "bold" if pick else "normal"),
          text(x + 65, base + 68, f"비용 ×{cost}", 20, GRAY, "middle")]
fy = sy(floor)
b += [f'<line x1="0" y1="{fy}" x2="{W}" y2="{fy}" stroke="{BAD}" stroke-width="3" stroke-dasharray="12 8"/>',
      f'<line x1="0" y1="18" x2="60" y2="18" stroke="{BAD}" stroke-width="3" stroke-dasharray="12 8"/>', text(76, 26, "품질 하한 85점 (골든 평가 세트로 잰다)", 24, BAD, weight="bold"),
      text(0, 690, "하한을 넘는 것 중 가장 싼 모델을 고른다", 28, OK, weight="bold"),
      text(W, 690, "점수·비용은 설명용 가상 값", 20, GRAY, "end")]
figs["rightsize"] = svg(710, "\n".join(b))

# 골든 평가 세트
rows = [("\"카드가 두 번 긁혔어요\"", "billing"), ("\"앱이 계속 꺼져요\"", "technical"), ("\"이메일을 바꾸고 싶어요\"", "account"),
        ("\"배송은 언제 오나요\"", "other")]
b = [text(0, 34, "골든 평가 세트 = 정답이 붙은 내 과제 예시", 28, TXT, weight="bold"),
     text(30, 92, "입력", 24, GRAY, weight="bold"), text(700, 92, "정답", 24, GRAY, "middle", "bold")]
for i, (q, a) in enumerate(rows):
    y = 112 + i * 84
    b += [rect(0, y, W, 70, LINE, FILL if i % 2 else SOFT, 0, 10), text(30, y + 46, q, 25, TXT), text(700, y + 46, a, 25, INK, "middle", "bold", mono=True)]
b += [rect(0, 470, 420, 140, LINE, FILL, 3, 16), text(210, 520, "벤치마크", 28, GRAY, "middle", "bold"),
      text(210, 566, "넓은 과제 수천 개", 24, GRAY, "middle"),
      rect(468, 470, 420, 140, INK, "#E3EEEA", 4, 16), text(678, 520, "골든 평가 세트", 28, INK, "middle", "bold"),
      text(678, 566, "내 과제 하나, 하한 하나", 24, INK, "middle")]
figs["golden"] = svg(620, "\n".join(b))

# 그림자 모드: 규칙이 처리한 요청 일부를 모델에도 흘려 비교
b = [rect(0, 0, 230, 100, LINE, FILL, 3, 14), text(115, 60, "요청", 30, TXT, "middle", "bold"),
     arrow(240, 50, 330, 50), rect(340, 0, 300, 100, OK, OKT, 3, 14), text(490, 46, "규칙 (키워드)", 28, OK, "middle", "bold"),
     text(490, 82, "답을 실제로 쓴다", 22, GRAY, "middle"),
     arrow(650, 50, 740, 50), rect(750, 0, 138, 100, OK, FILL, 3, 14), text(819, 60, "응답", 28, OK, "middle", "bold"),
     f'<path d="M115 110 L115 260 L330 260" fill="none" stroke="{GRAY}" stroke-width="3" stroke-dasharray="10 8" marker-end="url(#a)"/>',
     text(130, 200, "일부만 몰래", 22, GRAY),
     rect(340, 210, 300, 100, INK, "#E3EEEA", 3, 14, "10 6"), text(490, 256, "모델 (그림자)", 28, INK, "middle", "bold"),
     text(490, 292, "답은 쓰지 않고 비교만", 22, GRAY, "middle"),
     arrow(490, 120, 490, 200, GRAY, 3),
     text(0, 380, "고객이 쓰는 말이 바뀐다", 28, TXT, weight="bold")]
for i, (msg, r, m) in enumerate([("\"환불해 주세요\"", "billing", "billing"), ("\"돈 돌려받고 싶어요\"", "other", "billing"),
                                 ("\"결제 취소 부탁해요\"", "other", "billing")]):
    y = 410 + i * 84
    diff = r != m
    b += [rect(0, y, W, 70, BAD if diff else LINE, BADT if diff else FILL, 3 if diff else 2, 10),
          text(24, y + 46, msg, 24, TXT), text(560, y + 46, f"규칙 {r}", 22, OK, "middle", mono=True),
          text(760, y + 46, f"모델 {m}", 22, INK, "middle", mono=True)]
b.append(text(0, 690, "답이 갈리기 시작하면 → 그 단계를 다시 분류한다", 26, BAD, weight="bold"))
figs["shadow"] = svg(710, "\n".join(b))

if __name__ == "__main__":
    here = Path(__file__).parent
    for name, s in figs.items():
        (here / f"{name}.svg").write_text(s, encoding="utf-8")
    print(len(figs), "개:", ", ".join(figs))
