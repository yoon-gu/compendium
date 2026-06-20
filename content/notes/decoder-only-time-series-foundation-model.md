---
title: "시계열 예측을 위한 디코더 전용 기반 모델"
date: 2026-06-20
draft: false
source_url: "https://arxiv.org/abs/2310.10688"
author: "Abhimanyu Das, Weihao Kong, Rajat Sen, Yichen Zhou (Google Research)"
tags: ["AI", "Time Series", "Foundation Model", "Forecasting", "Transformer"]
summary: "Google Research의 TimesFM 논문을 한국어로 옮겼다. 이 논문은 대규모 실제·합성 시계열 코퍼스로 디코더 전용 Transformer를 사전학습해, 보지 못한 예측 데이터셋에서도 강한 제로샷 성능을 얻을 수 있음을 보인다."
---

> **원문:** [A decoder-only foundation model for time-series forecasting](https://arxiv.org/abs/2310.10688) — Abhimanyu Das, Weihao Kong, Rajat Sen, Yichen Zhou, Google Research, arXiv 2310.10688
>
> 아래 글은 원문 논문의 구조와 서술을 따라가며 한국어로 옮긴 번역본의 짧은 안내 노트다.

전문은 [한국어 번역본](/compendium/papers/decoder-only-time-series-foundation-model/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/decoder-only-time-series-foundation-model.pdf) — 원문 TeX 구조를 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/decoder-only-time-series-foundation-model-original.pdf)

## 핵심 요지

이 논문은 시계열 예측에서도 자연어 처리의 대규모 언어 모델처럼, 큰 규모의 이질적 데이터로 사전학습한 기반 모델(foundation model)이 다양한 다운스트림 데이터셋에 제로샷으로 적용될 수 있는지를 묻는다. 저자들은 입력 시계열을 패치 단위 토큰으로 바꾸고 디코더 전용 Transformer로 다음 패치를 예측하는 TimesFM을 제안한다.

핵심은 세 가지다. 첫째, 모델은 실제 데이터셋뿐 아니라 여러 주기·추세·노이즈 구조를 가진 합성 시계열을 함께 사용해 훈련된다. 둘째, 입력 패치 길이와 출력 패치 길이를 분리해 긴 예측 범위에서도 autoregressive decoding 비용을 줄인다. 셋째, Monash, Darts, Informer/ETT 계열의 벤치마크에서 데이터셋별 감독학습 모델에 근접하거나 일부 경우 더 나은 제로샷 성능을 보인다.

## 실무적으로 볼 부분

1. 시계열 기반 모델을 만들 때 텍스트 LLM 구조를 그대로 가져오는 것만으로는 부족하고, 패칭 방식·컨텍스트 길이·출력 패치 길이 같은 시계열 고유의 설계가 중요하다는 점을 잘 보여준다.
2. 합성 데이터는 단순한 데이터 증강이 아니라, 실제 공개 데이터에 부족한 주파수·계절성·세분성을 보완하는 역할을 한다.
3. 제로샷 성능 평가는 데이터셋별 scale 차이를 어떻게 정규화할 것인지가 중요하며, 논문은 MAE, scaled MAE, 기하평균을 함께 사용한다.
4. 파인튜닝 실험은 기반 모델이 특정 벤치마크에서 추가 적응될 수 있음을 보이지만, 논문의 중심 메시지는 여전히 범용 제로샷 예측이다.

## 번역 범위

한국어 PDF는 원문 TeX를 기반으로 본문, 표·그림 캡션, 수식 주변 설명, 참고문헌, 부록을 포함해 구조를 보존하도록 번역했다. 그림, 표, 수식, 레이블, 참조, 인용, bibliography hook은 원문 개수를 유지하도록 검증했다.
