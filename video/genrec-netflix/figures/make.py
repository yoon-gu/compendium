#!/usr/bin/env python3
"""GenRec 화면용 다이어그램을 SVG 로 그린다(논문 그림을 베끼지 않고 구조·수치만 가져와 새로 그림).  python3 make.py"""
from pathlib import Path

INK, TXT, GRAY, LINE, FILL = "#8A1C2B", "#141414", "#6B6B68", "#B9B9B4", "#FFFFFF"
F = 'font-family="NanumGothic, Nanum Gothic, sans-serif"'
W = 888


def text(x, y, s, size=30, color=TXT, anchor="start", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" {F}>{s}</text>'


def box(x, y, w, h, title, lines=(), accent=False):
    stroke = INK if accent else LINE
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{FILL}" stroke="{stroke}" stroke-width="{4 if accent else 3}"/>',
           text(x + 28, y + 58, title, 38, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 28, y + 112 + i * 50, ln, 30, GRAY))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label=""):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>']
    if label:
        out.append(text((x1 + x2) / 2 + 16, (y1 + y2) / 2 + 10, label, 26, GRAY))
    return "\n".join(out)


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>{body}</svg>')


def stack(items, gap=52, top=0):
    """세로로 쌓은 상자들 + 사이 화살표. items: (title, lines, accent)"""
    y, out = top, []
    for i, (t, ls, acc) in enumerate(items):
        h = 92 + 50 * len(ls) + (18 if ls else 0)
        out.append(box(0, y, W, h, t, ls, acc))
        y += h
        if i < len(items) - 1:
            out.append(arrow(W / 2, y + 4, W / 2, y + gap - 4)); y += gap
    return y, "\n".join(out)


figs = {}

# 1. 추론 파이프라인
h, b = stack([("원시 로그", ["시청·재생 시간·좋아요·찜, 기기·화면·지역·시간, 작품 메타데이터"], False),
              ("언어화 (verbalization)", ["강한 신호만 남기고, 반복은 압축해 자연어 프롬프트로"], False),
              ("LLM 백본 · 프리필 1회", ["디코더 전용 트랜스포머가 프롬프트를 한 번 읽는다"], True),
              ("카탈로그 인식 랭킹 헤드 → 개인화 순위", ["카탈로그 전체에 점수 → 소프트맥스 → 순위. 여러 화면이 재사용"], True)])
figs["pipeline"] = svg(h, b)

# 2. 두 단계 학습
h, b = stack([("Phase 1 · 기반 LLM", ["오픈소스 LLM + 넷플릭스 카탈로그·회원 행동 데이터", "세계 지식·개인화·콘텐츠 이해·언어 능력의 균형",
                                       "갱신: 드물게 / 서빙 비용 제약: 적음"], False),
              ("Phase 2 · GenRec (사후 학습)", ["랭킹용 데이터 + 라벨 + 보상 신호", "랭킹 품질과 추천 조정에 집중",
                                              "갱신: 자주(신작·인기 변화·최근 관심) / 비용 효율 필수"], True)], gap=64)
figs["two-phase"] = svg(h, b)

# 3. 랭킹 헤드
b = [box(0, 0, 520, 150, "x = V(H, {Mᵢ}, τ)", ["이력·작품 메타데이터·맥락을 문장으로"]),
     arrow(260, 154, 260, 210),
     box(0, 214, 520, 150, "LLM → h (d차원)", ["풀링 위치의 은닉 상태 = 취향·맥락 요약"], True),
     text(600, 40, "작품 임베딩", 28, GRAY),
     ]
for i, lab in enumerate(["e₁", "e₂", "e₃", "⋮", "e_N"]):
    y = 70 + i * 54
    b.append(f'<rect x="600" y="{y}" width="200" height="44" rx="10" fill="{FILL}" stroke="{LINE}" stroke-width="3"/>')
    b.append(text(700, y + 32, lab, 28, TXT, "middle"))
