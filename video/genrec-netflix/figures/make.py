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
           text(x + 24, y + 50, title, 38, INK if accent else TXT, weight="bold")]
    for i, ln in enumerate(lines):
        out.append(text(x + 24, y + 96 + i * 40, ln, 30, GRAY))
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


def stack(items, gap=36, top=0):
    """세로로 쌓은 상자들 + 사이 화살표. items: (title, lines, accent)"""
    y, out = top, []
    for i, (t, ls, acc) in enumerate(items):
        h = 74 + 40 * len(ls) + (12 if ls else 0)
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
                                              "갱신: 자주(신작·인기 변화·최근 관심) / 비용 효율 필수"], True)], gap=56)
figs["two-phase"] = svg(h, b)

# 3. 랭킹 헤드
b = [box(0, 0, 520, 110, "x = V(H, {Mᵢ}, τ)", ["이력·작품 메타데이터·맥락을 문장으로"]),
     arrow(260, 114, 260, 170),
     box(0, 174, 520, 110, "LLM → h (d차원)", ["풀링 위치의 은닉 상태 = 취향·맥락 요약"], True),
     text(600, 40, "작품 임베딩", 28, GRAY),
     ]
for i, lab in enumerate(["e₁", "e₂", "e₃", "⋮", "e_N"]):
    y = 70 + i * 54
    b.append(f'<rect x="600" y="{y}" width="200" height="44" rx="10" fill="{FILL}" stroke="{LINE}" stroke-width="3"/>')
    b.append(text(700, y + 32, lab, 28, TXT, "middle"))
b += [arrow(524, 229, 596, 229),
      box(0, 340, W, 110, "sᵢ = φ(h, eᵢ)  →  softmax over catalog  →  순위 π", ["LLM·φ·{eᵢ} 를 함께 학습. 출력 공간이 카탈로그라 없는 작품은 못 나온다"], True)]
figs["head"] = svg(460, "\n".join(b))

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
      box(0, 210, 380, 100, "프롬프트 1회 읽기", ["시청 기록 + 맥락"]),
      arrow(384, 260, 500, 260, "순전파 1번"),
      box(504, 210, 384, 100, "전체 점수", ["수천 개 작품 동시에"], True)]
figs["prefill"] = svg(330, "\n".join(b))

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
              ("w × 랭킹 손실", ["가치 높은 참여는 크게, 바람직하지 않은 행동은 작게. RL(GRPO)보다 단순·저비용"], False)])
figs["reward"] = svg(h, b)

for name, s in figs.items():
    Path(__file__).with_name(f"{name}.svg").write_text(s, encoding="utf-8")
print("made", ", ".join(figs))
