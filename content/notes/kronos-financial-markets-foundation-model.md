---
title: "Kronos: 금융시장의 언어를 위한 파운데이션 모델"
date: 2026-06-16
draft: false
source_url: "https://arxiv.org/abs/2508.02739"
author: "Yu Shi, Zongliang Fu, Shuo Chen, Bohan Zhao, Wei Xu, Changshui Zhang, Jian Li"
tags: ["AI", "Finance", "Time Series", "Foundation Model", "K-line", "Tokenization"]
summary: "Kronos는 금융 K-line 데이터를 전용 토크나이저로 이산 토큰화하고 45개 글로벌 거래소의 120억 개 이상 기록으로 자기회귀 사전학습한 금융 시계열 파운데이션 모델이다. 가격 예측, 변동성 예측, 합성 K-line 생성, 투자 시뮬레이션을 zero-shot으로 다루며 기존 TSFM과 비사전학습 모델 대비 큰 성능 향상을 보고한다."
---

> **원문:** [Kronos: A Foundation Model for the Language of Financial Markets](https://arxiv.org/abs/2508.02739) — Yu Shi, Zongliang Fu, Shuo Chen, Bohan Zhao, Wei Xu, Changshui Zhang, Jian Li, arXiv 2508.02739
>
> 아래 글은 원문 논문의 핵심 구조와 주장, 실험 설정을 한국어로 정리한 것이다. TeX/PDF 판은 원문 레이아웃의 그림·표·수식·부록 구조를 보존하는 번역본으로 제공한다.

전문은 [한국어 번역본](/compendium/papers/kronos-financial-markets-foundation-model/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/kronos-financial-markets-foundation-model.pdf)
- [arXiv 원문 PDF](/compendium/papers/kronos-financial-markets-foundation-model-original.pdf)

## 한눈에 보기

Kronos는 금융시장의 candlestick 또는 K-line 데이터를 하나의 “언어”처럼 다루기 위한 파운데이션 모델이다. 기존 범용 시계열 파운데이션 모델(Time Series Foundation Model, TSFM)은 많은 도메인의 시계열을 함께 다루지만, 금융 K-line의 미세한 가격 동학과 거래 활동 패턴을 포착하는 데 한계가 있었다. 논문은 이 문제를 전용 토크나이저와 대규모 금융 말뭉치 기반 자기회귀 사전학습으로 해결하려 한다.

핵심 아이디어는 연속적인 OHLCVA K-line을 직접 회귀하지 않고, 가격 움직임과 거래량 정보를 보존하는 이산 토큰 시퀀스로 바꾸는 것이다. 이렇게 얻은 토큰열 위에서 언어모델식 autoregressive objective를 적용하면, 금융시장의 시간적 패턴과 자산 간 표현을 함께 학습할 수 있다.

## 왜 중요한가

금융 시계열은 일반적인 센서·수요·기상 시계열과 다르게 비정상성, 두꺼운 꼬리, 거래소·자산·시간 주기별 미세구조 차이가 강하다. 그래서 범용 TSFM이 충분히 큰 말뭉치로 학습되더라도 K-line 데이터에서는 전통적 full-shot 모델이나 도메인 특화 비사전학습 모델을 이기지 못하는 경우가 많다.

Kronos는 이 간극을 “금융 데이터 비중이 높은 대규모 사전학습”과 “금융 K-line에 맞춘 토큰화”라는 두 축으로 다룬다. 논문은 45개 글로벌 거래소에서 모은 120억 개 이상의 K-line 기록을 사용했고, 가격 예측뿐 아니라 변동성 예측, 합성 K-line 생성, 투자 시뮬레이션까지 포괄한다.

## 모델과 토크나이저

Kronos의 토크나이저는 K-line을 여러 subtoken으로 분해해 연속적인 시장 정보를 이산 상태 공간으로 투영한다. 논문은 이 토큰화가 단순 압축이 아니라 노이즈를 줄이고, autoregressive 모델이 학습하기 쉬운 compact discrete state space를 제공한다고 해석한다. 또한 hyperspherical geometry를 이용해 꼬리 사건과 극단 움직임에 대한 민감도를 유지하려는 설계도 논의한다.

사전학습된 Kronos 모델 계열은 금융 K-line 토큰을 다음 토큰 예측 방식으로 학습한다. downstream에서는 동일한 생성 모델을 가격/수익률/변동성 예측, synthetic K-line generation, trading signal generation에 사용한다.

## 실험 결과

논문이 강조하는 결과는 다음과 같다.

1. 가격 시계열 예측에서 Kronos는 선도 TSFM 대비 RankIC를 93%, 최고 비사전학습 baseline 대비 87% 높였다고 보고한다.
2. 변동성 예측에서는 MAE를 약 9% 낮췄다.
3. 합성 K-line 생성에서는 fidelity 지표가 약 22% 개선되었다.
4. 투자 시뮬레이션에서는 Kronos가 생성한 신호가 여러 baseline보다 높은 누적 수익률과 더 안정적인 위험 조정 성과를 보였다.

이 결과는 금융 K-line처럼 도메인 특수성이 큰 시계열에서도, 토큰화와 사전학습 말뭉치 설계를 맞추면 foundation-model 접근이 유효할 수 있음을 보여준다.

## 읽을 때 볼 점

가장 중요한 부분은 성능 수치 자체보다 “왜 기존 TSFM이 금융 K-line에서 약했는가”와 “Kronos의 토크나이저가 무엇을 보존하고 무엇을 버리는가”다. 특히 appendix의 tokenizer ablation, codebook usage, subtoken factorization 분석은 모델의 성능이 단순히 파라미터 수나 데이터 양 때문인지, 아니면 이산화 구조 때문인지 판단하는 데 도움이 된다.

또한 zero-shot 금융 예측 성능을 주장하는 만큼, 데이터 분할, 거래소·자산의 in-distribution/out-of-distribution 구분, look-back window와 forecast horizon 설정, 거래 비용을 포함한 backtest 조건을 함께 확인해야 한다. 금융 모델에서는 작은 누수나 비용 가정 차이가 실전적 해석을 크게 바꿀 수 있기 때문이다.