b += [arrow(524, 289, 596, 289),
      box(0, 420, W, 150, "sᵢ = φ(h, eᵢ) → softmax → 순위 π", ["LLM·φ·{eᵢ} 를 함께 학습 · 출력 공간이 카탈로그 = 없는 작품은 못 나온다"], True)]
figs["head"] = svg(580, "\n".join(b))

# 4. 컨텍스트 압축
b = [text(0, 36, "컨텍스트 길이 (토큰)", 28, GRAY),
     f'<rect x="0" y="56" width="{W}" height="64" rx="10" fill="{LINE}"/>', text(20, 100, "원래  약 5,000", 30, FILL, weight="bold"),
     f'<rect x="0" y="150" width="{int(W * 1700 / 5000)}" height="64" rx="10" fill="{INK}"/>', text(20, 194, "압축 후  약 1,700", 30, FILL, weight="bold"),
     text(int(W * 1700 / 5000) + 20, 194, "≈ 1/3 · 오프라인 MRR 손실 무시할 수준", 27, GRAY),
     text(0, 270, "GenRec 은 연산이 병목 → 서빙 비용도 약 1/3", 30, TXT)]
figs["context"] = svg(290, "\n".join(b))

# 5. Phase 1·2 효과 (MRR 상대 개선)
b = [text(0, 36, "오프라인 랭킹 지표(MRR) 상대 개선", 28, GRAY)]
rows = [("Phase 1  (기성 LLM 백본 대비)", 10, 20, "+10-20%"),
        ("Phase 2  (갓 학습한 Phase 1 대비)", 35, 50, "+35-50%"),
        ("Phase 2, 2주 뒤", 78, 82, "≈ +80%")]
for i, (lab, lo, hi, s) in enumerate(rows):
    y = 70 + i * 120
    b.append(text(0, y + 30, lab, 28, TXT))
    b.append(f'<rect x="0" y="{y + 46}" width="{W}" height="40" rx="8" fill="#ECECE8"/>')
    b.append(f'<rect x="0" y="{y + 46}" width="{int(W * lo / 100)}" height="40" rx="8" fill="{INK}"/>')
    b.append(f'<rect x="{int(W * lo / 100)}" y="{y + 46}" width="{int(W * (hi - lo) / 100)}" height="40" fill="{INK}" opacity="0.45"/>')
    b.append(text(int(W * hi / 100) + 16, y + 76, s, 28, INK, weight="bold"))
figs["phase-impact"] = svg(420, "\n".join(b))

# 6. 스케일링 개형
import math
b = [text(0, 36, "Phase-2 데이터 스케일링 (개형 — 논문의 정성적 결과, 실제 수치 아님)", 26, GRAY),
     f'<line x1="60" y1="420" x2="{W}" y2="420" stroke="{LINE}" stroke-width="3"/>', f'<line x1="60" y1="60" x2="60" y2="420" stroke="{LINE}" stroke-width="3"/>',
     text(W / 2 + 30, 462, "Phase-2 학습 데이터 (1x → 20x)", 27, GRAY, "middle"), text(14, 70, "MRR", 27, GRAY)]
for k, (base, lab) in enumerate([(0.52, "~1B"), (0.74, "~10B")]):
    pts = " ".join(f"{60 + i * (W - 70) / 20:.0f},{420 - (base + 0.22 * math.log1p(i) / math.log1p(20)) * 330:.0f}" for i in range(21))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="{3 + 3 * k}" opacity="{0.55 + 0.45 * k}"/>')
    b.append(text(W - 4, 420 - (base + 0.22) * 330 - 12, lab, 28, INK, "end", "bold"))
figs["scaling"] = svg(480, "\n".join(b))

