---
title: "블록 디퓨전 요약: 자기회귀와 디퓨전 언어모델 사이를 보간하기"
date: 2026-05-10
draft: false
source_url: "https://arxiv.org/abs/2503.09573"
author: "Arriola, Gokaslan, Chiu, Yang, Qi, Han, Sahoo, Kuleshov (Cornell · Stanford · Cohere)"
tags: ["AI", "NLP", "디퓨전", "디퓨전 언어모델", "자기회귀", "블록 디퓨전", "ICLR 2025"]
summary: "BD3-LM은 블록 단위에서 자기회귀, 블록 안에서는 마스킹 디퓨전을 수행하여 두 패러다임을 보간한다. 가변 길이 생성과 KV 캐싱을 동시에 살리면서, 데이터 기반의 클립된 노이즈 스케줄로 그래디언트 분산을 줄여 디퓨전 LM의 perplexity SOTA를 새로 세웠다."
---

> 이 글은 [블록 디퓨전 한국어 번역본](/compendium/papers/interpolating-ar-diffusion-lm/)의 짧은 요약입니다. 라인바이라인 번역과 PDF 링크는 그쪽을 참고하세요.

## 한 문장 요약

**BD3-LM**(Block Discrete Denoising Diffusion Language Models)은 블록 사이에는 자기회귀(autoregressive, AR), 블록 안에서는 이산 마스킹 디퓨전(discrete masked diffusion)을 적용해 두 패러다임을 *보간*하는 언어모델이다. 가변 길이 생성과 KV 캐싱을 동시에 지원하면서, 데이터 기반(data-driven) 클립 노이즈 스케줄(clipped noise schedule)로 그래디언트 분산을 낮춰 디퓨전 LM의 perplexity 최첨단을 갱신했다.

## 핵심 아이디어

1. **블록 단위 분해**: 길이 $L$ 시퀀스를 $B = L/L'$ 개의 블록으로 묶어 우도를 $\log p_\theta(\mathbf{x}) = \sum_{b=1}^{B} \log p_\theta(\mathbf{x}^b \mid \mathbf{x}^{<b})$ 로 분해. 각 조건부는 블록 길이 $L'$에 대한 마스킹 디퓨전(MDLM)으로 모델링.
2. **두 극단을 잇는 보간**: $L'=1$이면 사실상 AR, $L'=L$이면 표준 마스킹 디퓨전. 가운데 영역에서 *AR의 정확도와 디퓨전의 병렬성*을 동시에 누림.
3. **벡터화 학습 알고리즘**: 노이즈 토큰 시퀀스 $\mathbf{x}_\text{noisy}$ 와 클린 시퀀스 $\mathbf{x}$를 이어 붙여 한 번의 forward에서 손실을 계산. 노이즈 토큰은 같은 블록 내 노이즈 토큰 + 이전 블록의 클린 토큰까지만 어텐션하도록 *블록-인과(block-causal) 마스크*를 설계 (FlashAttention/FlexAttention과 호환).
4. **KV 캐싱 + 가변 길이**: 디퓨전 LM이 갖지 못했던 두 가지를 동시에 회복. 이전 블록의 K/V를 재사용해 추론을 빠르게 하고, EOS가 나올 때까지 블록을 추가해 학습 컨텍스트보다 긴 시퀀스를 생성.
5. **데이터 기반 클립 스케줄**: 마스킹률 $1-\alpha_t$를 $\mathcal{U}[\beta, \omega]$로 잘라내 그래디언트 분산이 최소가 되도록 학습 중 그리드 서치로 $\beta, \omega$를 적응적으로 갱신. 작은 블록일수록 *무거운* 마스킹, 큰 블록일수록 *가벼운* 마스킹이 최적.

## 왜 분산이 중요한가 (단일 토큰 케이스 스터디)

$L'=1$ 인 BD3-LM과 AR은 *기댓값상으로는 같은 목적함수*인데, LM1B에서 학습하면 perplexity가 ~2점 벌어진다. 원인은 디퓨전 NELBO가 *마스킹된 토큰만*으로 손실을 계산하기 때문(평균 50% 마스킹 → AR 대비 토큰 절반). 마스킹 확률을 1로 강제(모든 토큰 마스킹)하면 NELBO가 AR NLL과 *완전히* 같아지고 perplexity가 22.88로 일치 — 두 패러다임의 갭이 *목적함수 차이가 아니라 분산 차이*에서 온다는 강력한 증거.

