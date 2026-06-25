---
title: "VibeThinker-3B: 소형 언어 모델에서 검증 가능한 추론의 프런티어 탐색"
date: 2026-06-25
draft: false
math: true
source_url: "https://arxiv.org/abs/2606.16140"
author: "Sen Xu, Shixi Liu, Wei Wang, Jixin Min, Yingwei Dai, Zhibin Yin, Yirong Chen, Xin Zhou, Junlin Zhang (Sina Weibo Inc.)"
tags: ["AI", "Reasoning", "Small Language Models", "Reinforcement Learning", "Synthetic Data"]
summary: "3B 규모 VibeThinker-3B가 검증 가능한 수학·코딩 추론에서 프런티어급 성능에 접근할 수 있음을 보이고, 추론 깊이와 개방형 지식 폭을 분리해 해석하는 관점을 제안한다."
---

짧은 요약은 [/notes/vibethinker-3b-verifiable-reasoning/](/compendium/notes/vibethinker-3b-verifiable-reasoning/)에서 볼 수 있다.

> **원문:** [VibeThinker-3B: Exploring the Frontier of Verifiable Reasoning in Small Language Models](https://arxiv.org/abs/2606.16140) — Sen Xu, Shixi Liu, Wei Wang, Jixin Min, Yingwei Dai, Zhibin Yin, Yirong Chen, Xin Zhou, Junlin Zhang, Sina Weibo Inc., arXiv 2606.16140
>
> 아래 글은 원문 논문의 순서와 서술을 최대한 따라가며 한국어로 옮긴 것이다. 수식, 표, 그림, citation, label, bibliography 구조는 TeX/PDF 번역본에서 보존했다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/vibethinker-3b-verifiable-reasoning.pdf) — 원문 레이아웃을 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/vibethinker-3b-verifiable-reasoning-original.pdf)

## 전문 번역 안내

이 논문은 그림·표·수식·참조가 포함된 기술 보고서 형태이며, 구조 보존을 위해 전체 한국어 번역은 TeX 기반 PDF로 제공한다.

- 한국어 TeX workspace: `papers-tex/vibethinker-3b-verifiable-reasoning/`
- 주요 엔트리포인트: `neurips_2026.tex`
- 원문 그림, 표, 수식, label/ref/cite, bibliography hook은 번역본 TeX/PDF에 유지했다.

## 초록 번역

이 기술 보고서는 엄격한 소형 모델 체제 안에서 검증 가능한 추론을 어디까지 밀어붙일 수 있는지 조사하기 위해 개발된 3B 파라미터의 compact dense model인 VibeThinker-3B를 소개한다. Spectrum-to-Signal post-training 패러다임을 바탕으로, 저자들은 curriculum-based supervised fine-tuning, multi-domain reinforcement learning, offline self-distillation을 포함하는 최적화된 파이프라인을 통해 모델을 체계적으로 강화한다.

실험 평가는 VibeThinker-3B가 매우 까다로운 검증 가능 과제에서 프런티어급 성능을 달성함을 보인다. 구체적으로 AIME26에서 94.3점을 달성하고, claim-level test-time scaling을 적용하면 97.1로 향상된다. LiveCodeBench v6에서는 Pass@1 80.2를 달성하며, 최근 공개되지 않았던 LeetCode contest에서는 96.1% acceptance rate로 강한 out-of-distribution generalization을 보인다.

이 결과는 VibeThinker-3B를 1차 추론 시스템의 성능대에 올려놓으며, DeepSeek V3.2, GLM-5, Gemini 3 Pro처럼 파라미터 수가 훨씬 큰 flagship model과 일부 검증 가능 추론 과제에서 맞먹거나 능가할 수 있음을 시사한다. 또한 IFEval 93.4점은 극단적인 추론 강화가 엄격한 instruction controllability를 반드시 훼손하지는 않는다는 점을 확인한다.

저자들은 이전 1.5B 작업을 확장하면서 Parametric Compression-Coverage Hypothesis를 제안한다. 이 관점은 검증 가능한 추론을 compact reasoning core로 압축할 수 있는 능력으로 보는 반면, open-domain knowledge와 general-purpose competence는 사실, 개념, long-tail scenario에 대한 폭넓은 parameter coverage를 요구한다고 본다. 따라서 compact model은 단순한 배포 효율 대체물이 아니라 parameter-dense capability regime에서 프런티어급 성능을 향한 보완적 경로가 될 수 있다.