# 7. 언어화 예시 (지어낸 예시)
b = [text(0, 36, "원시 로그 (예시)", 28, GRAY)]
for i, ln in enumerate(["10/05  재생  〈드라마 A〉 1-8화 전부, 각 40분+", "10/06  좋아요  〈영화 B〉", "10/07  재생  〈영화 C〉 4분 후 중단", "10/07  클릭  〈예고편 D〉 (조회만)"]):
    y = 60 + i * 50
    b.append(f'<rect x="0" y="{y}" width="{W}" height="42" rx="8" fill="{FILL}" stroke="{LINE}" stroke-width="2"/>')
    b.append(text(16, y + 30, ln, 26, GRAY if i >= 2 else TXT))
b += [arrow(W / 2, 268, W / 2, 316, "언어화"),
      f'<rect x="0" y="322" width="{W}" height="150" rx="14" fill="{FILL}" stroke="{INK}" stroke-width="4"/>',
      text(24, 372, "“지난주 〈드라마 A〉 시즌 전체를 정주행했고,", 30, TXT),
      text(24, 416, "〈영화 B〉에 좋아요를 눌렀다.”", 30, TXT),
      text(24, 456, "짧게 보다 만 C 와 조회만 한 D 는 뺀다 · 8편 → ‘정주행’ 하나로 압축", 25, GRAY)]
figs["verbalize"] = svg(490, "\n".join(b))

# 8. 자기회귀 vs 프리필 전용
b = [text(0, 36, "자기회귀 디코딩", 30, TXT, weight="bold"), text(300, 36, "토큰을 하나씩 생성 — 순전파 N번, 빔 서치까지 겹치면 더", 26, GRAY)]
for i in range(6):
    x = i * 150
    b.append(f'<rect x="{x}" y="56" width="120" height="56" rx="10" fill="{FILL}" stroke="{LINE}" stroke-width="3"/>')
    b.append(text(x + 60, 94, "토큰" if i < 5 else "…", 26, GRAY, "middle"))
    if i < 5: b.append(arrow(x + 124, 84, x + 146, 84))
b += [text(0, 190, "프리필 전용 (GenRec)", 30, INK, weight="bold"), text(360, 190, "입력을 한 번 읽고 카탈로그 전체 점수를 한 번에", 26, GRAY),
      box(0, 210, 380, 150, "프롬프트 1회 읽기", ["시청 기록 + 맥락"]),
      arrow(384, 285, 500, 285, "순전파 1번"),
      box(504, 210, 384, 150, "전체 점수", ["수천 개 작품 동시에"], True)]
figs["prefill"] = svg(380, "\n".join(b))

