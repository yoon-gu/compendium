---
title: "시계열 예측을 위한 디코더 전용 기반 모델"
date: 2026-06-20
draft: false
math: true
source_url: "https://arxiv.org/abs/2310.10688"
author: "Abhimanyu Das, Weihao Kong, Rajat Sen, Yichen Zhou (Google Research)"
tags: ["AI", "Time Series", "Foundation Model", "Forecasting", "Transformer"]
summary: "Google Research의 TimesFM 논문 한국어 번역. 대규모 실제·합성 시계열 코퍼스로 디코더 전용 Transformer를 사전학습해, 여러 예측 벤치마크에서 강한 제로샷 성능을 보이는 방법을 설명한다."
---

짧은 요약은 [/notes/decoder-only-time-series-foundation-model/](/compendium/notes/decoder-only-time-series-foundation-model/)에서 볼 수 있다.

> **원문:** [A decoder-only foundation model for time-series forecasting](https://arxiv.org/abs/2310.10688) — Abhimanyu Das, Weihao Kong, Rajat Sen, Yichen Zhou, Google Research, arXiv 2310.10688
>
> 아래 글은 원문 논문의 순서와 서술을 최대한 따라가며 한국어로 옮긴 것이다. TeX 원문 기반의 구조 보존 번역본은 PDF로 제공한다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/decoder-only-time-series-foundation-model.pdf) — 원문 레이아웃과 TeX 객체를 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/decoder-only-time-series-foundation-model-original.pdf)

## 초록

자연어 처리(NLP)를 위한 대규모 언어 모델의 최근 발전에 힘입어, 이 논문은 다양한 공개 데이터셋에 대한 기본 제로샷 성능이 각 개별 데이터셋에 대한 최첨단 감독 예측 모델의 정확도에 근접하는 시계열 예측 기반 모델을 설계한다. 제안 모델은 실제 데이터셋과 합성 데이터셋으로 구성된 대규모 시계열 코퍼스를 사용해 입력 패칭을 갖춘 디코더 스타일 attention 모델을 사전학습한다. 이전에 보지 못한 다양한 예측 데이터셋에 대한 실험은 이 모델이 도메인, 예측 범위, 시간적 세분성에 걸쳐 정확한 제로샷 예측을 생성할 수 있음을 시사한다.

## 문서 구조

번역 PDF는 다음 원문 구조를 유지한다.

1. 서론
2. 관련 연구
3. 문제 정의
4. 모델 아키텍처
5. 사전학습 세부 사항
6. 실증 결과
   - 제로샷 평가
   - 절제 실험
7. 결론
8. 영향 진술
9. 부록
   - 한계와 향후 연구
   - 평가지표
   - ETT에 대한 파인튜닝 연구
   - PatchTST 사전학습
   - 추가 실증 결과
   - 모델에 대한 추가 세부 사항
   - 날짜 특징
   - 합성 데이터
   - 예시 사례

## 번역 및 보존 메모

이 항목에서는 Markdown 본문으로 논문의 모든 표와 수식을 재조판하지 않고, 한국어 TeX/PDF를 전문 번역의 기준 산출물로 둔다. 원문 TeX의 figure, table, tabular, equation, label, reference, citation, `includegraphics`, bibliography hook 개수를 번역본과 비교해 감소가 없음을 확인했다. 한국어 PDF는 XeLaTeX와 kotex로 빌드했으며, 대표 페이지를 렌더링해 본문, 표, 그림, 부록 그림이 깨지지 않는지 확인했다.
