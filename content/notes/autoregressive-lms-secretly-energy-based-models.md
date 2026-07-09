---
title: "Autoregressive LM은 은밀한 Energy-Based Model이다"
date: 2026-07-09
draft: false
source_url: "https://arxiv.org/abs/2512.15605"
author: "Mathieu Blondel, Michael E. Sander, Germain Vivier-Ardisson, Tianlin Liu, Vincent Roulet"
tags: ["AI", "Language Model", "Energy-Based Model", "Reinforcement Learning", "Theory"]
summary: "Autoregressive LM과 Energy-Based Model을 확률 chain rule과 soft Bellman equation으로 연결해, next-token prediction이 어떻게 lookahead/planning 능력을 가질 수 있는지 설명하는 논문이다."
---

> **원문:** [Autoregressive Language Models are Secretly Energy-Based Models: Insights into the Lookahead Capabilities of Next-Token Prediction](https://arxiv.org/abs/2512.15605) — Mathieu Blondel, Michael E. Sander, Germain Vivier-Ardisson, Tianlin Liu, Vincent Roulet, arXiv 2512.15605
>
> 아래 글은 원문 논문의 핵심을 한국어로 정리한 짧은 note다. 원문 구조를 보존한 한국어 번역본은 PDF와 전문 page에서 볼 수 있다.

전문은 [한국어 번역본](/compendium/papers/autoregressive-lms-secretly-energy-based-models/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/autoregressive-lms-secretly-energy-based-models.pdf)
- [arXiv 원문 PDF](/compendium/papers/autoregressive-lms-secretly-energy-based-models-original.pdf)

## 왜 중요한가

이 논문은 현재 LLM의 주류인 autoregressive model(ARM)과, alignment post-training의 optimal policy를 자연스럽게 표현하는 energy-based model(EBM)을 하나의 관점에서 본다. 핵심 메시지는 단순하다. next-token prediction만으로 학습된 ARM도 적절한 함수공간 관점에서는 EBM과 거의 같은 대상을 표현할 수 있으며, 이 대응이 ARM의 lookahead/planning 능력을 설명한다.

특히 논문은 확률의 chain rule에서 출발해 ARM과 EBM 사이의 explicit bijection을 만들고, 이것이 maximum-entropy reinforcement learning의 soft Bellman equation의 특수한 경우와 맞닿아 있음을 보인다. 따라서 next-token prediction은 겉보기에는 한 token씩만 보는 local objective처럼 보이지만, 그 내부에는 sequence-level energy 또는 reward 구조를 흡수하는 경로가 있다.

## 핵심 기여

1. ARM과 EBM을 같은 함수공간에서 비교하는 unified perspective를 제시한다.
2. ARM과 EBM 사이의 exact bijection을 보이며, 이를 probability chain rule과 soft Bellman equation으로 해석한다.
3. supervised learning에서 ARM과 EBM의 optimum이 동등함을 증명한다.
4. EBM을 ARM으로 distillation할 때의 KL error bound를 도출한다.
5. 수치 실험으로 ARM과 EBM의 loss landscape와 logit/energy 분포가 이론적 대응과 맞아떨어지는지 확인한다.

## practitioner 관점의 읽는 법

- 이 논문은 새로운 training recipe라기보다는, 왜 next-token prediction이 sequence-level behavior를 낳을 수 있는지 설명하는 theoretical lens에 가깝다.
- alignment, reward modeling, MaxEnt RL, EBM, GFlowNet 쪽 배경이 있으면 논문의 bijection과 soft Bellman 해석이 특히 유용하다.
- 논문의 결과는 function space에서의 equivalence를 다루므로, 실제 Transformer parameterization, optimization dynamics, finite data, sampling efficiency까지 자동으로 해결해 주지는 않는다.
- 그럼에도 “ARM은 정말 next token만 보는가?”라는 질문에 대해, ARM이 EBM의 sequence-level structure를 implicit하게 encode할 수 있다는 강한 이론적 답을 제공한다.

## 한 줄 요약

Autoregressive LM은 next-token predictor처럼 보이지만, 확률 chain rule과 soft Bellman 관점에서 보면 sequence-level Energy-Based Model을 암묵적으로 구현할 수 있다.