# 9. A/B 테스트 타일
b = []
tiles = [("약 10%", "넷플릭스 트래픽"), ("4주", "배치 연산 화면"), ("+0.006%", "핵심 온라인 지표 (상대)"), ("단기·장기", "모두 통계적으로 유의미")]
for i, (big, small) in enumerate(tiles):
    x, y = (i % 2) * (W / 2 + 12), (i // 2) * 180
    b.append(f'<rect x="{x}" y="{y}" width="{W / 2 - 12}" height="160" rx="14" fill="{FILL}" stroke="{INK if i == 2 else LINE}" stroke-width="3"/>')
    b.append(text(x + 24, y + 80, big, 56, INK, weight="bold"))
    b.append(text(x + 24, y + 128, small, 26, GRAY))
figs["abtest"] = svg(350, "\n".join(b))

# 10. 보상 가중 랭킹 손실
h, b = stack([("학습 예시 하나 (회원의 실제 참여)", ["예: 오래 본 재생, 좋아요, 짧게 보다 만 재생"], False),
              ("보상 모델들 → 가중치 w", ["장기 만족 대리 지표: 재방문·넓은 탐색·지속 참여 ↑",
                                      "행동 재조정: 영화·게임·라이브·팟캐스트, 공개 단계 간 균형"], True),
              ("w × 랭킹 손실", ["가치 높은 참여는 크게, 나쁜 행동은 작게 반영", "RL(GRPO)보다 단순하고 싸다"], False)])
figs["reward"] = svg(h, b)

# ---------- 용어 그림: 처음 듣는 말을 그림 한 장으로 ----------
def term(title, caption):
    """용어 카드 머리글과 아래 설명 한 줄."""
    return text(0, 40, title, 36, INK, weight="bold"), text(0, 0, caption, 28, GRAY)

# 11. 루브 골드버그 장치: 구슬 하나가 경사로·톱니·지렛대를 지나 종을 친다
b = [text(0, 40, "루브 골드버그 장치", 36, INK, weight="bold"), text(360, 40, "일부러 복잡하게 만든 연쇄 기계", 26, GRAY),
     f'<circle cx="60" cy="90" r="16" fill="{INK}"/>', text(84, 80, "구슬(영화·드라마)", 24, GRAY),
     f'<line x1="40" y1="110" x2="300" y2="190" stroke="{TXT}" stroke-width="5"/>',           # 경사로
     f'<circle cx="340" cy="230" r="42" fill="none" stroke="{TXT}" stroke-width="5"/>',          # 톱니
     f'<circle cx="340" cy="230" r="14" fill="{TXT}"/>']
for k in range(8):
    import math as _m
    a = k * _m.pi / 4; b.append(f'<line x1="{340 + 42 * _m.cos(a):.0f}" y1="{230 + 42 * _m.sin(a):.0f}" x2="{340 + 56 * _m.cos(a):.0f}" y2="{230 + 56 * _m.sin(a):.0f}" stroke="{TXT}" stroke-width="5"/>')
b += [f'<line x1="400" y1="300" x2="640" y2="260" stroke="{TXT}" stroke-width="5"/>', f'<polygon points="520,282 505,310 535,310" fill="{TXT}"/>',   # 지렛대
      f'<line x1="640" y1="260" x2="640" y2="150" stroke="{TXT}" stroke-width="4" stroke-dasharray="8 8"/>',
      f'<path d="M700 120 q40 -40 80 0 v70 h-80z" fill="none" stroke="{INK}" stroke-width="5"/>', f'<circle cx="740" cy="196" r="8" fill="{INK}"/>',  # 종
      text(700, 230, "땡!", 30, INK, weight="bold"),
      text(0, 360, "구슬 전용으로 정밀하게 짜인 장치라서", 27, TXT),
      text(0, 398, "탁구공(게임·라이브·팟캐스트)이 오면", 27, TXT),
      text(0, 436, "경사로와 톱니를 전부 다시 깎아야 한다 = 기존 추천 시스템", 27, INK)]
figs["t-goldberg"] = svg(460, "\n".join(b))

# 12. 피처(feature): 사람이 정의한 숫자 특징
b = [text(0, 40, "피처 (feature)", 36, INK, weight="bold"), text(300, 40, "모델에 넣으려고 사람이 미리 정의한 숫자 특징", 28, GRAY)]
cells = ["액션 클릭 3회", "평균 시청 42분", "마지막 접속 2일 전", "주말 시청 비율 0.7", "…수천 개"]
for i, c in enumerate(cells):
    x = i * 178
    b.append(f'<rect x="{x}" y="76" width="168" height="100" rx="10" fill="{FILL}" stroke="{LINE if i < 4 else INK}" stroke-width="3"/>')
    b.append(text(x + 84, 134, c, 25, TXT if i < 4 else INK, "middle"))
b += [arrow(W / 2, 186, W / 2, 246), box(0, 252, W, 150, "기존 랭커: 피처 수천 개를 조합해 점수", ["새 콘텐츠 유형마다 피처를 새로 정의·검증해야 한다"]),
      text(0, 460, "GenRec: 피처 대신 시청 기록을 문장으로 그대로 넣는다", 28, INK)]
figs["t-feature"] = svg(480, "\n".join(b))

# 13. 토큰과 토큰 예산
b = [text(0, 40, "토큰 (token) · 토큰 예산", 36, INK, weight="bold"), text(0, 78, "LLM이 글을 읽는 최소 단위 · 한 번에 읽을 수 있는 양의 한도", 26, GRAY)]
toks = ["지난주", "〈드라마 A〉", "를", "정주행", "했고", "…"]
x = 0
for t in toks:
    w = 40 + 26 * len(t)
    b.append(f'<rect x="{x}" y="100" width="{w}" height="56" rx="8" fill="{FILL}" stroke="{LINE}" stroke-width="3"/>'); b.append(text(x + w / 2, 138, t, 26, TXT, "middle")); x += w + 10
b += [text(0, 204, "토큰 예산", 28, TXT), f'<rect x="0" y="220" width="{W}" height="44" rx="8" fill="#ECECE8"/>',
      f'<rect x="0" y="220" width="{int(W * 0.34)}" height="44" rx="8" fill="{INK}"/>', text(16, 250, "꼭 필요한 기록", 24, FILL, weight="bold"),
      text(int(W * 0.34) + 16, 250, "넘치면 비용↑, 어텐션 희석 → 하이라이트만 남긴다", 24, GRAY)]
figs["t-token"] = svg(284, "\n".join(b))

# 14. 환각(hallucination)
b = [text(0, 40, "환각 (hallucination)", 36, INK, weight="bold"), text(0, 78, "그럴듯하지만 사실이 아닌 것을 모델이 지어내는 현상", 26, GRAY),
     box(0, 100, 420, 260, "카탈로그 (실제 목록)", ["〈드라마 A〉", "〈영화 B〉", "〈영화 C〉"]),
     box(468, 100, 420, 260, "자유 생성 LLM", ["〈드라마 A〉", "〈영화 B〉", "〈심야 식당 3〉  ✗ 없는 작품"], True),
     f'<line x1="494" y1="302" x2="704" y2="302" stroke="{INK}" stroke-width="5"/>',
     text(0, 416, "출력을 카탈로그 안의 점수로 제한 → 없는 작품은 나올 수 없다", 27, TXT)]
figs["t-halluc"] = svg(440, "\n".join(b))

# 15. 강화학습 vs 보상 가중
b = [text(0, 40, "강화학습(RL) vs 보상 가중", 36, INK, weight="bold"),
     box(0, 70, 420, 260, "강화학습", ["추천 → 보상 → 갱신을", "수없이 반복 (예: GRPO)", "효과 컸지만 비용이 크다"]),
     box(468, 70, 420, 260, "보상 가중 손실 (채택)", ["예시마다 보상으로 w 결정", "손실에 w를 곱하기만", "단순·안정·저비용"], True),
     f'<path d="M60 350 q150 -60 300 0" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>', f'<path d="M360 370 q-150 60 -300 0" fill="none" stroke="{INK}" stroke-width="4" marker-end="url(#a)"/>',
     text(210, 366, "반복 루프", 24, GRAY, "middle")]
figs["t-rl"] = svg(440, "\n".join(b))

# 16. MLP 인프라 vs LLM 인프라
b = [text(0, 40, "MLP (다층 퍼셉트론) 와 LLM 인프라", 36, INK, weight="bold")]
for li, n in enumerate([3, 4, 2]):
    for k in range(n):
        cx, cy = 60 + li * 120, 110 + k * 50 + (4 - n) * 25
        b.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="{FILL}" stroke="{TXT}" stroke-width="3"/>')
        if li < 2:
            for j in range([3, 4, 2][li + 1]):
                b.append(f'<line x1="{cx + 14}" y1="{cy}" x2="{60 + (li + 1) * 120 - 14}" y2="{110 + j * 50 + (4 - [3, 4, 2][li + 1]) * 25}" stroke="{LINE}" stroke-width="2"/>')
b += [text(0, 330, "고전 추천: 작은 신경망·행렬 분해", 26, TXT), text(0, 364, "CPU 로도 충분, 입력은 숫자 피처", 24, GRAY),
      box(468, 70, 420, 260, "LLM 인프라", ["수십억 파라미터 트랜스포머", "GPU + vLLM 서빙", "KV 캐시·프리픽스 캐시·프리필 전용"], True),
      text(468, 370, "입력은 긴 문장(수천 토큰) → 서빙 효율이 설계의 중심", 24, GRAY)]
figs["t-infra"] = svg(400, "\n".join(b))

# 17. A/B 테스트
b = [text(0, 40, "A/B 테스트", 36, INK, weight="bold"), text(230, 40, "실제 사용자를 둘로 나눠 두 버전을 같은 기간 동안 비교", 28, GRAY),
     box(0, 70, 300, 150, "전체 회원", ["같은 기간, 같은 화면"]),
     arrow(304, 118, 460, 118), arrow(304, 170, 460, 250), text(330, 104, "약 90%", 24, GRAY), text(300, 262, "약 10%", 24, INK),
     box(468, 70, 420, 96, "A · 기존 프로덕션 랭커", []), box(468, 200, 420, 96, "B · GenRec", [], True),
     text(0, 350, "4주 뒤 단기·장기 지표를 비교 → 차이가 우연이 아닌지 통계적으로 검정", 27, TXT)]
figs["t-abtest"] = svg(370, "\n".join(b))

# ---------- 진행자의 비유·예시 그림 ----------
# 18. 스프레드시트 추천 (0:17)
b = [text(0, 40, "기존 추천 = 거대한 스프레드시트", 36, INK, weight="bold")]
hdr = ["회원", "액션 클릭", "로맨스 클릭", "평균 시청", "→ 추천"]
rows = [["A", "3", "0", "42분", "액션 영화"], ["B", "0", "5", "18분", "로맨스 영화"], ["C", "1", "1", "7분", "인기작"]]
cw = [100, 170, 190, 170, 258]
for r, row in enumerate([hdr] + rows):
    x = 0
    for c, val in enumerate(row):
        fill = "#ECECE8" if r == 0 else FILL
        b.append(f'<rect x="{x}" y="{70 + r * 58}" width="{cw[c]}" height="56" fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
        b.append(text(x + cw[c] / 2, 70 + r * 58 + 38, val, 26, INK if (c == 4 and r > 0) else TXT, "middle", "bold" if r == 0 else "normal"))
        x += cw[c]
b.append(text(0, 350, "규칙: 액션을 3번 클릭했으니 액션 영화 — 차갑고 기계적인 공식", 27, GRAY))
figs["ex-spreadsheet"] = svg(370, "\n".join(b))

# 19. MRR 예시 (5:07)
b = [text(0, 40, "MRR: 보고 싶은 작품이 얼마나 앞에 뜨는가", 36, INK, weight="bold")]
for col, (lab, want, score) in enumerate([("추천 목록 ①", 1, "1/1 = 1.0"), ("추천 목록 ②", 5, "1/5 = 0.2")]):
    x0 = col * 460
    b.append(text(x0, 86, lab, 28, TXT, weight="bold"))
    for i in range(5):
        y = 104 + i * 54
        hit = (i + 1 == want)
        b.append(f'<rect x="{x0}" y="{y}" width="420" height="46" rx="8" fill="{INK if hit else FILL}" stroke="{INK if hit else LINE}" stroke-width="2"/>')
        b.append(text(x0 + 16, y + 31, f"{i + 1}위  " + ("내가 보고 싶던 작품 ★" if hit else "다른 작품"), 25, FILL if hit else GRAY))
    b.append(text(x0, 408, f"역순위 = {score}", 28, INK, weight="bold"))
b.append(text(0, 458, "여러 요청의 역순위를 평균 → MRR. 1에 가까울수록 좋다", 27, GRAY))
figs["ex-mrr"] = svg(480, "\n".join(b))

# 20. 모기 잡는 데 대포 (6:05) — CC0 아이콘(위키미디어 공용)을 안에 심는다
def icon(name, x, y, w, h, color):
    """figures/<name>.svg 를 중첩 <svg> 로 넣는다(<img> 로 읽는 SVG 는 외부 파일 참조가 막히므로 인라인)."""
    import re as _re
    raw = Path(__file__).with_name(f"{name}.svg").read_text(encoding="utf-8")
    vb = _re.search(r'viewBox="([^"]+)"', raw)[1]
    inner = raw[raw.index(">", raw.index("<svg")) + 1:raw.rindex("</svg>")].replace("#000000", color).replace("#000", color)
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" fill="{color}">{inner}</svg>'

b = [text(0, 40, "모기 잡는 데 대포를 쏜다?", 36, INK, weight="bold"),
     icon("icon-cannon", 20, 90, 320, 320, TXT),
     f'<path d="M330 150 q180 -120 380 40" fill="none" stroke="{LINE}" stroke-width="4" stroke-dasharray="12 10"/>',
     icon("icon-mosquito", 700, 150, 90, 108, INK),
     text(40, 450, "거대 LLM = 대포", 30, TXT, weight="bold"), text(40, 484, "수억 명에게 매초 쏜다면 비용 폭탄", 25, GRAY),
     text(600, 300, "영화 순위 몇 개 = 모기", 28, INK, weight="bold"),
     text(0, 540, "아이콘: viglino, Marco Hernandez (CC0, Wikimedia Commons)", 22, GRAY)]
figs["ex-cannon"] = svg(560, "\n".join(b))

# 21. 기초공사 vs 인테리어 (6:46)
b = [text(0, 40, "기초공사와 인테리어 공사를 분리", 36, INK, weight="bold"),
     f'<rect x="60" y="300" width="760" height="70" fill="{TXT}"/>', text(440, 345, "기초 = Phase 1 기반 LLM · 가끔 갱신", 28, FILL, "middle", "bold"),
     f'<rect x="100" y="150" width="680" height="150" fill="{FILL}" stroke="{TXT}" stroke-width="4"/>',
     f'<polygon points="80,150 440,70 800,150" fill="none" stroke="{TXT}" stroke-width="4"/>',
     text(440, 215, "인테리어 = Phase 2 랭커", 30, INK, "middle", "bold"), text(440, 258, "신작·최신 시청 반영 · 자주 갱신", 26, GRAY, "middle"),
     text(0, 420, "무거운 공사는 드물게, 가벼운 공사는 자주 — 지능은 그대로, 운영은 가볍게", 27, TXT)]
figs["ex-house"] = svg(440, "\n".join(b))

# 22. 휴가 이야기 (9:01)
b = [text(0, 40, "친구에게 휴가 이야기를 할 때", 36, INK, weight="bold"),
     box(0, 70, 420, 310, "자잘한 기록 전부", ["3시 2분 기상", "3시 10분 화장실", "3시 15분 물 마심", "… (친구가 도망간다)"]),
     box(468, 70, 420, 310, "하이라이트만", ["비행기 연착, 최악", "도착해서 먹은 저녁은", "정말 환상적!"], True),
     text(0, 436, "넷플릭스도 같다: 5분 보다 만 영화·잡음 클릭은 버리고", 27, TXT),
     text(0, 474, "끝까지 본 드라마·좋아요만 문장으로 남긴다", 27, TXT)]
figs["ex-vacation"] = svg(500, "\n".join(b))

# 23. 객관식 (11:20)
b = [text(0, 40, "객관식처럼 보기 안에서만 고르게", 36, INK, weight="bold"),
     f'<rect x="0" y="70" width="{W}" height="320" rx="14" fill="{FILL}" stroke="{LINE}" stroke-width="3"/>',
     text(24, 114, "문제: 이 회원에게 다음으로 보여 줄 작품은?", 28, TXT, weight="bold")]
for i, (t, pick) in enumerate([("① 〈드라마 A〉", False), ("② 〈영화 B〉", True), ("③ 〈영화 C〉", False), ("④ 〈다큐 D〉", False)]):
    y = 160 + i * 54
    b.append(f'<circle cx="44" cy="{y}" r="14" fill="{INK if pick else "none"}" stroke="{INK if pick else LINE}" stroke-width="3"/>')
    b.append(text(72, y + 9, t + ("   ← 카탈로그 안에서 점수가 가장 높은 작품" if pick else ""), 26, INK if pick else TXT))
b.append(text(0, 430, "주관식(자유 생성)이 아니라서 보기에 없는 작품은 답이 될 수 없다", 27, GRAY))
figs["ex-choice"] = svg(450, "\n".join(b))

# 24. 똑똑한 학생 (16:54)
b = [text(0, 40, "A부터 Z까지 떠먹이지 않아도 된다", 36, INK, weight="bold"),
     box(0, 70, 420, 260, "백지 학생 (기존 랭커)", ["\"이건 액션, 저건 코미디\"", "수많은 라벨로 일일이", "처음부터 가르쳐야 한다"]),
     box(468, 70, 420, 260, "똑똑한 학생 (Phase 1)", ["언어·문맥·넷플릭스를", "이미 안다", "→ 40배 적은 라벨로 충분"], True),
     text(0, 386, "하나를 가르치면 열을 아는 기반 모델 덕에 Phase 2 가 가볍다", 27, TXT)]
figs["ex-student"] = svg(410, "\n".join(b))

# 25. 발자국 → 이야기 (19:13)
b = [text(0, 40, "디지털 발자국이 하나의 이야기가 된다", 36, INK, weight="bold")]
steps = ["주말 드라마 정주행", "지루해서 끈 다큐", "좋아요 누른 영화", "새벽에 본 예고편"]
for i, t in enumerate(steps):
    x, y = 30 + i * 215, 110 + (i % 2) * 40
    b.append(f'<ellipse cx="{x + 20}" cy="{y}" rx="16" ry="24" fill="{LINE}"/>'); b.append(f'<ellipse cx="{x + 20}" cy="{y - 30}" rx="7" ry="9" fill="{LINE}"/>')
    b.append(text(x + 50, y + 8, t, 24, GRAY))
b += [arrow(W / 2, 200, W / 2, 250),
      f'<rect x="0" y="256" width="{W}" height="120" rx="14" fill="{FILL}" stroke="{INK}" stroke-width="4"/>',
      text(24, 304, "\"주말엔 몰아보고, 다큐는 금방 질려 하지만,", 28, TXT), text(24, 346, "좋아요 누른 영화 같은 작품을 새벽에 찾는 사람\"", 28, TXT),
      text(0, 420, "변수의 묶음이 아니라 한 사람의 서사로 읽는다 — 다음 클릭이 아니라 장기 만족을 위해", 26, GRAY)]
figs["ex-footprints"] = svg(440, "\n".join(b))

# 스케일링 그래프에 '기존 모델의 유리 천장' 곡선 추가
_old = figs["scaling"]
ceiling = (f'<line x1="60" y1="250" x2="{W}" y2="250" stroke="{GRAY}" stroke-width="3" stroke-dasharray="12 8"/>'
           + text(70, 240, "유리 천장", 24, GRAY)
           + f'<polyline points="' + " ".join(f"{60 + i * (W - 70) / 20:.0f},{420 - (0.30 + 0.18 * (1 - 2.718 ** (-i / 4))) * 330:.0f}" for i in range(21)) + f'" fill="none" stroke="{GRAY}" stroke-width="4"/>'
           + text(W - 4, 420 - 0.48 * 330 + 36, "기존 추천 모델 (정체)", 24, GRAY, "end"))
figs["scaling"] = _old.replace("</svg>", ceiling + "</svg>")

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
