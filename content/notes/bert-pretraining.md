---
title: "BERT 요약: 깊은 양방향 트랜스포머의 사전학습"
date: 2026-05-09
draft: false
source_url: "https://arxiv.org/abs/1810.04805"
author: "Devlin, Chang, Lee, Toutanova (Google AI Language)"
tags: ["AI", "NLP", "BERT", "사전학습", "양방향", "트랜스포머", "Google"]
summary: "BERT는 모든 층에서 좌우 양쪽 맥락을 동시에 조건화하는 깊은 양방향 트랜스포머 인코더다. 마스킹 LM과 다음 문장 예측 두 비지도 과제로 사전학습한 단일 모델이, 출력 층 하나만 추가하는 파인튜닝만으로 11개 NLP 과제에서 최첨단을 갱신한다."
---

> 이 글은 [BERT 한국어 번역본](/compendium/papers/bert-pretraining/)의 짧은 요약입니다. 라인바이라인 번역과 PDF는 그쪽을 참고하세요.

## 한 문장 요약

BERT는 **마스킹 언어모델(MLM)** 과 **다음 문장 예측(NSP)** 두 비지도 목적함수로 사전학습된 *깊은 양방향 트랜스포머 인코더*이며, 출력 층 하나만 추가해 파인튜닝하는 것만으로 GLUE·SQuAD·SWAG 등 11개 NLP 벤치마크의 최첨단을 한 번에 갱신했다.

## 핵심 아이디어

1. **양방향성을 가능하게 하는 MLM**: 입력 토큰의 15%를 무작위로 가린 뒤 그 자리의 원본 토큰을 맥락으로 예측. 좌→우 LM(GPT)이나 ELMo의 얕은 결합과 달리, *모든 층*에서 좌·우 맥락을 함께 조건화할 수 있게 됨.
2. **마스킹 트릭**: 선택된 위치를 항상 `[MASK]`로 바꾸지 않음 — 80% `[MASK]`, 10% 임의 토큰, 10% 원본 유지. 사전학습/파인튜닝 불일치를 줄이는 의도.
3. **다음 문장 예측(NSP)**: 두 문장 A/B를 50% 확률로 실제 연속(`IsNext`), 50%로 무작위(`NotNext`)로 묶어 학습. QA·NLI처럼 문장 간 관계가 중요한 과제에 도움.
4. **통일된 입출력 표현**: `[CLS]` (분류 집계) + 토큰 시퀀스 + `[SEP]` (분리). 토큰 임베딩 + 세그먼트 임베딩 + 위치 임베딩의 합. 단일 시퀀스/문장 쌍 모두 동일 형식으로.
5. **두 모델 크기**: BERT-BASE(L=12, H=768, A=12, 110M) ↔ OpenAI GPT와 동일 크기로 직접 비교 가능. BERT-LARGE(L=24, H=1024, A=16, 340M).

## 주요 결과

- **GLUE 평균**: BERT-LARGE **80.5점** (이전 SOTA 75.1, +4.5%p). MNLI에서만 +4.6%p 절대 향상.
- **SQuAD v1.1**: 단일 모델 F1 **91.1**, 앙상블 **93.2** (인간 수준 91.2 초과).
- **SQuAD v2.0**: F1 **83.1**로 이전 최고 시스템 대비 +5.1.
- **SWAG**: BERT-LARGE 86.3% — ESIM+ELMo 대비 +27.1%.
- **CoNLL-2003 NER (피처 기반)**: 상위 4개 층 결합 피처 위 BiLSTM이 전체 파인튜닝 대비 0.3 F1만 뒤짐 — BERT는 피처 기반 사용에도 강함.

## 절제 연구가 말해주는 것

- **NSP 제거** → QNLI, MNLI, SQuAD에서 의미 있는 성능 하락.
- **양방향성 제거(LTR & No NSP)** → 모든 과제에서 추가 하락. 특히 SQuAD에서 큰 폭. BiLSTM을 위에 얹어도 양방향 사전학습 모델에는 한참 못 미침.
- **모델 크기 증가** → 라벨 3,600개에 불과한 MRPC 같은 *작은 다운스트림 데이터*에서도 일관된 향상. 충분히 사전학습된 모델은 적은 라벨로도 큰 모델의 표현력을 활용할 수 있음.

## 내가 흥미롭게 본 지점

- 이전까지 NLP에서 ImageNet-style 전이가 어려웠던 이유 중 하나가 *단방향 LM 제약*이었다는 진단이 명쾌함. MLM은 그 제약을 푸는 깔끔한 우회.
- "거의 모든 과제에서 출력 층 하나만 추가" — 과제별 아키텍처 엔지니어링 시대의 종지부를 찍은 결정적 결과.
- 80/10/10 마스킹 트릭이 절제 실험에서 *파인튜닝에서는 거의 무관*하지만 *피처 기반 NER에서는 의미 있는 차이*를 만든다는 비대칭 — 적응 방식이 사전학습/파인튜닝 불일치에 얼마나 민감한지를 잘 보여줌.

## 더 읽기

- 전체 한국어 번역본 (라인바이라인 + 모든 표·그림 + 부록): [/papers/bert-pretraining/](/compendium/papers/bert-pretraining/)
- 한국어 PDF: [bert-pretraining.pdf](/compendium/papers/bert-pretraining.pdf)
- arxiv 원문 PDF: [bert-pretraining-original.pdf](/compendium/papers/bert-pretraining-original.pdf)
- 원문: [arxiv 1810.04805](https://arxiv.org/abs/1810.04805)