## 주요 결과

- **LM1B perplexity**: BD3-LM $L'=4$ ≤ **28.23** (이전 디퓨전 SOTA MDLM 31.78 대비 약 11% 개선). AR Transformer 22.83.
- **OpenWebText**: BD3-LM $L'=4$ ≤ **20.73** (MDLM 22.98). AR 17.54.
- **제로샷**: OWT 학습 모델로 PTB·Wikitext·LM1B·Lambada·AG News·Pubmed·Arxiv 평가. Wikitext·LM1B·AG News·Pubmed에서 디퓨전 SOTA, **Pubmed에서는 AR마저 능가** (42.52 vs 48.59).
- **가변 길이 생성**: SEDD가 학습 컨텍스트(1024) 안에 갇히는 동안, BD3-LM $L'=16$은 최대 **9982토큰**까지 생성 (≈ 10배). OWT 훈련셋의 중앙값(717토큰)에 더 가까움.
- **생성 perplexity** (GPT2-Large 기준): $L=2048$에서 BD3-LM $L'=4$ **23.6** vs MDLM 41.3 vs SSD-LM 35.3 (그것도 SSD-LM은 80K NFE, BD3-LM은 2K NFE).

## 노이즈 스케줄 절제

| $L'$ | 최적 클립 | PPL | NELBO 분산 |
|---|---|---|---|
| 4  | $\mathcal{U}[0.45, 0.95]$ (무거운 마스킹) | **29.21** | **6.24** |
| 4  | 선형 $\mathcal{U}[0,1]$ | 30.18 | 23.45 |
| 16 | $\mathcal{U}[0.3, 0.8]$ (가벼운 마스킹) | **31.12** | **3.58** |
| 16 | 선형 $\mathcal{U}[0,1]$ | 31.72 | 7.62 |

분산과 perplexity가 거의 단조 비례하며, 블록이 작을수록 더 많이 마스킹해야 학습 신호가 살아남는다는 직관과 일치.

## 내가 흥미롭게 본 지점

- "perplexity 갭은 목적함수가 아니라 *그래디언트 추정량의 분산* 때문" 이라는 진단을 *equivalence in expectation* 증명과 변동성 측정으로 깔끔하게 분리한 점. 디퓨전 모델 학습이 본질적으로 *Monte Carlo 적분의 노이즈에 시달린다*는 사실을 드러내는 시각.
- 마스킹률을 *극단(0이나 1 부근)에서 잘라낸다* 는 trick — 너무 적게 마스킹하면 문제가 trivial해 그래디언트가 0에 수렴하고, 너무 많이 마스킹하면 모델이 단지 *주변 분포*를 외워버림. 두 극단 다 학습 신호를 죽인다는 직관이 명쾌.
- 한 forward에서 *clean+noisy* 를 같이 흘려 보내는 어텐션 마스크 설계 — 두 번 forward 도는 단순 구현보다 20-25% 빠르며, FlashAttention 같은 효율 커널을 그대로 활용.
- AR ↔ 디퓨전을 한쪽이 아닌 *연속체*로 본다는 관점이 결정적: 블록 크기 $L'$ 가 *제어 가능성, 속도, 정확도* 사이의 다이얼이 된다.

## 더 읽기

- 전체 한국어 번역본 (모든 절·표·부록 정리): [/papers/interpolating-ar-diffusion-lm/](/compendium/papers/interpolating-ar-diffusion-lm/)
- arxiv 원문 PDF: [interpolating-ar-diffusion-lm-original.pdf](/compendium/papers/interpolating-ar-diffusion-lm-original.pdf)
- 원문: [arxiv 2503.09573](https://arxiv.org/abs/2503.09573) — Arriola et al., ICLR 2025
- 프로젝트 페이지: [m-arriola.com/bd3lms](https://m-arriola.com/bd3lms)
