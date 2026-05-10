---
title: "PRAGMA 요약: Revolut의 멀티 소스 뱅킹 이벤트 시퀀스 파운데이션 모델"
date: 2026-05-09
draft: false
source_url: "https://arxiv.org/abs/2604.08649"
author: "Ostroukhov 외 (Revolut Research × NVIDIA)"
tags: ["AI", "파운데이션 모델", "금융", "Revolut", "트랜잭션", "MLM", "LoRA"]
summary: "PRAGMA는 카드 결제·송금·앱 사용·커뮤니케이션 같은 이질적 뱅킹 이벤트 시퀀스를 통째로 사전학습한 인코더형 파운데이션 모델이다. 단일 백본을 LoRA로 가볍게 적응시켜 신용 평가·사기 탐지·추천 등 6개 과제에서 과제별 모델을 큰 폭으로 능가한다."
---

> 이 글은 [PRAGMA 한국어 번역본](/compendium/papers/pragma-revolut-foundation-model/)의 짧은 요약입니다. 라인바이라인 번역과 PDF는 그쪽을 참고하세요.

## 한 문장 요약

PRAGMA는 26M 사용자·207B 토큰 규모의 멀티 소스 뱅킹 이벤트 위에서 마스킹 모델링(MLM)으로 학습된 **인코더 전용 트랜스포머 백본**이며, 동일 백본을 LoRA로 가볍게 적응시키는 것만으로 6개 다운스트림 과제에서 과제별 베이스라인을 일관되게 능가한다.

## 핵심 아이디어

1. 키–값–시간(key–value–time) 토큰화: 각 이벤트를 의미 타입(키), 값(범주/수치/텍스트), 시간 좌표로 분해. 수치는 백분위 버킷, 범주는 단일 토큰, 텍스트는 BPE 서브워드로 토큰화. 시간은 직전 이벤트 대비 로그-초 + 달력 주기 피처(시각·요일·일자)로 함께 인코딩.
2. 2-가지(branch) 인코더 구조: 정적 프로필 상태(플랜·잔고 분위 등)는 *프로필 상태 인코더*가, 이벤트 시퀀스는 *이벤트 인코더*가 각각 독립적으로 처리한 뒤, *히스토리 인코더*가 두 표현을 융합한다. RoPE로 절대 시간 좌표를 인코딩.
3. MLM 사전학습: 토큰 단위(15%) + 이벤트 단위(10%) + 키 단위(10%) 마스킹을 혼합. 일부 위치는 `[MASK]` 대신 `[UNK]`로 치환해 입력 드롭아웃 효과.
4. 3가지 모델 크기: PRAGMA-S(10M), PRAGMA-M(100M), PRAGMA-L(1B). 16-32×H100에서 2일-2주.
5. 두 가지 적응 모드: 임베딩 프로빙(고정 백본 위에 선형 프로브) / LoRA 파인튜닝(2-4% 파라미터만 갱신).

## 주요 결과 (PRAGMA-L LoRA, 베이스라인 대비 상대 향상)

| 과제 | 지표 | 향상 |
|---|---|---|
| 신용 평가 | PR-AUC / ROC-AUC | +130.2% / +12.4% |
| 커뮤니케이션 인게이지먼트 | PR-AUC / ROC-AUC | +79.4% / +20.4% |
| 외부 사기 | Precision / Recall | +16.7% / +64.7% |
| 상품 추천 | mAP | +40.5% |
| 정기 거래 | F₁ | +5.8% |
| 라이프타임 밸류 | PR-AUC / ROC-AUC | +1.8% / +2.6% |

소수 클래스 식별이 결정적인 신용 평가/커뮤니케이션 인게이지먼트에서 향상폭이 가장 크다. 반면 본질이 관계적(cross-record)인 자금세탁방지(AML)에서는 −47.1% F₀.₅로 한계를 드러냄 — PRAGMA가 이력을 사용자별로 고립 처리하기 때문.

## 내가 흥미롭게 본 지점

- 이벤트가 곧 토큰이라기보다, "키 1개 + 값 N개 + 시간 1개"로 이벤트를 펼쳐 *내부 위치 임베딩이 필드 안*에서만 의미를 갖게 한 점. 텍스트 LLM의 토큰화를 표 형식 데이터로 옮길 때의 가장 깔끔한 해법 중 하나.
- 시퀀스 패킹 + 동적 배칭으로 패딩 오버헤드를 제거해 처리량 2-5배 향상. 운영 환경에서 효율성 차원의 영향이 큰 디테일.
- LoRA가 *전체 학습보다 일관되게 같거나 더 좋다*는 결과 — 사전학습 백본의 표현이 실제로 과제 간에 잘 전이된다는 강한 증거.

## 더 읽기

- 전체 한국어 번역본 (라인바이라인 + 모든 표·그림): [/papers/pragma-revolut-foundation-model/](/compendium/papers/pragma-revolut-foundation-model/)
- 한국어 PDF: [pragma-revolut-foundation-model.pdf](/compendium/papers/pragma-revolut-foundation-model.pdf)
- arxiv 원문 PDF: [pragma-revolut-foundation-model-original.pdf](/compendium/papers/pragma-revolut-foundation-model-original.pdf)
- 원문: [arxiv 2604.08649](https://arxiv.org/abs/2604.08649)
