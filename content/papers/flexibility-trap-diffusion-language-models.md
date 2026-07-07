---
title: "유연성의 함정: Diffusion Language Model에서 arbitrary order의 가치 재고"
date: 2026-07-08
draft: false
math: true
source_url: "https://arxiv.org/abs/2601.15165"
author: "Zanlin Ni, Shenzhi Wang, Yang Yue, Tianyu Yu, Weilin Zhao, Yeguo Hua, Tianyi Chen, Jun Song, Cheng Yu, Bo Zheng, Gao Huang"
tags: ["AI", "Diffusion Language Models", "Reasoning", "Reinforcement Learning", "GRPO"]
summary: "dLLM의 arbitrary-order generation이 일반 reasoning task에서 high-uncertainty fork를 우회해 solution coverage를 줄일 수 있음을 보이고, 학습 중 AR order로 exploration을 제한하는 단순한 JustGRPO가 강한 reasoning 성능과 parallel decoding 보존을 동시에 달성함을 제시한다."
---

짧은 요약은 [/notes/flexibility-trap-diffusion-language-models/](/compendium/notes/flexibility-trap-diffusion-language-models/)에서 볼 수 있다.

> **원문:** [The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models](https://arxiv.org/abs/2601.15165) — Zanlin Ni, Shenzhi Wang, Yang Yue, Tianyu Yu, Weilin Zhao, Yeguo Hua, Tianyi Chen, Jun Song, Cheng Yu, Bo Zheng, Gao Huang, arXiv 2601.15165v4
>
> 아래 항목의 정식 full translation은 원문 TeX source를 기반으로 만든 한국어 PDF다. Figure, table, equation, citation, appendix 구조는 PDF와 `papers-tex/flexibility-trap-diffusion-language-models/`의 Korean TeX workspace에 보존했다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/flexibility-trap-diffusion-language-models.pdf) — 원문 TeX 레이아웃을 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/flexibility-trap-diffusion-language-models-original.pdf)

## 번역본 안내

이 논문은 공개 arXiv TeX source가 제공되어 있어, Compendium에는 다음 산출물을 함께 보존했다.

1. 원문 PDF: `static/papers/flexibility-trap-diffusion-language-models-original.pdf`
2. 한국어 PDF: `static/papers/flexibility-trap-diffusion-language-models.pdf`
3. 한국어 TeX workspace: `papers-tex/flexibility-trap-diffusion-language-models/`
4. 짧은 한국어 note: `content/notes/flexibility-trap-diffusion-language-models.md`

PDF는 본문, appendix, figure/table caption, table text, equations, labels, references, citations를 보존하는 line-by-line 번역본이다. 아래 Markdown은 PDF를 읽기 전 논문 구조를 빠르게 파악하기 위한 안내다.

## 초록

Diffusion Large Language Models(dLLMs)는 전통적인 LLM의 rigid left-to-right 제약을 깨고 token을 arbitrary order로 생성할 수 있다. 직관적으로 이 유연성은 고정된 autoregressive trajectory를 엄격히 포함하는 solution space를 뜻하므로 더 높은 reasoning potential을 제공할 것처럼 보인다. 그러나 저자들은 수학과 코딩 같은 일반 reasoning task에서 arbitrary-order generation이 dLLM의 reasoning potential을 실제로 제한할 수 있음을 보인다.

핵심 메커니즘은 dLLM이 order flexibility를 사용해 exploration에 중요한 high-uncertainty token을 우회한다는 것이다. 이 우회는 solution coverage의 premature collapse를 낳을 수 있다. 이 관찰은 dLLM을 위한 RL 접근법을 재고하게 한다. 기존 방법들은 combinatorial trajectory와 intractable likelihood를 다루며 arbitrary-order flexibility를 보존하려고 하지만, 저자들은 이 유연성을 포기하고 표준 GRPO를 적용하는 것만으로 효과적인 reasoning을 이끌어낼 수 있음을 보인다. 제안한 JustGRPO는 GSM8K에서 89.1% accuracy를 달성하면서 dLLM의 parallel decoding 능력을 유지한다.

## 논문 구조

### 1. Introduction

