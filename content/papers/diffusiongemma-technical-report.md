---
title: "DiffusionGemma Technical Report"
date: 2026-08-07
draft: false
math: true
source_url: "https://arxiv.org/abs/2608.00146"
author: "DiffusionGemma Team, Google DeepMind"
tags: ["AI", "LLM", "Diffusion", "Gemma", "Inference", "Reasoning"]
summary: "DiffusionGemma는 Gemma 4를 discrete diffusion으로 전환한 open-weight text generation 모델이다. 본 entry는 구조 보존형 한국어 TeX/PDF 번역본의 진입점이며, 한국어 PDF를 canonical 번역 자산으로 제공한다."
---

짧은 요약은 [/notes/diffusiongemma-technical-report/](/compendium/notes/diffusiongemma-technical-report/)에서 볼 수 있다.

> **원문:** [DiffusionGemma Technical Report](https://arxiv.org/abs/2608.00146) — DiffusionGemma Team, Google DeepMind, arXiv 2608.00146
>
> 이 페이지는 원문 LaTeX 구조를 보존한 한국어 번역본의 entry point다. 한국어 PDF를 canonical 번역 자산으로 제공하며, 원문 PDF도 함께 링크한다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/diffusiongemma-technical-report.pdf)
- [arXiv 원문 PDF](/compendium/papers/diffusiongemma-technical-report-original.pdf)

## 초록

DiffusionGemma는 discrete diffusion을 이용해 텍스트를 고속으로 생성하는 experimental open-weight language model이다. token을 왼쪽에서 오른쪽으로 하나씩 생성하는 대신, 256-token canvas를 병렬로 반복 정제해 autoregressive decoding의 순차 병목을 피한다. 저자들은 Gemma 4 MoE를 출발점으로 사용하는 2단계 학습 파이프라인을 제안하며, SFT로 양방향 denoising을 학습한 뒤 sampler distillation과 reinforcement learning으로 few-step regime의 품질과 inference 효율을 함께 개선한다. 보고서의 핵심 주장은, DiffusionGemma가 생성 속도와 모델 역량 사이에서 새로운 Pareto frontier를 열고, single H100 기준 약 1,500 TPS 수준의 throughput을 제공한다는 것이다.

## 번역본 안내

이 번역본은 `papers-tex/diffusiongemma-technical-report/`의 XeLaTeX + kotex 소스를 바탕으로 생성했다. figures, tables, equations, algorithms, labels, refs, cites, bibliography hook, appendix 구조는 원문 LaTeX를 기준으로 유지했다.

## 원문 링크

- arXiv abs: <https://arxiv.org/abs/2608.00146>
- arXiv PDF: <https://arxiv.org/pdf/2608.00146>
