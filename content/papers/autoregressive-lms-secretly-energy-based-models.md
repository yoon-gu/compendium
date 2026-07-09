---
title: "Autoregressive LM은 은밀한 Energy-Based Model이다"
date: 2026-07-09
draft: false
math: true
source_url: "https://arxiv.org/abs/2512.15605"
author: "Mathieu Blondel, Michael E. Sander, Germain Vivier-Ardisson, Tianlin Liu, Vincent Roulet"
tags: ["AI", "Language Model", "Energy-Based Model", "Reinforcement Learning", "Theory"]
summary: "Autoregressive LM과 Energy-Based Model 사이의 bijection, supervised learning optimum의 동등성, EBM-to-ARM distillation error bound를 통해 next-token prediction의 lookahead 능력을 설명한다."
---

짧은 요약은 [/notes/autoregressive-lms-secretly-energy-based-models/](/compendium/notes/autoregressive-lms-secretly-energy-based-models/)에서 볼 수 있다.

> **원문:** [Autoregressive Language Models are Secretly Energy-Based Models: Insights into the Lookahead Capabilities of Next-Token Prediction](https://arxiv.org/abs/2512.15605) — Mathieu Blondel, Michael E. Sander, Germain Vivier-Ardisson, Tianlin Liu, Vincent Roulet, arXiv 2512.15605
>
> 아래 page는 원문 논문의 구조를 보존한 한국어 TeX/PDF 번역본을 위한 Compendium entry다. 수식, proposition, proof, figure, appendix를 포함한 full translation은 PDF로 제공한다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/autoregressive-lms-secretly-energy-based-models.pdf) — 원문 TeX 구조를 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/autoregressive-lms-secretly-energy-based-models-original.pdf)

## 초록

Autoregressive model(ARM)은 현재 large language model(LLM)의 지배적 paradigm이다. Energy-based model(EBM)은 LLM 개발에서는 역사적으로 덜 널리 쓰였지만, post-training alignment에서 optimal policy를 자연스럽게 특징짓는 또 다른 model class다. 이 논문은 두 model class를 unified view로 연결한다. 확률의 chain rule을 출발점으로 삼아 함수공간에서 ARM과 EBM 사이의 explicit bijection을 세우고, 이 bijection이 maximum entropy reinforcement learning의 soft Bellman equation의 특수한 경우에 해당함을 보인다. 또한 이 bijection 위에서 ARM과 EBM의 supervised learning이 갖는 동등성을 도출하고, EBM을 ARM으로 distillation할 때의 theoretical error bound를 분석한다. 결과적으로 이 논문은 next-token prediction paradigm에 기반한 ARM이 어떻게 lookahead/planning 능력을 가질 수 있는지 설명한다.

## 번역본 안내

이 entry의 canonical full translation은 한국어 PDF다. TeX workspace에는 원문 arXiv source를 보존하면서, 본문과 appendix의 자연어 문장, section/paragraph title, caption, item text를 한국어로 옮긴 `main.tex`가 들어 있다. 수식, label/ref/cite, figure include, proof structure, bibliography hook은 유지했다.

- TeX workspace: `papers-tex/autoregressive-lms-secretly-energy-based-models/`
- 원문 PDF: `static/papers/autoregressive-lms-secretly-energy-based-models-original.pdf`
- 한국어 PDF: `static/papers/autoregressive-lms-secretly-energy-based-models.pdf`

## 논문 구조

1. **Introduction** — ARM과 EBM을 비교하는 motivation, next-token prediction과 lookahead에 대한 문제 제기, contribution 요약.
2. **A unified perspective on EBMs and ARMs** — EBM/ARM 정의, supervised learning objective, MaxEnt RL objective와의 연결.
3. **ARM-EBM bijection and supervised-learning equivalence** — 함수공간에서의 bijection, 같은 minima, KL bound와 distillation 해석.
4. **Discussion and related work** — MaxEnt RL, probabilistic inference, GFlowNet, energy-based modeling, lookahead 관련 논의.
5. **Supplementary materials** — variable-length sequence 처리, chain rule, bijection proof, gradient/backpropagation, numerical illustration details.

## 읽을 때 유의할 점

- 이론 결과는 function space에서의 equivalence를 주로 다룬다. 실제 finite-width Transformer, optimization, sampling cost는 별도의 문제로 남는다.
- ARM이 EBM과 동등한 구조를 가질 수 있다는 주장은 next-token prediction 자체를 부정하는 것이 아니라, next-token distribution이 sequence-level energy/reward 구조를 chain rule로 흡수할 수 있음을 말한다.
- MaxEnt RL, EBM, distillation, sequence-level reward modeling을 다루는 practitioner에게 특히 유용한 이론적 lens다.
