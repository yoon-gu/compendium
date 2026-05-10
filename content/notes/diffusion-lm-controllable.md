---
title: "Diffusion-LM 요약: 연속 디퓨전으로 세밀 제어 가능한 텍스트 생성"
date: 2026-05-10
draft: false
math: true
source_url: "https://arxiv.org/abs/2205.14217"
author: "Li, Thickstun, Gulrajani, Liang, Hashimoto (Stanford)"
tags: ["AI", "NLP", "디퓨전", "디퓨전 언어모델", "제어 가능 생성", "NeurIPS 2022", "Stanford"]
summary: "Diffusion-LM은 가우시안 잡음 벡터를 점진적으로 단어 벡터로 잡음제거하는 비자기회귀 언어모델이다. 학습 가능한 임베딩과 $x_0$ 매개변수화 + 클램핑 트릭으로 이산 토큰 문제를 해결하고, 연속 잠재 변수에 대한 그라디언트 기반 분류기 가이던스로 구문 트리·POS·길이·인필링 등 6개 세밀 제어 과제에서 기존 PPLM·FUDGE 대비 성공률을 거의 두 배로 높였다."
---

> 이 글은 [Diffusion-LM 한국어 번역본](/compendium/papers/diffusion-lm-controllable/)의 짧은 요약입니다. 라인바이라인 번역과 PDF 링크는 그쪽을 참고하세요.

## 한 문장 요약

**Diffusion-LM**은 가우시안 잡음 시퀀스를 단어 벡터로 점진적으로 잡음제거하는 *연속(continuous) 디퓨전 기반 비자기회귀(non-autoregressive)* 언어모델이며, 그 결과로 만들어지는 *연속 잠재 변수의 위계*를 분류기 그라디언트로 직접 조작해 구문 트리·POS·길이·의미 콘텐츠·인필링 같은 *세밀 제어(fine-grained control)* 를 단일 프레임워크로 푼다.

## 핵심 아이디어

1. **임베딩 + 라운딩 단계 추가**: 이산 단어 $\mathbf{w}$ 와 연속 잠재 $\mathbf{x}_0$ 사이에 $q_\phi(\mathbf{x}_0 \mid \mathbf{w}) = \mathcal{N}(\mathrm{Emb}(\mathbf{w}), \sigma_0 I)$ 를 추가하고, 역과정 끝에 학습 가능한 라운딩 $p_\theta(\mathbf{w} \mid \mathbf{x}_0)$ 을 둔다. 임베딩과 디퓨전 모델을 *엔드투엔드*로 함께 학습 (목적함수 $\mathcal{L}^{\text{e2e}}_{\text{simple}}$).
2. **$\mathbf{x}_0$ 매개변수화**: 표준 디퓨전이 $\mu_\theta$ 또는 잡음 $\epsilon$ 을 예측하는 것과 달리, 모델 $f_\theta(\mathbf{x}_t, t)$ 가 *모든 $t$ 에서* 클린 $\mathbf{x}_0$ 를 직접 예측하도록 재매개변수화. 라운딩 오류를 줄여 $\mathbf{x}_0$ 가 *실제 단어 임베딩* 에 정확히 위치하도록 한다.
3. **클램핑 트릭(clamping trick)**: 디코딩 시 $\mathbf{x}_{t-1} = \sqrt{\bar\alpha}\cdot \mathrm{Clamp}(f_\theta(\mathbf{x}_t, t)) + \sqrt{1-\bar\alpha}\,\epsilon$ 처럼 예측 벡터를 *가장 가까운 단어 임베딩*으로 강제 스냅. 중간 단계에서 단어 약속을 시키는 효과.
4. **새 노이즈 스케줄(sqrt)**: $\bar\alpha_t = 1 - \sqrt{t/T + s}$. $t=0$ 부근에서 가우시안 노이즈가 단어의 최근접 이웃을 잘 안 바꾸어 학습 신호가 빈약해지는 문제를 해결하기 위해, 처음 50 스텝에서 노이즈를 빠르게 올리고 이후 완만히 증가시킨다.
5. **분류기 가이던스 기반 제어**: 잠재 시퀀스 $\mathbf{x}_{0:T}$ 에 대해 $\nabla_{\mathbf{x}_{t-1}} \log p(\mathbf{x}_{t-1} \mid \mathbf{x}_t, \mathbf{c}) = \nabla \log p(\mathbf{x}_{t-1}\mid\mathbf{x}_t) + \nabla \log p(\mathbf{c}\mid \mathbf{x}_{t-1})$ 로 그라디언트 업데이트. *유창성 정규화* $\lambda \log p(\mathbf{x}_{t-1}\mid\mathbf{x}_t)$ 항과 *디퓨전 스텝당 3회 Adagrad 업데이트*, 그리고 2000→200 스텝 다운샘플링이 핵심.
6. **분류기 없는 제어**: 길이·인필링은 분류기 없이도 가능. 인필링은 좌·우 컨텍스트를 양방향으로 조건화하는 자연스러운 시나리오 — 자기회귀 LM 으로는 어려움.

## 주요 결과 (E2E / ROCStories)

