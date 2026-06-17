---
title: "에이전트 코딩을 위한 로컬 LLM 사용하기"
date: 2026-06-17
draft: false
math: true
source_url: "https://blog.alexewerlof.com/p/local-llms-for-agentic-coding"
author: "Alex Ewerlöf"
tags: ["AI", "LLM", "Agentic Coding", "Local Models", "Copilot"]
summary: "GitHub Copilot의 사용량 기반 과금 전환 이후, 로컬 LLM을 에이전트 코딩 워크플로에 연결하는 실무 절차를 설명한다. LM Studio로 Gemma 계열 모델을 실행하고 VS Code Copilot, Pi, OpenRouter 대안을 설정하는 과정과 하드웨어·컨텍스트 윈도·비용·프라이버시의 트레이드오프를 다룬다."
---

> **원문:** [Using local LLMs for agentic coding](https://blog.alexewerlof.com/p/local-llms-for-agentic-coding) — Alex Ewerlöf, 2026년 6월 4일
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다.

## 요약

GitHub Copilot이 사용량 기반 과금으로 옮겨가면서, 저자는 로컬 모델(local model)을 에이전트 코딩(agentic coding)의 비용·프라이버시 대안으로 제시한다. 핵심 주장은 로컬 모델이 Claude, GPT, Gemini 같은 최첨단 클라우드 모델보다 원시 성능은 낮더라도, 좋은 하네스(harness), 도구 호출, 테스트, 린트, 명확한 컨텍스트 압축 규칙을 결합하면 실무 코딩 워크플로에서 충분히 유용해질 수 있다는 것이다.

글은 Gemma 4 계열 모델을 중심으로 LM Studio에서 모델을 찾고, 컨텍스트 윈도와 KV cache quantization을 조정하고, OpenAI-compatible API 서버를 열어 VS Code Copilot과 Pi에 연결하는 과정을 단계별로 설명한다. 마지막으로 하드웨어가 부족한 독자를 위해 OpenRouter의 free models를 쓰는 우회 경로와, 비용 상한·guardrail 설정의 필요성을 다룬다.

4일 전 GitHub가 [사용량 기반 과금](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)으로 전환했다. Microsoft가 자선사업을 해서 세계 최대 기업 중 하나가 된 것은 아니니, 때가 되긴 했다!

다행히도 우리는 여기에 순응할 필요가 없다. 로컬 모델(local models)이 상당히 발전했기 때문이다. 이 글에서는 다음을 공유하겠다:

1. 로컬 모델을 실행하는 방법(그리고 무료 클라우드 기반 대안)
2. 에이전트(Copilot 및 Pi)를 구성하는 방법
3. 로컬 모델의 힘을 보여주는 간단한 데모 앱

***면책: 이 글 전체에는 AI가 사용되지 않았다.***

## 간단한 소개

나는 3년 전부터 로컬 모델을 전문적으로 다뤄왔다. 주된 이유는 비용(AI 기반 앱 개발)이었지만, 프라이버시와 하드웨어에 대한 개인적 집착도 있었다. 더 작은 모델을 길들이는 것은 훨씬 어렵지만, 일단 숙달하면 더 큰 모델을 더 잘 활용할 수 있다.

NVIDIA RTX, Apple M4, AMD ROCm을 거치며 Linux, Mac, Windows에서 Llama.cpp, Ollama, LM Studio, Jan을 써봤다. 그래서 지난 3년간 배운 내용을 공유해 여러분의 여정을 줄이는 데 도움이 될 수 있겠다고 생각했다.

참고: 이미 LLM을 로컬에서 실행하고, 이를 코딩 도구에 연결해 괜찮은 결과를 얻는 방법을 알고 있다면, **이 글은 당신을 위한 글이 아니다**. 흥미로울 수 있는 AI 관련 다른 글들도 있다.

## 가격 인상

GitHub는 예전에는 크레딧 모델로 운영했고, 무료 모델도 일부 있었다. 이제는 그 무료 모델조차 더 이상 무료가 아니다:

![](https://substack-post-media.s3.amazonaws.com/public/images/36e726b3-76f3-4c88-a662-f1618925d732_745x500.png)

*출처: GitHub*

GitHub는 [AI 크레딧 사용량을 최적화하는 방법](https://code.visualstudio.com/docs/copilot/guides/optimize-usage)에 대한 몇 가지 포인트를 공유했다.

가격 인상은 GitHub에서 더 뚜렷하게 보인다. GitHub는 토큰 리셀러이기 때문이다. 플래그십 모델들은 상당한 가격 인상과 함께 도입되지만, 성능은 같은 속도로 개선되지 않는다.

Google Flash 3.5는 Flash 2.5보다 3배 이상 비싸다:

![](https://substack-post-media.s3.amazonaws.com/public/images/3468eb96-63f3-4671-a924-aa7041360135_1216x598.png)

*출처: OpenRouter*

그렇다면 3배 더 비싼데, 얼마나 더 나을까? Google의 자체 벤치마크는 다음과 같다:

![](https://substack-post-media.s3.amazonaws.com/public/images/752df7e6-bb40-4d82-9049-6963cc2b0715_787x815.png)

*출처: Google*

GPT 5.5는 5보다 3배 이상 비싸다:

![](https://substack-post-media.s3.amazonaws.com/public/images/872dc4b5-9b87-4874-8a62-54341044d7fa_1215x559.png)

*출처: OpenRouter*

그럼 Claude는? Claude는 이미 너무 비쌌기 때문에 오히려 가격을 낮췄다! 😉

![](https://substack-post-media.s3.amazonaws.com/public/images/78c1fe5f-cf7c-4f59-8132-d299acf71f40_849x245.png)

*출처: Anthropic*

## 로컬 모델?

로컬 모델이 Claude, GPT, Gemini 같은 SOTA(state of the art, 최첨단) 모델의 성능에 미치지 못하는 것은 사실이다. 하지만 몇 가지 뉘앙스가 있다:

- 가격/성능 비율: 최첨단 클라우드 모델은 성능 향상 대비 비용이 기하급수적으로 더 비싸다.
- 결정론적 하네스(deterministic harness): 더 나은 도구, 지시문 등을 사용하면 더 약한 모델의 품질을 최대 6배까지 향상시킬 수 있다. 클라우드 모델은 원시 형태(raw form)에서는 로컬 모델보다 뛰어나지만, 도구화(tooling), 예컨대 AI 하네스를 적용하면 상당 부분 보완할 수 있다.
- 벤치마크의 오류: 벤치마크는 속일 수 있다. 모델처럼 복잡한 것을 하나의 스칼라 숫자로 정량화하는 것은 극도로 어렵다. 벤치마크는 예상 작업과 일반적인 요구사항을 대표할 수는 있지만, 그것들이 당신의 작업이나 요구사항은 아니다. 게다가 모든 AI 연구소는 자기 모델이 좋아 보이는 벤치마크에 집중한다. 모델을 현실적으로 평가하려면 자신의 워크로드에서 직접 시험해봐야 한다.
- 지정학적 효과: 미국 AI 연구소들이 무료로 공개하려는 것은 그들의 최고 결과물이 아니다. [gpt-oss-20b](https://openai.com/index/introducing-gpt-oss/)는 너무 오래됐다. Anthropic은 오픈 웨이트(open weight)를 아무것도 공개하지 않았다. [Gemma 4](https://ai.google.dev/gemma/docs/core)가 이 리그에서 유일하게 진지한 모델이다. 하지만 중국 연구소들에는 감사해야 한다. 그들은 미국의 투자와 AI에 대한 대규모 베팅을 무력화하려는 노력 속에서 Qwen, Kimi, GLM 등 매우 유능한 모델들을 공개하고 있다.

![](https://substack-post-media.s3.amazonaws.com/public/images/756c4a91-b01d-4a32-b8b6-d897d9d9f6e3_1000x545.png)

그리고 여기에는 brain rot 현상도 있다:

- 더 약한 모델은 두뇌에 더 좋다. 그들의 지능 부족을 보완해야 하고, 더 많이 관여해야 하기 때문이다. 다른 사람들이 차를 탈 때 자전거를 타는 것과 조금 비슷하다. 더 느린가? 그렇다. 건강에 더 좋은가? 그것도 그렇다! 지식 노동에서 두뇌는 좋은 상태를 유지해야 할 가장 중요한 기관이다. 때로는 “느린 것이 빠른 것”이다.
- 우리의 목표는 자동화를 극대화하고 사고를 기계에 떠넘기는 것이 아니다. 그것은 우리의 일이 자동화 가능하다는 노골적인 고백이 될 것이다. 상사가 시켰다는 이유만으로 단기 속도를 위해 미래의 관련성을 희생하지 마라.
- 더 약한 모델을 길들이는 데 도움이 되는 많은 방법은 더 큰 모델에도 적용된다. 더 약한 모델을 길들이는 것은 **하드 모드로 플레이하는 것**과 같다. 그 방법을 알게 되면, 큰 도구들을 훨씬 더 효과적으로 사용할 수 있다. 이제 이런 모델들은 범용 상품(commodity)이 되었다.
- 또한 최첨단 모델이 당신의 영향력을 100배 키워준다고 생각한다면 다시 생각해보라. 확실히 당신의 *산출물*은 늘려주지만, *영향력*은 언제나 *가치*와 연결되어 있고, 그 가치는 인간에게서 나온다.
- 영향력을 AI에 떠넘기는 것은 위험한 일이지만, 동시에 적은 노력으로도 가능하다. 모두가 하는 일을 그대로 한다면, 평균적인 결과를 얻게 될 것이다.

윤리는 이쯤 하자! 이제 엔지니어링 이야기로 들어가자.

## 어떤 모델?

무엇을 하려는지에 따라 모델은 많다. 코딩의 경우, 중국 모델들이 대체로 [Hugging Face 리더보드](https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard) 상위권에 있다.

이 분야는 매우 빠르게 진화하고 있으므로 너무 단정적으로 말하는 것은 조심스럽지만, Qwen, DeepSeek, Kimi, Llama, Gemma 등이 있다.

### Gemma 4

나는 [Gemma 4](https://deepmind.google/models/gemma/gemma-4/) 모델들이 꽤 좋다고 본다.

Gemma 4에는 여러 버전이 있다:

- E2B: “E”는 edge를 의미한다. 이는 2B 파라미터 버전으로, 대부분의 하드웨어에서 실행할 수 있을 만큼 작지만 환각(hallucination)을 일으키거나 작업을 완료하지 않고 그냥 포기할 위험이 더 높다.
- E4B: E2B와 같지만 크기가 두 배다. 유용성이 작업과 환경에 따라 달라지기 때문에, 두 배 더 유용하다는 것을 증명하려고 벤치마크를 끌어오고 싶지는 않다. 다음 모델을 쓰기 전에 내가 처음 시작한 버전이 이것이다. 다운로드와 구성 비용이 더 낮으므로 E4B부터 시작하는 것을 추천한다.
- 12B: 솔직히 왜 “E”를 뺐는지는 모르겠지만, 아무튼! 이 버전은 다른 모델들이 내부에 디코더를 갖고 있는 것과 달리 이미지를 네이티브로 이해한다는 점에서 꽤 독특하다. 이는 구현 세부사항이지만, 우리에게는 모델에 이미지를 보내야 할 수 있는 프론트엔드 또는 시각적 코딩에서 12B가 더 빠르다는 뜻이다. 네이티브 오디오 지원도 있지만, 코딩 워크로드에는 중요하지 않다.
- 26B A4B: 겉보기에 무작위인 영숫자 이름을 읽는 법을 배우면, 사실 이 모델이 내가 가장 좋아하는 모델이다. 26B 파라미터를 갖고 있지만, 특정 시점에 활성화되는 것은 4B뿐이다. 일반 E4B 버전보다 똑똑하지만, 여전히 8-12GB VRAM을 가진 일반 그래픽 카드에 들어간다. 이것이 가능한 방식은 MoE(mixture of experts, 전문가 혼합) 아키텍처다. [우리는 이전에 MoE와 MoA를 다룬 적이 있다](https://blog.alexewerlof.com/p/ai-systems-engineering-patterns). 따라서 26B는 모든 전문가를 포함하지만, 작업에 따라 그중 일부만 활성화된다.
- 31B: 이는 Google의 가장 큰 오픈 웨이트 모델이다. MoE가 아니므로 실행하려면 많은 VRAM이 필요하다. 나는 26B MoE 모델이 꽤 괜찮은 일을 해주고, 내 AMD APU로도 실행은 되지만 속도가 실사용 불가능한 수준(1-2 TPS)이기 때문에 이것은 시도해보지 않았다.

Gemma를 선택하려면 QAT 변형(예: E4B QAT)을 사용할 수 있다. 메모리는 덜 필요하지만 거의 같은 품질을 유지한다.

또한 Unsloth는 기본 Google 모델 위에 [추가 작업](https://unsloth.ai/docs/models/gemma-4/qat)을 해서 모델들을 더욱 효율적으로 만들었다:

![](https://substack-post-media.s3.amazonaws.com/public/images/d405031e-ac35-4522-98d7-50053c563515_789x236.png)

*출처: Unsloth*

## 로컬 모델은 어떻게 실행하나요?

글의 나머지가 전문 용어 수프처럼 보이지 않도록 먼저 언어를 정리해둘 필요가 있다.

아마 이미 아는 내용이 많을 테니 편하게 훑어보자:

- Deep learning: 10년 전까지만 해도 NN(neural network)은 몇 개의 레이어로 제한되어 있었다. Deep learning은 의미 있는 개선을 얻으면서 그 레이어들을 효율적으로 늘리는 것에 관한 분야다. 여러분의 머신에서 실행하려고 모델을 다운로드할 때는 neural network의 weights와 아키텍처에 따라 필요한 몇 가지 추가 요소를 다운로드하는 것이다.
- Attention mechanism: Turing test의 기본 버전을 통과할 수 있는 language model을 여는 핵심이었다. 기본적으로 대화가 컴퓨터가 생성한 것인지 인간에게서 나온 것인지 구분하기 어렵다는 뜻이다.
- LLM: 우리가 관심 있는 “AI”의 하위 집합이다. 컴퓨터 코드를 생성할 수 있기 때문이다. 이미지를 생성하거나 비디오를 생성하는 등 다른 AI도 있다. 하지만 우리는 코드를 로컬에서 실행할 대안을 찾고 있으므로 이 글의 범위 밖이다.
- SLM: small language model은 LLM과 비슷하지만 소비자용 GPU에 들어갈 만큼 작다. 실행할 수 있는 모델은 다양하지만, [0.27B](https://developers.googleblog.com/en/introducing-gemma-3-270m/)처럼 작은 SLM도 있다. 다만 의미 있는 코딩 작업이라면 적어도 4B 모델은 실행하고 싶을 것이다. 중국 연구소들이 미국의 투자와 AI에 대한 큰 베팅을 무력화하려는 노력의 일환으로 이 요구사항을 낮춘다고 해도 놀랍지는 않겠지만, 정치 이야기는 피하도록 하겠다.
- [Hugging Face](https://huggingface.co/models?sort=trending): 모델을 위한 GitHub 같은 곳이다. GitHub가 코드를 위한 곳이라면, Hugging Face는 model weights를 담은 거대한 파일인 모델을 찾을 수 있는 곳이다. 그리고 코드에 *open source*가 있는 것처럼, 모델에는 weights가 공개적으로 접근 가능한 *open weights*가 있다. 물론 코드와 마찬가지로 모델을 어디서 어떻게 사용할 수 있는지 규정하는 라이선스가 있다.
- Inference: 새로운 token을 생성하는 과정이다. 예컨대 코드 또는 사람이 읽을 수 있는 텍스트를 만든다.
- CPU/GPU/TPU/NPU: 모델을 실행하는 하드웨어다:
  - CPU: Central Processing Unit은 전통적으로 ML(machine learning) 작업을 실행하는 데 사용되었지만, 범용적인 특성 때문에 너무 느리고 에너지 효율이 낮았다.
  - GPU: Graphics Processing Unit. [AlexNet](https://en.wikipedia.org/wiki/AlexNet) 같은 프로젝트 덕분에 사람들은 현재 세대의 AI 작업에 완벽한 대규모 행렬 연산에 GPU를 사용하기 시작했다. 이전에는 게임용 GPU로 알려졌던 NVIDIA는 갑자기 자신을 “accelerated computing의 리더”로 마케팅하기 좋은 위치에 놓이게 되었다. GPU의 맥락에서 VRAM(video random access memory)은 어떤 크기의 모델을 실행할 수 있는지를 결정하기 때문에 핵심 파라미터다.
  - TPU: Tensor Processing Unit은 행렬 연산을 위한 Google의 특수 칩이다. 더 정확히 말하면 matrix는 2D이고 tensor는 임의의 차원을 가질 수 있는 상위 집합이다. 서버급 하드웨어가 아니라면 소비자용 하드웨어에서 사용할 수 있는 TPU는 내가 알기로 없다.
  - NPU: Neural Processing Unit은 최신 컴퓨터에서 흔히 볼 수 있으며, 종종 Copilot+ 브랜딩과 함께 제공된다. 노이즈 제거 또는 배경 교체처럼 빠르고 가벼운 AI 작업을 효율적으로 처리하는 데 특화되어 있다. LLM 작업에서는 NPU 지원이 좋지 않으므로 다른 하드웨어 유형을 사용하겠다.
  - APU: Accelerated Processing Unit은 주로 AMD가 CPU+GPU 유닛을 설명하는 데 사용하는 용어다. 이 유닛은 UMA(unified memory architecture)라고 불리는 방식으로 동일한 RAM을 공유한다.
  - Apple Silicon: M1, M2 등 프로세서다. AI 작업에서 뛰어난 성능과 효율성을 보이는 Apple 자체 프로세서다. Apple Silicon 프로세서(예: M4, M5)가 있다면 일반 RAM이 CPU와 GPU 사이에서 UMA라고 불리는 방식으로 공유된다.

재미있는 관찰: 내가 이 글을 bullet point로 정확히 AI가 생성한 텍스트처럼 포맷하고 있다는 걸 알아차렸다! 😄 전부 자연스럽게 쓴 거라고 약속하지만, 내가 AI 콘텐츠를 너무 많이 사용한 걸까? 아니면 AI가 잘 포맷된 텍스트를 너무 많이 먹은 걸까?

### 요구사항

*참고: 하드웨어가 충분히 좋지 않더라도 OpenRouter에서 무료 모델을 실행하는 방법이 있다. 이 섹션은 건너뛰어도 된다.*

로컬 모델을 실행하려면 몇 가지가 필요하다:

![](https://substack-post-media.s3.amazonaws.com/public/images/b22cc99b-4c97-4149-8849-4dfacf66c642_881x833.png)

- Harness: harness의 내부 아키텍처와 기능에 대해서는 별도의 글이 있다. 이 글의 맥락에서는 VS Code Copilot, Copilot CLI 또는 Pi가 harness다. 이들은 모델(stochastic component) 주변에서 deterministic component(전통적인 코드)를 사용한다.
- Model: 보통 deep neural network weights를 담은 거대한 파일이다. 다양한 model quantization(예: Q8, Q4)이 있는데, 대략 말하면 서로 다른 이미지 해상도와 비슷하다. 그리고 runtime에 따라 서로 다른 format(예: GGUF, MLX)이 있다. 여러분의 하드웨어에 무엇이 맞는지만 알아내면 되며, LM Studio 같은 도구가 이를 더 쉽게 만들어준다.
- Runtime 또는 inference engine: 모델을 실행하고 token을 내보내는 것이다. 각자 고유한 format을 가진 몇 가지 옵션이 있다:
  - [Llama.cpp](https://github.com/ggml-org/llama.cpp): 가장 인기 있는 open source runtime이다. Llama(Meta의 open weight model)와는 아무 관련이 없다. GGUF 또는 MLX model format을 로드할 수 있다. LM Studio는 내부적으로 Llama.cpp를 사용한다.
  - [MLX](https://opensource.apple.com/projects/mlx/): Apple의 runtime이다. M1, M2 등 프로세서가 탑재된 Mac을 가지고 있다면 이것을 사용하게 된다. Apple Silicon에서 Llama.cpp를 실행할 때 내부적으로 MLX를 사용할 수 있다.
  - [ONNX Runtime](https://onnxruntime.ai/): 예를 들어 WebGPU를 사용해 브라우저에서 LLM을 실행하는 transformers.js 뒤에 있는 것이다. 하지만 모바일 기기(iOS, Android)에서도 실행할 수 있다. model format은 ONNX다.
  - [vLLM](https://vllm.ai/): UC Berkeley에서 나온 또 다른 open source 옵션이다. 주로 더 강력한 서버에서 사용되며 설정이 조금 더 어렵다.
- Model manager: 이 부분은 선택 사항이지만 순조로운 시작을 위해 강력히 추천한다. 하드웨어와 runtime을 추상화하면서 다양한 모델을 찾고, 다운로드하고, 설정하고, 로드하고, 시험해볼 수 있는 좋은 인터페이스를 제공한다. 중요한 기능은 OpenAI compatible API다. 이는 많은 AI 애플리케이션(harness 또는 model-agnostic AI application)이 사실상의 표준인 이 방식으로 동작하기 때문에 중요하다.

![](https://substack-post-media.s3.amazonaws.com/public/images/2cf3b119-e921-423e-9514-83a59d5a9aaa_1492x1145.png)

*내 Linux 노트북에서 실행 중인 LM Studio*

모델 관리를 위해 몇 가지 옵션이 있다:

- [Ollama](https://ollama.com/): terminal CLI로 시작했지만 이제는 가벼운 GUI도 있다. 다시 말하지만 Meta의 LLaMA나 Llama.cpp(runtime)와는 관련이 없다. 다만 후자인 C++ 프로젝트를 감싼 Go wrapper일 뿐이다. Open source다.
- [LM Studio](https://lmstudio.ai/): 무료이지만 **open source는 아니다**. 더 많은 부가 기능과 자체 SDK(Python/TypeScript), 그리고 로컬 모델에 고유한 측면(예: 동적으로 로드하기)을 제어할 수 있는 추가 REST API 위에 [REST API](https://lmstudio.ai/docs/developer/rest)를 제공한다.
- [Jan](https://www.jan.ai/): LM Studio와 매우 비슷한 무료이면서 open source인 대안이지만, 기능은 그만큼 풍부하지 않다.

![](https://substack-post-media.s3.amazonaws.com/public/images/7a466446-9019-4237-802b-f6cac1f0582b_1700x1256.png)

*Jan의 웹사이트*

LM Studio 같은 model manager는 때때로 최신 runtime 개발보다 뒤처질 수 있다는 점만 알아두자. 개인적으로 나는 GUI를 더 선호하는 편이라 LM Studio를 선호한다.

Model manager는 필수는 아니다. 나는 container에서 Llama.cpp를 실행하는 것으로 시작했다. Llama.cpp 역시 OpenAI-compatible API를 제공하며 자체 [web based chat interface](https://github.com/ggml-org/llama.cpp/discussions/16938)도 함께 제공한다. 커뮤니티가 이런 도구들을 발전시키면서 runtime과 model manager 사이의 경계는 흐려지고 있다.

llama.cpp 경로를 선택한다면 모델을 찾고 다운로드하는 방법은 아마 알고 있겠지만, 간단히 언급하겠다:

1. [Hugging Face](https://huggingface.co/models?sort=trending)로 가서 상단 헤더의 Models를 클릭한다.
2. 그런 다음 모델을 [GGUF](https://huggingface.co/models?library=gguf&sort=trending) format으로 필터링한다. Llama.cpp가 기대하는 것이기 때문이다. Apple Silicon에서 실행한다면 [MLX](https://huggingface.co/models?library=mlx&sort=trending)도 함께 또는 대신 선택한다.
3. 원하는 모델을 검색한다. 무엇을 원하는지 모르겠다면 계속 읽어보자.

![](https://substack-post-media.s3.amazonaws.com/public/images/9e71bcf5-0fa8-4b8c-9951-b268a89ca4f2_1002x643.png)

*Hugging Face의 model search page*

LM Studio를 사용하는 장점은 모델을 찾고 그것이 여러분의 하드웨어에 맞는지 알아내기 위해 Hugging Face로 갈 필요가 없다는 것이다. 또한 많은 모델이 미리 설정되어 제공되므로 설정을 조정하는 데 시간을 쓸 필요가 없다.

실제로 한번 살펴보자!

### 모델 선택하기

다음 지침을 따르려면 LM Studio 0.4.15+([여기에서 다운로드](https://lmstudio.ai/))가 필요하다:

![](https://substack-post-media.s3.amazonaws.com/public/images/3cc158bc-d899-43b1-a11c-1f74b5accb9a_1330x954.png)

1. 왼쪽의 Model Search 버튼을 클릭한다.
2. 원하는 모델 이름을 입력한다. 아래 내용 참고.
3. VRAM에 맞는지 확인한다. 여기에 초록색 또는 회색 텍스트가 보이면 좋지만, 빨간색은 안 된다.
4. 다운로드한다. 당연히 충분한 저장 공간과 인터넷 대역폭이 필요하다.

어떤 모델을 다운로드해야 할까? 모델은 많다. 개인적으로는 Gemma 4를 추천하지만, 그건 내가 최근에 가장 많이 사용해 봤기 때문이다.

이전에는 DeepSeek와 Llama를 사용해 봤다. 내 생각에 Gemma 4는 일반적인 작업량(예: planning, discovery)과 코드 생성 전문성 사이에서 좋은 균형을 이룬다. 또한 VS Code에서 실행하는 데 핵심적인 몇 가지 기능도 갖추고 있다:

- Tools Use: 모든 agentic workload는 bash, MCP 또는 파일 편집 같은 일반 harness 기능을 캡슐화한 tools 사용을 필요로 하므로, 이는 타협할 수 없는 요소다.
- Vision: 스크린샷을 붙여넣을 때 유용하다.
- Reasoning: 코딩 작업에 큰 장점이다.

raw model은 채팅할 때 그다지 똑똑해 보이지 않을 수 있지만, guardrails, skills, tools가 있는 harness에 넣으면 훨씬 더 많은 일을 할 수 있다.

### 서버 설정하기

Copilot이 로컬 모델을 사용하도록 구성하기 전에, 먼저 서버를 설정해야 한다. 앞서 말했듯이 [llama-server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)도 이 일을 해내지만 llama.cpp는 초보자에게 친절하지 않다. 그래서 우리는 LM Studio를 사용할 것이다:

![](https://substack-post-media.s3.amazonaws.com/public/images/8cf6a3ca-865c-458d-8109-f61668998cf6_807x475.png)

*LM Studio 서버*

1. 왼쪽 사이드바에서 “Developer” 버튼을 클릭한다.
2. 해당 토글로 서버를 시작한다.
3. 필요하다면 서버 설정을 조정한다. 흥미로운 것 몇 가지는 다음과 같다.
4. Serve on Local Network: VS Code가 실행되는 머신과 다른 머신에서 LLM을 실행하는 경우, 또는 Podman/Docker 컨테이너에서 실행하는 경우 사용한다.
5. Enable CORS: 웹 애플리케이션에서 모델에 접근하고 싶다면 사용한다. VS Code에는 필요 없지만, 기술적으로는 LLM API endpoint와 token이 필요한 어떤 앱에도 같은 서버를 사용할 수 있기 때문에 언급한다. token 얘기가 나왔으니 말인데, “Manage Tokens” 버튼에서 몇 개를 생성할 수 있다. 내 설정에서는 token을 요구하지 않지만, 다른 컴퓨터에서 접근 가능한 전용 서버를 운영한다면 추가 보안 계층으로 token을 넣고 싶을 수 있다.

넘어가기 전에, 내가 실수로 배운 몇 가지 중요한 점을 언급해야겠다.

서버를 막 시작하면 보통 아무 모델도 로드되어 있지 않다:

![](https://substack-post-media.s3.amazonaws.com/public/images/3296df07-f4ed-436f-a1b3-c8a2b0a60e62_765x98.png)

그 이유는 요청이 들어왔을 때 LM Studio가 모델을 lazy load하기 때문이다. 물론 먼저 모델을 다운로드해야 한다. 이것을 JIT(Just In Time) loading이라고 한다.

또한 더 이상 요청이 없을 때 메모리를 해제하기 전에 모델을 메모리에 얼마나 오래 유지할지도 제어할 수 있다. 이것이 TTL(Time To Live) 설정이다:

![](https://substack-post-media.s3.amazonaws.com/public/images/5d4dc970-2375-4949-83ad-f515a7e19de7_765x444.png)

**Cold start:** JIT는 모델이 로드되어 있지 않으면 첫 요청에 추가 시간이 걸린다는 뜻이다. 약 10-30초다. AWS Lambda의 cold-start와 조금 비슷하다. 모델이 로드되면 이후 요청은 더 빨라지지만, timeout이 있다면 cold-start를 감안하거나 미리 모델을 수동으로 로드해야 한다. 영향을 받는 지표는 **TTFT**(Time To First Token)다. 장점으로는, LM Studio가 요청에 포함된 모델을 동적으로 로드할 수 있다. 이런 방식으로 여러 모델을 동시에 실행하는 서버인 척할 수 있다.

**짧은 context window:** 하지만 더 중요한 함정이 있다. LM Studio가 모델을 로드할 때 일부 기본 설정을 사용한다. 그리고 이 설정들이 중요한 이유는 기본적으로 context window가 겨우 4k일 수도 있기 때문이다!!! 감을 잡기 위해 비교하자면, VS Code Copilot의 대부분 모델은 200-400k context window를 갖는다. LM Studio에서 context window를 수동으로 늘려야 한다.

클라우드 AI 세계에서 왔다면 이런 설정이 낯설 수 있으니, VS Code 설정을 이야기하기 전에 빠르게 살펴보자.

“Load” 버튼을 클릭해 다운로드한 모델 목록을 본다.

내 목록은 다음과 같다:

![](https://substack-post-media.s3.amazonaws.com/public/images/1e45454a-0f6a-4ab7-96a7-aec5813b0f58_765x318.png)

1. “Manually…” 스위치를 켠다.
2. 모델 행 끝에 있는 화살표 버튼을 눌러 advanced settings를 본다.

중요한 부분에 번호를 붙인 Gemma 4 26B 설정은 다음과 같다:

![](https://substack-post-media.s3.amazonaws.com/public/images/d62a88de-3907-41be-96f6-56ad0d85dce6_761x1202.png)

범례:

1. 이 특정 config에 필요한 메모리 양
2. 모델의 attention span에 들어가는 총 token 수(input과 output)
3. deep neural network의 몇 개 layer를 GPU에서 실행할지
4. 사용할 CPU thread 수. 최대로 올리지 말자. AI workload가 진행되는 동안 컴퓨터가 느려질 수 있다.
5. flash attention 활성화
6. key cache의 quantization
7. value cache의 quantization
8. 이 설정을 저장하는 것이 매우 중요하다. 그렇지 않으면 LM Studio가 다음 모델 로드 시 기본값으로 되돌아간다.

좋다, 전문 용어가 많다! 들어가 보자.

대부분의 경우 **Context Length** 슬라이더를 제외하면 이것들을 조정할 필요가 없다. 이를 이리저리 바꿔 보면 GPU 앞의 숫자(오른쪽 위)가 바뀌는 것을 볼 수 있다. 그것이 서로 다른 설정에서 소비될 RAM 양이다. 몇 가지 수치는 다음과 같다:

- Context Length = 262144 (max), VRAM required = 25.74
- Context Length = 4096 (default), VRAM required = 18.16
- Context Length = 150000 (my preference), VRAM required = 22.45

곧 몇 가지 요령을 다루겠지만, 특정 하드웨어에서 무엇이 작동하는지 보려면 다양한 값을 실험해야 한다.

내 경험상 최소 100k token으로 모델을 로드할 수 없다면 VS Code Copilot에서 코딩용으로 쓰기 어려울 것이다. system prompt만 해도 20-40k token을 차지하기 때문이다. 프로젝트에 따라 다르다.

너무 큰 context window를 선택할 수도 없다. 예컨대 최대로 올리는 것이다. context 사용량이 늘어날수록 token generation 속도가 떨어지기 때문이다. 적절한 지점은 harness가 context **utilization이 performance를 해치기** 시작하는 즉시 자동으로 **context를 compress**하는 곳이다.

![](https://substack-post-media.s3.amazonaws.com/public/images/dd4e5ee9-8d94-4b8d-9098-66327761917e_517x543.png)

*Copilot은 단순한 “hi” prompt에도 거대한 system prompt와 tool definition을 보낸다! 이것은 150k Context Window다.*

눈썰미가 좋은 분들은 3가지 서로 다른 config가 작동하고 있다는 것을 알아챘을 수 있다:

- LM Studio는 [Context Length](https://lmstudio.ai/docs/python/model-info/get-context-length)를 정의할 수 있게 해준다. 이것은 모델의 attention span에 들어가는 총 token 수다. 이를 `C`라고 부르자.
- [Copilot이 기대하는 것](https://code.visualstudio.com/docs/agent-customization/language-models):
  - `maxInputTokens`: 모델이 받는 최대 input token 수. 숫자가 작을수록 context compression이 더 공격적으로 작동한다. 이를 `I`라고 부르자.
  - `maxOutputTokens`: 모델이 생성하는 최대 output token 수. 숫자가 작을수록 모델이 쿼리에 응답하는 방식이 더 제한된다. 이를 `O`라고 부르자.

Context length(`C`)는 input(`I`)과 output(`O`) token의 hard ceiling이다:

<span style="display:block;">\(C = I + O\)</span>

VS Code에서 `maxInputTokens`나 `maxOutputTokens`의 권장 값을 언급한 공식 문서를 찾지 못했다. 나는 보통 100k/50k를 선택해 context length를 150k로 맞춘다.

*여러분의 머신이 괜찮은 모델을 실행할 수 없더라도 포기하지 말자. 마지막에 다룰 무료 workaround가 있다.*

나머지 settings menu를 파고들기 전에, 이상적으로는 모든 model layer가 GPU에서 실행되길 원한다는 점만 언급하겠다. 저 “GPU Offload” 슬라이더(3)가 보이는가? 가능하다면 최대로 올리자.

deep neural network의 일부 layer를 CPU(4)에서 실행하는 것도 가능하지만, 대부분의 하드웨어에서는 CPU와 GPU 사이에 데이터를 복사해야 한다. 내가 알기로 Apple Silicon은 UMA 덕분에 유일한 예외다.

좋다, 하드웨어 전문 용어는 충분하다. 요령으로 넘어가자:

- **K Cache Quantization Type**을 `Q8_0`로 설정한다.
- **V Cache Quantization Type**을 `Q4_0`로 설정한다.

![](https://substack-post-media.s3.amazonaws.com/public/images/86231864-bf62-4a7d-9ad1-7b0bba309501_765x506.png)

왜 정확히 이 숫자일까? 마법이다! 😉 농담이다!

여기서 *Quantization*은 KV cache(LLM의 attention mechanism)가 메모리를 사용하는 방식을 조정하는 것을 의미한다. 모델을 다운로드할 때처럼 “resolution”이라고 생각할 수 있다.

![](https://substack-post-media.s3.amazonaws.com/public/images/be6c02d4-c9f3-4954-bcfc-6558ba51cb3f_788x133.png)

*이미지 해상도에 관한 Wikipedia 글의 이미지(그냥 분위기를 잡기 위해)*

우리는 values보다 keys에 더 높은 resolution을 원한다. 이 정확한 숫자들은 내가 내 설정을 설명하고 팁을 얻었던 Gemini Pro와의 대화에서 나왔다. 모든 조합을 시도해 본 것은 아니지만, 이 특정 설정은 GPU memory requirement를 28.75GB(default)에서 22.45GB로 줄였으니 중요하다!

이 config 광풍에서 가장 중요한 부분은 저장하는 것이다:

![](https://substack-post-media.s3.amazonaws.com/public/images/29db2712-2e68-4488-97be-3371af6b6311_761x91.png)

다음번에 이 모델이 REST API를 통해 요청될 때 LM Studio가 이 설정을 기억하게 하고 싶을 것이다. VS Code Copilot은 custom context window length나 local-models에 특화된 다른 옵션을 요청한다는 개념이 없기 때문이다! 주로 cloud AI용으로 만들어졌다.

💭 이론적으로 LM Studio는 `POST /api/v1/models/load` endpoint에서 [이미 지원하는 것](https://lmstudio.ai/docs/developer/rest/load)을 복제하는 custom headers를 사용해 이를 지원할 수 있다. VS Code는 model config에 custom headers를 추가하는 것을 지원한다. 그렇게 하면 LM Studio와 이를 사용하는 agent harnesses 사이에서 config를 중복할 필요가 없다.

거의 끝났다. 아주 작은 팁 하나: LM Studio의 chat window로 가서 방금 조정한 설정을 시험해 볼 수 있다. harness가 없으면 모델은 꽤 멍청할 것이다. 실망하지 말자. 여기서 우리의 목표는 TPS(token per second)를 확인하는 것이다.

TPS performance가 10보다 낮으면 코딩 용도로는 고통스러울 정도로 느릴 것이다. 의미 있는 작업을 하는 시간보다 모델을 기다리는 시간이 더 많아질 것이다. 그리고 시간은 돈이다.

## Copilot Custom Endpoint 설정하기

드디어 여러분이 기다리던 부분이다! 다만 여기서는 GUI 버전을 다룬다. [Copilot CLI 설정 방법은 다르다](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models#connecting-to-an-openai-compatible-endpoint).

**참고: 최신 VS Code 버전이 필요하다. 작성 시점 기준으로 [1.122.1](https://code.visualstudio.com/updates/v1_122)이며, 일주일 전에 출시되었다.**

Copilot chat 창에서:

1. 모델 선택기(Agent 버튼 옆)를 클릭한다.
2. 그런 다음 기어 아이콘을 클릭한다.

![](https://substack-post-media.s3.amazonaws.com/public/images/a697fc14-8e59-4208-8d4a-21f1fdb681b1_600x398.png)

그러면 “Language Model” 대화상자가 열린다:

1. “Add Models”를 클릭한다.
2. Custom Endpoint를 클릭한다. Ollama를 실행하기로 했다면, Ollama 전용 옵션도 볼 수 있다.

![](https://substack-post-media.s3.amazonaws.com/public/images/a2e8f5b4-f18e-416f-9963-9fefc75bfc21_1440x302.png)

그러면 상단 중앙에 작은 입력 상자가 나타난다!

1. “Local LM Studio” 같은 이름을 지정한다.
2. 위에서 LM Studio server를 설정할 때 API Key를 지정했다면 입력한다. 지정하지 않았다면 그냥 enter를 누른다.
3. inference API endpoint의 형태를 선택한다. API 유형은 3가지가 있다. 내 테스트에서는 **Chat Completions**만 매끄럽게 작동했다.

LM Studio는 4개의 endpoint를 지원한다. 다양한 옵션에 대해서는 [여기](https://lmstudio.ai/docs/developer/rest)에서 읽어볼 수 있다.

![](https://substack-post-media.s3.amazonaws.com/public/images/7b350b9f-4ed1-442b-a582-ecff20655f21_855x494.png)

*LM Studio 웹사이트의 Inference Endpoint Comparison*

VS Code는 기본적으로 cloud AI를 염두에 두고 만들어졌기 때문에, 완전히 쓸 만하게 만들려면 몇 가지 단계를 더 거쳐야 한다. 방금 추가한 “Local LM Studio” 항목 앞의 톱니바퀴 아이콘을 클릭하고 JSON에서 settings를 연다:

![](https://substack-post-media.s3.amazonaws.com/public/images/5d6f54e9-b121-4865-a4ad-c430bcf77c5f_1386x669.png)

그런 다음 `url`, `maxInputTokens`, `maxOutputTokens` 및 [기타 parameters](https://code.visualstudio.com/docs/agent-customization/language-models#_model-configuration-reference)를 수동으로 설정한다.

다음은 4B와 A4B(MoE) 버전 둘 다에 대한 내 settings다:

```json
[
  {
    "name": "Local LM Studio",
    "vendor": "customendpoint",
    "apiType": "chat-completions",
    "models": [
      {
        "id": "google/gemma-4-e4b",
        "name": "Gemma 4 4B (chat-completions)",
        "url": "http://localhost:1234",
        "thinking": true,
        "streaming": true,
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 64000,
        "maxOutputTokens": 16000,
        "reasoningEffortFormat": "chat-completions",
        "supportsReasoningEffort": ["off", "on"]
      },
      {
        "id": "google/gemma-4-26b-a4b",
        "name": "Gemma 4 26B MoE (chat-completions)",
        "url": "http://localhost:1234",
        "thinking": true,
        "streaming": true,
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 100000,
        "maxOutputTokens": 50000,
        "reasoningEffortFormat": "chat-completions",
        "supportsReasoningEffort": [
          "none",
          "minimal",
          "low",
          "medium",
          "high",
          "xhigh"
        ]
      }
    ]
  }
]
```

확인해야 할 사항은 다음과 같다:

1. 올바른 `url`이 설정되어 있어야 한다.
2. `thinking` 옵션이 올바르게 설정되어 있어야 한다. Gemma 4는 이를 지원한다.
3. `supportsReasoningEffort`는 모델에 따라 달라지는 array다. 26B 버전은 E4B 버전보다 더 세분화된 제어를 지원한다.

내가 말했던 cold-start의 미묘한 차이를 기억하는가? 그건 모델을 memory에 로드하는 과정과 관련이 있다. 모델에 보내는 첫 prompt는 Copilot이 자체적으로 거대한 system prompt와 tool definitions를 보내기 때문에 매우 무겁다. 이 때문에 맨 처음 interaction에서 2-5분 지연이 발생한다! ☠️

Pi는 기본적으로 system prompt가 아주 작기 때문에 이런 문제가 없다.

감을 주자면, 내 머신에서 모델 로딩은 30초가 걸리는 반면 prompt input tokens 처리에는 약 5분이 걸린다! 다행히 LM Studio가 prompt caching을 존중하기 때문에 이 일은 세션마다 한 번만 발생한다.

Cloud hosted AI providers는 빠릿한 경험을 제공하기 위해 일반적인 prompts를 미리 cache해두는 것 같다. 게다가 이 부분은 대규모 GPU에서 병렬로 실행할 수 있다. local workload에서는 그런 호사를 누릴 수 없다.

기다리는 동안 LM Studio server settings를 열고 prompt processing이 실제로 진행되는 모습을 볼 수 있다. 거의 페인트가 마르는 걸 지켜보는 기분이다!

![](https://substack-post-media.s3.amazonaws.com/public/images/cebf79f9-d728-4512-8f05-845fbeb83016_1047x495.png)

또는 GPU load가 100%로 올라가 열을 발생시키는 모습을 보며 재미를 찾을 수도 있다:

![](https://substack-post-media.s3.amazonaws.com/public/images/81f077f2-880f-4d42-8b8b-c8cb95f5a1a7_247x625.png)

팁: 지금 남반구에 있다면 local AI server를 윤리적인 실내용 heater로 사용할 수 있다! 🫠

### 빠른 테스트

Gemma 4 26B A4B가 무엇을 할 수 있는지 보여주기 위해 one-shot prompt snake game(AGENTS.md나 SKILL 없음)을 만들어봤다:

![](https://substack-post-media.s3.amazonaws.com/public/images/f2abfe15-6e89-4aed-a3e7-3b60cc9f8125_942x745.png)

*여기서 code와 prompt를 보거나 그냥 플레이해보자*

전체 prompt와 source code는 [GitHub](https://github.com/alexewerlof/gemma-snake)에 있다.

내 현재 setup:

- Lenovo ThinkPad L16 Gen 2
- AMD Ryzen 7 PRO 250 APU
- 64GB DDR5 - 5 600MT/s
- Aurora Linux (Fedora 기반 atomic desktop)

*참고: Black Friday 때 이 머신을 아주 싸게 구해서 운이 좋았다고 느낀다! RAM 가격 폭등 때문에 오늘 사려고 하면 두 배가 든다. 하지만 32GB면 충분하다고 생각한다.*

## Pi setup

Pi가 API server 대신 local LM Studio server를 사용하게 하는 것도 아주 쉽다.

한 가지 눈에 띄는 차이는 LM Studio를 설정하는 방식과 더 잘 맞는 `contextWindow` setup이다.

[공식 가이드](https://pi.dev/docs/latest/models)를 반복하며 지루하게 만들지는 않겠다. 다음은 내 config다:

```json
{
  "providers": {
    "lm-studio": {
      "baseUrl": "http://host.containers.internal:1234/v1",
      "api": "openai-completions",
      "apiKey": "test",
      "models": [
        {
          "id": "google/gemma-4-e4b",
          "name": "Gemma 4 4B",
          "contextWindow": 64000,
          "maxTokens": 16000,
          "reasoning": true,
          "thinkingLevelMap": {
            "off": "off",
            "minimal": "on"
          }
        },
        {
          "id": "google/gemma-4-26b-a4b",
          "name": "Gemma 26B MoE",
          "input": ["text", "image"],
          "contextWindow": 150000,
          "maxTokens": 50000,
          "reasoning": true,
          "thinkingLevelMap": {
            "off": "none",
            "minimal": "minimal",
            "low": "low",
            "medium": "medium",
            "high": "high",
            "xhigh": "xhigh"
          }
        }
      ]
    }
  }
}
```

## 요약 정리

OpenRouter의 free models 사용에 대해 이야기하기 전에, development workflows에서 local models를 실행하는 것의 장단점을 정리해보자:

장점:

- Offline으로 작동한다.
- 더 높은 privacy를 제공한다.
- 더 빠른 response time을 얻을 수 있다. 하드웨어, workflow 복잡도, model 및 config에 따라 다르다.

단점:

- Open weight models는 flagship proprietary models만큼 똑똑하지 않다. 하지만 적절한 guardrails(예: lints, tests, AGENTS.md 등)를 갖춘 좋은 harness는 coding workflows에서 accuracy를 크게 향상시킬 수 있다.
- 느리다. 개발 중인 같은 머신에서 LLM을 실행하면, hardware가 inputs를 처리하거나 tokens를 생성하느라 바쁠 때 slow-down을 느낄 수 있다.
- cold-start가 있다.
- initial prompt input processing(cache miss)이 있다.
- 더 높은 초기 hardware 투자가 필요하다. 많은 dev들이 Apple Silicon이 들어간 Apple Mac 컴퓨터를 사용하므로, 아주 큰 문제는 아닐 것이다.

여기서는 LM Studio를 사용하지만, 판세를 익히고 나면 GUI를 건너뛰고 underlying Llama.cpp를 직접 사용할 수 있다.

VS Code Copilot과 Pi를 예시로 사용했지만, 대부분의 다른 harnesses도 local LLM과 함께 작동할 수 있는 custom endpoints를 지원한다.

이 글을 [한 번의 클릭](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fblog.alexewerlof.com%2Fp%2Flocal-llms-for-agentic-coding&t=Using%20local%20LLMs%20for%20agentic%20coding)으로 Hacker News에 공유해줄 수 있을까? 🙏

## OpenRouter의 Free models

[OpenRouter](https://openrouter.ai/)는 단일 endpoint와 account를 통해 수백 개의 models를 노출하는 통합 API 및 routing service다.

무엇이든 하기 전에: OpenRouter를 처음 시도했을 때는 정말 WTF 순간이었다! API Key가 작동하는지 보려고 Pi에 연결해 간단히 “tell me a joke” prompt를 보냈다. 비용이 얼마나 나오는지 보고 싶어서 Opus 4.6을 골랐다! 농담은 내가 당했다! 😆 비싼 실수를 막으려면 아래 instructions를 꼭 읽자.

![](https://substack-post-media.s3.amazonaws.com/public/images/495651bc-9301-41ad-88bb-50a8385a9c83_846x443.png)

account를 작동하게 하려면 약간의 credit을 구매해야 한다.

Copilot, Zed, Pi는 모두 OpenRouter를 기본적으로 지원한다. API token을 만들고 그들에게 제공하기만 하면 된다.

account에 돈을 넣었다면, spending에 cap을 반드시 설정하자.

가장 좋은 방법은 custom guardrail을 만들고 그 위에 `$1/mo` cap을 거는 것이다.

![](https://substack-post-media.s3.amazonaws.com/public/images/aaa63225-dfe3-47b7-ad13-7d516d461ff8_1020x768.png)

그런 다음 free models를 allow-list한다:

![](https://substack-post-media.s3.amazonaws.com/public/images/27a2dc0e-ff32-413d-8440-c99857d3e5dd_783x654.png)

새 API key(Pi나 Copilot 또는 다른 harnesses에서 사용할)를 만들 때 max credit을 설정하는 옵션이 있다. 0으로 설정하자.

![](https://substack-post-media.s3.amazonaws.com/public/images/0b7f0d2e-1d52-4ae2-8f2b-7c9e73492bcd_494x523.png)

깜빡했거나 변경하고 싶다면 Key settings page에서 할 수 있다:

![](https://substack-post-media.s3.amazonaws.com/public/images/7252e5f5-b9be-438b-8a96-5db0ceb3f1dc_943x646.png)

그런 다음 LLM-assistance/agentic coding용으로 생성한 API key에 해당 custom guardrail을 attach한다.

![](https://substack-post-media.s3.amazonaws.com/public/images/1480ba73-aa58-4de6-98f8-e63cc2efe34b_943x396.png)

물론 여기에는 몇 가지 함정이 있다:

1. ZDR(Zero Data Retention) setting이 있긴 하지만, prompts와 data가 training에 사용될 수 있다.
2. internet connection이 필요하다.
3. OpenRouter가 업계의 다른 곳들처럼 free models 제공을 중단하기로 결정할 수 있다.

좋은 점은 model을 local에 다운로드하고 설정할 필요가 없다는 것이다. 또한 model을 사용하는 동안 컴퓨터가 느려지지도 않는다.

**Update 2026-06-09:** 나는 [Claude Opus 4.8만큼 거의 좋은 Deepseek V4 Pro](https://deepseek.ai/blog/claude-opus-4-8-vs-deepseek-v4)를 사용하기로 했다. context window는 5배이고 가격은 약 17-86배 더 저렴하다! 🤯 하지만 Pi와 OpenRouter가 가격에 대해 서로 다른 생각을 갖고 있다는 것을 알게 되었다. OpenRouter에서는 거의 3배 더 비쌌고, markup은 5.5%에 불과해야 했는데도 말이다. 파헤쳐보니 OpenRouter가 내 requests를 더 비싼 endpoint(GMICloud)로 보내고 있었고, 그래서 더 비쌌던 것이었다. 나는 Deepseek에 account를 만들고, 복잡한 tasks를 위한 매우 저렴하면서도 high capability model을 사용하려고 충전했다. 더 단순한 tasks나 behind the scene에서 무슨 일이 일어나는지 이해하는 것이 중요할 때, 또는 privacy가 중요할 때는 local models가 여전히 내 go-to다.
