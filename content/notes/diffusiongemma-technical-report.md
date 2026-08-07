---
title: "DiffusionGemma Technical Report 요약"
date: 2026-08-07
draft: false
source_url: "https://arxiv.org/abs/2608.00146"
author: "DiffusionGemma Team, Google DeepMind"
tags: ["AI", "LLM", "Diffusion", "Gemma", "Inference", "Reasoning"]
summary: "DiffusionGemma는 Gemma 4를 discrete diffusion으로 fine-tuning해 256-token canvas를 병렬 정제하는 초고속 text generation 모델이다. 단일 H100에서 약 1,500 TPS를 목표로 하며, SFT와 sampler distillation + reinforcement learning의 2단계 recipe를 사용한다."
---

> **원문:** [DiffusionGemma Technical Report](https://arxiv.org/abs/2608.00146) — DiffusionGemma Team, Google DeepMind, arXiv 2608.00146

## 한 줄 요약

DiffusionGemma는 autoregressive decoding의 순차 병목을 피하기 위해, 256개 token block을 병렬로 denoise하는 discrete diffusion 방식의 Gemma 계열 언어 모델이다.

## 핵심 포인트

- Gemma 4 26B A4B MoE를 출발점으로 삼아 처음부터 pretraining하지 않고 diffusion fine-tuning으로 전환한다.
- 2단계 학습 파이프라인은 SFT로 양방향 denoising을 학습한 뒤, sampler distillation과 reinforcement learning으로 적은 step 체제에서의 품질과 속도를 함께 끌어올린다.
- 저자들은 단일 NVIDIA H100에서 약 1,500 TPS, forward pass당 약 20 token 수준의 throughput을 보고하며, low-batch serving에서 큰 이점을 주장한다.
- diffusion 모드로 바뀐 뒤에도 AR decoding 능력을 일부 유지해, latency 제약에 따라 hybrid routing 가능성을 남긴다.

## 링크

- 논문 페이지: [/papers/diffusiongemma-technical-report/](/compendium/papers/diffusiongemma-technical-report/)
- 한국어 PDF: [/compendium/papers/diffusiongemma-technical-report.pdf](/compendium/papers/diffusiongemma-technical-report.pdf)
- arXiv 원문 PDF: [/compendium/papers/diffusiongemma-technical-report-original.pdf](/compendium/papers/diffusiongemma-technical-report-original.pdf)