분류기 가이던스 5종 과제에서 PPLM·FUDGE 베이스라인 대비 성공률 큰 폭 상승, 일부는 *파인튜닝 오라클까지 능가*.

| 과제 | FUDGE | Diffusion-LM | FT-search (오라클) |
|---|---|---|---|
| Semantic Content | 69.9 | **81.2** | 89.9 |
| Parts-of-speech  | 27.0 | **90.0** | 93.0 |
| Syntax Tree      | 17.9 | **86.0** | 76.4 |
| Syntax Spans     | 54.2 | **93.8** | 54.4 |
| Length           | 46.9 | **99.9** | 100.0 |

(% ctrl 성공률 — 높을수록 좋음. PPLM 은 Semantic Content 에서 9.9% 로 다른 4 과제는 위치 정보 부재로 적용 불가.)

## 세부 결과

- **제어 합성**: Semantic Content + Syntax Tree, Semantic Content + POS 조합에서 *두 제약을 동시에* 만족시키는 율이 FUDGE 와 FT-PoE(파인튜닝 product of experts) 모두를 큰 폭으로 능가. 모듈식 분류기 합산이 자연스럽게 작동.
- **인필링** (aNLG, BLEU-4 / ROUGE-L / CIDEr / BERTScore): Diffusion-LM **7.1 / 28.3 / 30.7 / 89.0** vs DELOREAN 1.6/19.1/7.9/41.7, COLD 1.8/19.5/10.7/42.7. *분류기 없이 MBR 디코딩만으로도* 처음부터 인필링용으로 학습한 자기회귀 LM 수준에 도달.
- **NLL 트레이드오프**: Diffusion-LM 의 변분 NLL 상한은 같은 크기 AR 트랜스포머보다 나쁘다 (E2E 2.28 vs 1.77, ROCStories 3.88 vs 3.05). 제어 성능을 얻는 대가로 우도가 약간 손해.
- **속도**: 200 스텝으로 다운샘플해도 자기회귀 LM 대비 ≈7배 느린 디코딩. 제어 시 PPLM 보다는 60배 빠르고 FUDGE 보다 1.5배 느림.

## 절제

- **학습 임베딩 vs 무작위**: 학습 임베딩이 ROCStories 처럼 어려운 LM 과제에서 의미 있게 우월. E2E 에서는 격차가 작음.
- **$\mathbf{x}_0$ vs $\epsilon$ 매개변수화**: $\mathbf{x}_0$ 매개변수화는 임베딩 차원 전반에서 안정. $\epsilon$ 은 작은 차원에선 동작하지만 큰 차원에서 빠르게 붕괴 — *라운딩이 명시 모델링되지 않기 때문*.
- **노이즈 스케줄**: sqrt 가 cosine·linear 보다 안정. 다만 $\mathbf{x}_0$ 매개변수화가 들어가면 sqrt 의 이점이 작아짐 (즉 sqrt 와 $\mathbf{x}_0$ 매개변수화는 *같은 문제* 를 다른 방식으로 푸는 셈).

## 내가 흥미롭게 본 지점

- 텍스트의 *이산성*이라는 진짜 적은 디퓨전 자체가 아니라 *임베딩 ↔ 단어 사이의 라운딩 단계*에 있다는 진단. 이 진단을 받아들이면 자연히 (a) $\mathbf{x}_0$ 를 모든 항에서 명시 예측, (b) 디코딩 중에도 클램핑으로 단어로 *되돌리는 압력*을 주는 두 처방이 나온다.
- 자기회귀 좌→우 생성이 강요하는 구조적 한계 — 인필링과 *전역적 구문 제약*은 본질적으로 양방향. 디퓨전은 *시퀀스 전체*를 한꺼번에 다루기에 이런 제약을 자연스럽게 처리. 구문 트리 제어에서 파인튜닝 오라클까지 *능가*하는 결과가 그 증거.
- "거친→세밀(coarse-to-fine) 잠재 위계"라는 관점 — $t \approx T$ 에서는 시퀀스 전역 속성, $t \approx 0$ 에서는 개별 토큰 식별을 분류기가 동시에 조작 가능. 같은 모델로 길이부터 토큰 단위 POS 까지 한 인터페이스로 풀린다.
- *유창성 정규화* $\lambda \log p(\mathbf{x}_{t-1}\mid\mathbf{x}_t)$ — 이미지 디퓨전의 분류기 가이던스에는 보통 들어가지 않는 항이지만, 텍스트에서는 이 항이 없으면 분류기 신호만 따라가다 비유창한 출력이 나온다는 관찰.

## 더 읽기

- 전체 한국어 번역본 (모든 절·표·부록 정리): [/papers/diffusion-lm-controllable/](/compendium/papers/diffusion-lm-controllable/)
- arxiv 원문 PDF: [diffusion-lm-controllable-original.pdf](/compendium/papers/diffusion-lm-controllable-original.pdf)
- 원문: [arxiv 2205.14217](https://arxiv.org/abs/2205.14217) — Li et al., NeurIPS 2022
- 코드: [github.com/XiangLi1999/Diffusion-LM](https://github.com/XiangLi1999/Diffusion-LM)