논문은 dLLM의 두 장점, 즉 parallel decoding과 arbitrary-order generation을 구분한다. parallel decoding의 효율성은 비교적 명확하지만, arbitrary order가 일반 reasoning에 주는 가치는 덜 분명하다. 저자들은 Pass@$k$를 solution space coverage의 proxy로 사용해 LLaDA-Instruct에서 AR order와 arbitrary order를 비교하고, AR order가 더 높은 reasoning boundary를 만드는 반직관적 결과를 제시한다.

### 2. Preliminaries

이 절은 masked diffusion model 기반 dLLM, GRPO, 그리고 reasoning potential proxy로서 Pass@$k$를 정리한다. 특히 RL이 base distribution을 새로 만드는 것보다 이미 존재하는 distribution을 sharpen하는 성격이 크다는 최근 관찰에 기대어, base model의 Pass@$k$가 post-training 이후 도달 가능한 reasoning ceiling을 가늠하는 지표가 될 수 있다고 설명한다.

### 3. The Flexibility Trap

논문의 중심 절이다. 저자들은 arbitrary order가 더 넓은 decoding space를 제공하지만, 일반 reasoning에서는 high-uncertainty fork를 직접 sampling하지 않고 우회하는 경향 때문에 solution coverage를 줄일 수 있다고 분석한다. Logical fork는 reasoning path가 갈라지는 지점이며 entropy spike로 나타난다. AR order는 이 fork에 맞서도록 강제하지만, arbitrary order는 더 쉬운 future token을 먼저 채워 fork의 ambiguity를 줄인다. 저자들은 이 현상을 entropy degradation이라고 부른다.

### 4. “Just GRPO” for dLLMs

이 절은 arbitrary-order flexibility를 보존하려는 diffusion-specific RL이 치르는 비용을 flexibility tax로 설명한다. Token-level decomposition의 ambiguity, sequence likelihood의 intractability, sampler-learner mismatch가 대표적인 문제다. JustGRPO는 학습 중 dLLM을 AR policy처럼 다루어 표준 GRPO objective를 적용한다. 단, model architecture 자체는 그대로 두며 causal mask를 추가하지 않는다. 따라서 training에서는 sequential exploration의 이점을 얻고, inference에서는 dLLM의 parallel decoding을 유지한다.

### 5. Experiments

실험은 LLaDA-Instruct를 중심으로 GSM8K, MATH-500, HumanEval, MBPP 등 reasoning benchmark에서 진행된다. JustGRPO는 diffusion-specific RL adaptation을 쓰는 방법들과 비교해 단순하지만 강한 성능을 보인다. 또한 block size를 늘려 parallel decoding을 활성화해도 성능이 유지되어, AR-style training으로 얻은 reasoning capability가 dLLM의 inference efficiency와 충돌하지 않음을 보여 준다. Training efficiency 분석에서는 JustGRPO가 ESPO보다 더 좋은 accuracy/wall-time trade-off를 보이며, top-entropy position만 probability ratio 계산에 사용하는 JustGRPO-Fast도 제시된다.

### 6. Related Work

관련 연구는 diffusion language model, order arbitrariness의 가치, diffusion language model을 위한 reinforcement learning으로 나뉜다. 논문은 기존 연구들이 arbitrary-order generation을 capability source로 보거나 이를 보존하려는 RL formulation에 집중한 반면, 본 연구는 일반 reasoning에서 그 유연성이 오히려 exploration을 방해할 수 있음을 보인다는 점에서 차별화된다.

### 7. Conclusion

저자들은 arbitrary order가 dLLM의 직관적 매력이지만, 일반 reasoning task에서는 solution coverage보다 single trajectory refinement를 선호하게 만들 수 있다고 결론낸다. 학습 중 기본적인 left-to-right order로 돌아가는 것은 logical fork의 high-entropy 성격을 유지하고 다양한 reasoning branch를 sampling하도록 돕는다. JustGRPO는 이 단순한 scaffold가 복잡한 diffusion-specific adaptation 없이도 효과적일 수 있음을 보여 준다.

## Appendix

Appendix에는 data preparation, training configuration, reward function, temperature analysis, different sampling algorithm 비교, entropy degradation 추가 결과, random order 대안 검토, general capability preservation이 포함된다. 특히 random order는 coverage를 개선하지 못하고 single-shot accuracy를 무너뜨리며, RL post-training에서도 안정적인 대안이 되지 못한다는 결과가 제시된다. 또한 MMLU, PIQA, ARC-C, HellaSwag에서 JustGRPO 이후 general non-reasoning capability가 유지되는지 확인한다.
