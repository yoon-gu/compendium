---
title: "DiffusionGemma: 4배 빠른 텍스트 생성"
date: 2026-06-10
draft: false
source_url: "https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/"
author: "Brendan O'Donoghue, Sebastian Flennerhag"
tags: ["AI", "Diffusion", "Gemma", "LLM", "Local Inference"]
summary: "Google이 텍스트 확산(text diffusion)을 활용한 실험적 오픈 모델 DiffusionGemma를 공개했다. 26B MoE 구조와 병렬 디코딩으로 전용 GPU에서 최대 4배 빠른 텍스트 생성을 노리지만, 품질과 클라우드 서빙 비용 측면에서는 표준 Gemma 4와 다른 트레이드오프를 갖는다."
---

> **원문:** [DiffusionGemma: 4x faster text generation](https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/) — Brendan O'Donoghue, Sebastian Flennerhag, 2026년 6월 10일
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다.

![DiffusionGemma hero image](https://storage.googleapis.com/gweb-uniblog-publish-prod/images/HeroVisual.width-1200.format-webp.webp)

Google의 최신 오픈 실험 모델은 전용 GPU에서 최대 4배 빠른 추론을 제공하며, 속도가 중요한 상호작용형 로컬 워크플로를 탐색할 수 있는 길을 연다.

오늘 Google은 텍스트 확산(text diffusion)을 탐구하는 실험적 오픈 모델 DiffusionGemma를 소개한다. 텍스트 확산은 텍스트 생성을 매우 빠르게 수행하는 접근법이다. Apache 2.0 라이선스로 공개된 이 26B Mixture of Experts(MoE) 모델은 일반적인 자기회귀 대규모 언어 모델(autoregressive Large Language Models, LLMs)의 순차적 토큰별 처리 방식을 넘어선다. 대신 텍스트 블록 전체를 동시에 생성하여 GPU에서 최대 4배 빠른 텍스트 생성을 제공한다.

![Intelligence vs Latency](https://storage.googleapis.com/gweb-uniblog-publish-prod/images/updated-Intelligence_vs_Latency_.width-1000.format-webp.webp)

DiffusionGemma는 Gemma 4 제품군의 업계 선도적인 파라미터당 지능(intelligence-per-parameter)과 최첨단 [Gemini Diffusion 연구](https://deepmind.google/models/gemini-diffusion/)를 기반으로 구축되었으며, 생성 속도를 극대화하도록 설계된 새로운 diffusion head를 통합한다. 자기회귀 Gemma 4 모델이 여전히 고품질 프로덕션 출력의 표준인 반면, DiffusionGemma는 인라인 편집, 빠른 반복, 비선형 텍스트 구조 생성처럼 속도가 중요한 상호작용형 로컬 워크플로를 탐색하는 연구자와 개발자를 위해 설계되었다.

## 개발자를 위한 새로운 가치 열기

실시간 상호작용형 AI 애플리케이션을 만드는 개발자들은 로컬 추론(local inference)의 지연 시간 병목 때문에 자주 어려움을 겪는다. DiffusionGemma는 몇 가지 핵심 트레이드오프와 함께 이 문제를 직접 겨냥한다.

- 매우 빠른 추론: 디코드 병목을 메모리 대역폭에서 계산으로 옮김으로써 DiffusionGemma는 전용 GPU에서 최대 4배 빠른 토큰 출력을 생성한다. 단일 NVIDIA H100에서는 초당 1000개 이상의 토큰, NVIDIA GeForce RTX 5090에서는 초당 700개 이상의 토큰을 생성한다.[^1]
- 접근 가능한 하드웨어 풋프린트: 전체 26B Mixture of Experts(MoE) 모델이지만 추론 중에는 3.8B 파라미터만 활성화되므로, 양자화하면 고급 소비자용 전용 GPU의 18GB VRAM 한계 안에 충분히 들어간다.
- 양방향 어텐션(bi-directional attention): 각 forward pass에서 256개 토큰을 병렬로 생성하기 때문에 모든 토큰이 다른 모든 토큰을 볼 수 있다. 이는 인라인 편집, 코드 채우기(code infilling), 아미노산 서열, 수학적 그래프처럼 비선형적인 영역에서 큰 장점을 제공한다.
- 지능적인 자기 수정: 모델은 자신의 출력을 반복적으로 정제하며, 텍스트 블록 전체를 한 번에 평가해 실시간으로 오류를 고칠 수 있다.
- 실험적 상태와 프로덕션 권장 사항: DiffusionGemma는 속도와 병렬 레이아웃 생성을 우선하므로 전체 출력 품질은 표준 Gemma 4보다 낮다. 최대 품질이 필요한 애플리케이션에는 표준 Gemma 4 배포를 권장한다.

![DiffusionGemma Benchmark](https://storage.googleapis.com/gweb-uniblog-publish-prod/images/diffusiongemma__benchmark__bar_l.width-1000.format-webp.webp)

특정 과제에서는 fine-tuning으로 DiffusionGemma의 성능을 개선할 수 있다. 아래 예시에서 [Unsloth](https://unsloth.ai/docs/models/diffusiongemma)는 DiffusionGemma를 스도쿠 풀이에 맞게 fine-tuning했다. 스도쿠는 각 토큰이 미래 토큰에 의존하기 때문에 자기회귀 모델이 어려워하는 과제다. DiffusionGemma의 양방향 어텐션은 이를 훨씬 쉽게 만든다.

![Fine-tuned DiffusionGemma solving Sudoku.](https://storage.googleapis.com/gweb-uniblog-publish-prod/original_images/sudoku_before_after11.gif)

*Fine-tuned DiffusionGemma가 스도쿠를 푸는 모습.*

## 왜 텍스트에 확산을 쓰는가?

AI 연구 커뮤니티는 수년 동안 확산 기반 텍스트 생성(diffusion-based text generation)을 탐구해 왔지만, 이를 대형 모델에 적용하는 일은 계속 어려운 과제였다. DiffusionGemma는 모델이 하드웨어를 사용하는 방식을 바꾸어 이 상황을 전환한다.

### 전통적 모델의 트레이드오프

대부분의 언어 모델은 타자기처럼 작동한다. 왼쪽에서 오른쪽으로 한 번에 한 토큰씩 생성한다. 클라우드에서는 서버가 수천 개의 사용자 요청을 함께 배치 처리해 하드웨어 부하를 나눌 수 있으므로 이 방식이 효율적이다. 하지만 단일 사용자를 위해 로컬에서 실행할 때는 이 단어별 처리 방식이 전용 GPU나 TPU를 충분히 활용하지 못하게 만든다. 하드웨어는 대부분의 시간을 다음 “키 입력”을 기다리며 보낸다.

DiffusionGemma는 이 비효율을 뒤집는다. 단어를 순차적으로 예측하는 대신 256토큰짜리 문단 전체를 동시에 초안으로 만든다. 컴퓨터의 프로세서에 한 번에 더 큰 작업 덩어리를 주기 때문에 DiffusionGemma는 하드웨어를 최대한 활용한다. 모델 추론을 하나의 순차적 타자기에서 텍스트 블록 전체를 동시에 찍어내는 거대한 인쇄기로 업그레이드하는 셈이다.

<video controls autoplay loop muted playsinline preload="metadata" title="Hugging Face DiffusionGemma text-to-3D SVG demo">
  <source src="https://storage.googleapis.com/gweb-uniblog-publish-prod/original_videos/dgemma_faster.mp4" type="video/mp4">
  DiffusionGemma text-to-3D SVG demo video: https://storage.googleapis.com/gweb-uniblog-publish-prod/original_videos/dgemma_faster.mp4
</video>

*Hugging Face가 만든 DiffusionGemma text-to-3D SVG 데모. 단계별 생성 과정.*

이는 DiffusionGemma의 속도 향상이 로컬 및 낮은 동시성(low-concurrency) 추론을 위해 설계되었음을 뜻한다. 높은 QPS 클라우드 서빙에서는 자기회귀 모델을 배포해 계산 자원을 효율적으로 포화시킬 수 있으므로, DiffusionGemma의 병렬 디코딩은 수익이 줄어들며 더 높은 서빙 비용으로 이어질 수 있다. 처리량 이점은 단일 가속기에서 낮거나 중간 정도의 batch size를 사용할 때 가장 강하다.

### 텍스트 확산은 어떻게 작동하는가

AI 이미지 생성기가 [시각적 노이즈에서 시작해 반복적으로 정제](https://research.google/blog/on-device-diffusion-plugins-for-conditioned-text-to-image-generation/)하여 선명한 그림을 만드는 것과 비슷하게, DiffusionGemma는 이 방식을 텍스트에 적용한다.

1. 캔버스: 모델은 무작위 placeholder token으로 이루어진 캔버스에서 시작한다.
2. 반복적 정제: 모델은 여러 번 통과하면서 올바른 토큰을 고정하고, 이를 문맥 단서로 사용해 나머지를 정제한다.
3. 최종 다듬기: 텍스트는 고품질 출력으로 수렴한다.

<video controls autoplay loop muted playsinline preload="metadata" title="DiffusionGemma Process">
  <source src="https://storage.googleapis.com/gweb-uniblog-publish-prod/original_videos/Diffusion_Process_3_1.mp4" type="video/mp4">
  DiffusionGemma diffusion process video: https://storage.googleapis.com/gweb-uniblog-publish-prod/original_videos/Diffusion_Process_3_1.mp4
</video>

모델이 생성 중에 문단 전체를 처리할 수 있기 때문에, 복잡한 Markdown formatting을 완벽하게 닫거나 거의 실시간으로 코드를 생성하고 렌더링하는 것처럼 새로운 모델 행동 패턴이 가능해진다.

### 오늘 시작하기

- 가중치 다운로드: 허용적인 Apache 2.0 라이선스로 공개된 실험 모델 가중치를 지금 Hugging Face에서 사용할 수 있다.
- 통합하고 배우기: [DiffusionGemma developer guide](https://developers.googleblog.com/en/diffusiongemma-the-developer-guide)에서 더 알아볼 수 있다. 내부 동작을 깊이 이해하려면 [A Visual Guide to DiffusionGemma](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-diffusiongemma)를 참고할 수 있다.
- 선호하는 개발 도구 사용: [MLX](https://huggingface.co/collections/mlx-community/diffusiongemma), [vLLM](https://vllm-project.github.io/2026/06/10/diffusion-gemma)([Red Hat](https://huggingface.co/collections/RedHatAI/diffusiongemma-26b-a4b-it)이 지원하는 통합 포함), [Hugging Face Transformers](https://huggingface.co/google/diffusiongemma-26B-A4B-it)를 사용해 모델을 효율적으로 서빙할 수 있다. 빠른 실험을 위해 Google은 조합 가능성을 위해 설계된 모듈형 JAX toolbox인 [Hackable Diffusion](https://github.com/google/hackable_diffusion)을 이용한 fine-tuning tutorial도 공개한다. [Unsloth](https://unsloth.ai/docs/models/diffusiongemma)와 NVIDIA [NeMo](https://github.com/NVIDIA-NeMo/Automodel/blob/main/docs/guides/dllm/diffusiongemma.md)로 fine-tuning을 탐색할 수도 있다. 또한 llama.cpp의 공식 지원도 곧 제공될 예정이다.
- 최적화된 성능 경험: Google은 [NVIDIA](https://blogs.nvidia.com/blog/rtx-ai-garage-local-gemma-diffusion)와 협력해 하드웨어 스택 전반에서 최적화했다. 이를 통해 소비자 환경에서는 GeForce RTX 5090 및 4090 GPU용 양자화를 제공하고, 엔터프라이즈 시스템에서는 고급 NVFP4 kernel을 사용하는 Hopper 및 Blackwell에서 고성능을 보장한다. 여기에는 로컬 desk-side 배포를 위한 NVIDIA DGX Spark와 DGX Station, AI 전문가를 위한 RTX PRO도 포함된다. NVFP4(4-bit floating-point) 네이티브 지원은 계산 처리량을 가속해 거의 손실 없는 정확도로 더 빠르게 모델을 실행할 수 있게 한다.
- 원하는 방식으로 시도: 데스크톱 전용 GPU에서 실행하거나, [Gemini Enterprise Agent Platform Model Garden](https://console.cloud.google.com/agent-platform/publishers/google/model-garden/diffusiongemma) 또는 [NVIDIA NIM](https://catalog.ngc.nvidia.com/orgs/nim/teams/google/containers/diffusiongemma-26b-a4b-it?version=latest)을 통해 클라우드에서 실행할 수 있다.

[^1]: 참고: 이 속도 향상은 가속기의 높은 산술 집약도(arithmetic intensity)를 활용하는 데 의존하므로, 추론 중 계산보다 메모리 대역폭에 묶이는 경우가 많은 Apple Silicon Mac 같은 unified-memory architecture에서는 Gemma 4 같은 자기회귀 모델 대비 같은 가속을 보지 못할 수 있다.
