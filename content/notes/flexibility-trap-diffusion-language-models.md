---
title: "유연성의 함정: Diffusion Language Model에서 arbitrary order 다시 보기"
date: 2026-07-08
draft: false
source_url: "https://arxiv.org/abs/2601.15165"
author: "Zanlin Ni, Shenzhi Wang, Yang Yue, Tianyu Yu, Weilin Zhao, Yeguo Hua, Tianyi Chen, Jun Song, Cheng Yu, Bo Zheng, Gao Huang"
tags: ["AI", "Diffusion Language Models", "Reasoning", "Reinforcement Learning", "GRPO"]
summary: "이 논문은 dLLM의 arbitrary-order generation이 일반 reasoning task에서 항상 장점이 아니라, high-uncertainty fork를 우회하게 만들어 solution coverage를 줄일 수 있다고 주장한다. 저자들은 복잡한 diffusion-specific RL 대신 AR order로 학습 중 exploration을 제한한 JustGRPO가 GSM8K·MATH-500 등에서 강한 성능을 내면서도 dLLM의 parallel decoding 능력을 유지함을 보인다."
---

전문은 [한국어 번역본](/compendium/papers/flexibility-trap-diffusion-language-models/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/flexibility-trap-diffusion-language-models.pdf) — 원문 TeX 레이아웃을 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/flexibility-trap-diffusion-language-models-original.pdf)

> **원문:** [The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models](https://arxiv.org/abs/2601.15165) — Zanlin Ni et al., arXiv 2601.15165v4
>
> 아래 글은 논문의 문제의식과 주요 결과를 한국어로 정리한 짧은 note다. 전체 line-by-line 번역과 figure/table은 위 한국어 PDF에 보존했다.

## 핵심 요약

Diffusion Large Language Models(dLLMs)는 left-to-right로만 token을 생성하는 autoregressive model과 달리, token을 arbitrary order로 채울 수 있다. 직관적으로는 이 유연성이 더 넓은 solution space를 제공하므로 reasoning에 유리해 보인다. 하지만 이 논문은 수학·코딩 같은 일반 reasoning task에서는 오히려 arbitrary order가 reasoning potential을 좁힐 수 있다고 주장한다.

핵심 관찰은 reasoning이 균일하게 이어지는 과정이 아니라, “Therefore”, “Since” 같은 logical fork에서 경로가 갈라지는 과정이라는 점이다. AR decoding은 이런 high-uncertainty token을 반드시 먼저 마주하게 하므로 여러 reasoning path를 sampling할 수 있다. 반면 arbitrary-order decoding은 더 쉬운 low-uncertainty token을 먼저 채우면서 어려운 fork를 우회할 수 있다. 이후 미래 context가 이미 고정된 상태에서 fork를 다시 채우면, 원래 열려 있던 branching 가능성은 줄어든다. 저자들은 이를 entropy degradation이라고 부른다.

이 관찰은 dLLM용 RL 설계를 다시 생각하게 만든다. 많은 diffusion-specific RL 방법은 arbitrary-order trajectory를 보존하려고 combinatorial trajectory, intractable likelihood, sampler-learner mismatch 같은 복잡성을 감수한다. 하지만 arbitrary order가 일반 reasoning에서 필수적이지 않거나 해롭다면, 그 복잡성은 “flexibility tax”일 수 있다.

논문은 이 문제에 대한 단순한 대안으로 JustGRPO를 제안한다. 학습 중에는 dLLM을 AR policy처럼 다루고 표준 Group Relative Policy Optimization(GRPO)을 거의 그대로 적용한다. 중요한 점은 inference에서 dLLM architecture 자체를 바꾸거나 causal mask를 도입하지 않는다는 것이다. 학습 시 exploration order만 left-to-right로 제한하고, inference에서는 dLLM의 parallel decoding 능력을 유지한다.

## 왜 흥미로운가

1. dLLM의 대표 장점으로 여겨진 arbitrary-order generation을 “항상 좋은 자유도”가 아니라 task-dependent inductive bias로 다시 해석한다.
2. Pass@$k$를 reasoning potential의 proxy로 사용해, AR order가 더 높은 solution coverage를 만들 수 있음을 보인다.
3. entropy degradation이라는 메커니즘을 통해 arbitrary order가 high-uncertainty fork를 우회하는 방식을 설명한다.
4. 복잡한 diffusion-specific RL보다 단순한 JustGRPO가 강한 성능을 낼 수 있음을 보여, dLLM post-training의 설계 공간을 단순화한다.
5. 학습 중 sequential exploration과 inference 중 parallel decoding을 분리함으로써, reasoning 성능과 dLLM inference 효율을 함께 유지하려 한다.

## 주요 결과

저자들은 LLaDA-Instruct를 중심으로 실험한다. AR order로 제한한 decoding은 arbitrary-order decoding보다 Pass@$k$에서 더 높은 reasoning boundary를 보이는 경향이 있다. JustGRPO는 GSM8K에서 89.1%, MATH-500에서 45.1%를 보고하며, diffusion-specific RL adaptation을 사용하는 기존 방법들과 경쟁적이거나 더 나은 결과를 낸다. 또한 block size를 키워 parallel decoding을 사용할 때도 성능 저하가 완만해, RL로 얻은 reasoning capability가 dLLM의 parallel decoding과 양립 가능함을 보인다.

## 읽을 때 주의할 점

이 논문은 arbitrary order 자체를 폐기하자는 주장이 아니다. 저자들도 일반 capability benchmark에서는 JustGRPO 이후 성능이 유지됨을 보고한다. 논문의 메시지는 더 좁다. 수학·코딩처럼 branching decision이 중요한 reasoning task에서는 arbitrary order가 exploration을 돕기보다 어려운 결정을 미루고 solution coverage를 줄일 수 있으며, 이 경우 학습 중 AR order라는 단순한 scaffold가 더 효과적일 수 있다는 것이다.
