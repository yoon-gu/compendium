---
title: "Hardware-aware Dynamic Speculative Decoding"
date: 2026-07-12
draft: false
source_url: "https://cohere.com/blog/hardware-aware-dynamic-speculative-decoding"
author: "Ekagra Ranjan, Cohere"
tags: ["AI", "LLM Inference", "Speculative Decoding", "vLLM", "Cohere"]
summary: "Cohere는 Speculative Decoding의 draft token 수 K를 hardware 상태와 batch size에 맞춰 동적으로 고르는 DSD를 설명한다. DSD는 small batch에서는 남는 compute를 활용하고, large batch에서는 fixed-K SD가 throughput을 해치는 구간을 피하며, vLLM의 async scheduling과 Full CUDA Graph까지 고려해 production inference에 맞춘다."
---

> **원문:** [Hardware-aware dynamic speculative decoding](https://cohere.com/blog/hardware-aware-dynamic-speculative-decoding) — Ekagra Ranjan, Cohere, 2026-07-10
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 기술 독자를 위해 Speculative Decoding, batch size, throughput, scheduler, CUDA Graph 같은 practitioner terminology는 영어를 기본으로 유지했다.

## 핵심 요약

Cohere의 글은 Speculative Decoding(SD)을 단순히 “draft model을 붙이면 빨라진다”가 아니라, GPU의 compute와 memory bandwidth 사이의 operating regime에 따라 이득이 달라지는 hardware-aware 문제로 설명한다. Fixed-K SD는 small batch에서는 효과적이지만, batch size가 커져 inference가 compute-bound로 이동하면 오히려 vanilla decoding보다 느려질 수 있다. Dynamic Speculative Decoding(DSD)은 offline profiling으로 acceptance length(AL)와 inter-token latency(ITL)를 측정해 `goodput = AL / ITL`을 최대로 만드는 K를 lookup table로 저장하고, runtime에서 batch/model/hardware 상태에 맞게 K를 선택한다.

Dense model에서는 batch size가 커질수록 optimal K가 대체로 단조 감소한다. MoE model에서는 low batch에서 expert loading 비용 때문에 K가 낮고, mid batch에서는 대부분의 expert가 이미 load되어 K가 높아질 수 있으며, high batch에서는 다시 compute-bound가 되어 K가 낮아지는 비단조 패턴을 보인다. Cohere는 이 최적화를 vLLM에 기여하면서 async scheduling과 Full CUDA Graph(FCG)와의 compatibility까지 다루었다.

## Speculative decoding의 hardware 관점

Speculative decoding(SD)은 품질 손실 없이 large language model(LLM) inference를 가속하는 데 널리 쓰이는 기법이다. 일반적인 LLM inference는 token을 한 번에 하나씩 생성한다. SD는 대신 더 작은 draft model이 여러 token을 제안하고, large target model이 그것들을 single timestep에서 verify한다. 한 step에서 하나보다 많은 token이 accept될 수 있으므로 generation 속도가 빨라진다.

SD의 speedup은 GPU의 compute와 memory bandwidth 사이의 tradeoff를 활용한다. 여러 request를 batch로 묶으면 GPU utilization은 좋아지지만, 실제 operating regime은 batch size(BS)에 따라 달라진다.

- Small BS에서는 inference가 memory bandwidth-bound다. LLM weight를 HBM에서 SRAM으로 load하는 비용이 지배적이다.
- Large BS에서는 inference가 compute-bound가 된다. LLM weight와 많은 request token 사이의 matrix multiplication 비용이 지배적이다.

SD에서 걸리는 시간은 크게 두 부분으로 나눌 수 있다.

> **Time in SD = Time to draft tokens (small draft model) + Time to verify draft tokens (large target model)**

Draft model은 실행 비용이 훨씬 낮다. Draft가 K개의 token을 만들면 target model은 `BS × (K+1)` token을 처리해야 하므로, verification이 bottleneck이 된다. 주어진 BS에서 K+1배의 computation을 수행하기 때문이다. 현대 GPU에서는 compute unit이 memory bandwidth보다 보통 두 자릿수 정도 빠르기 때문에, memory bandwidth-bound인 small-BS inference에서는 compute unit이 상당 부분 idle 상태로 남는다. SD는 verification 동안 target model에 K+1배 많은 token을 밀어 넣어, 원래라면 낭비될 compute를 활용한다.

## Speculative decoding의 과제

### Production의 dynamic batching

Batch size가 커질수록 일반 LLM inference는 점점 compute-bound가 되고, SD가 활용할 idle compute가 사라진다. 이 regime에서는 SD가 일반 inference보다 오히려 느려질 수 있다. 이는 BS가 거의 작게 고정되지 않고 동적으로 변하는 production system에서 SD의 활용 범위를 제한한다.

### Reinforcement learning (RL)

RL은 model weight를 update하는 training phase와, 학습에 사용할 data와 reward signal을 생성하는 rollout phase를 번갈아 수행한다. Rollout phase가 주된 bottleneck이며 resource의 최대 [85%](https://microsoft.ai/pdf/mai-thinking-1.pdf)를 소비할 수 있다. RL scaling은 model intelligence를 개선하는 중요한 경로이므로, RL rollout inference를 가속하는 것은 중요한 문제다.

하지만 reasoning model을 사용하는 RL은 long-tail distribution을 만든다. Batch 안의 단일 request가 매우 오래 generation을 지속하면서 batch의 나머지를 stall시키고 resource를 낭비할 수 있다. SD는 이런 long-tail generation에 도움이 되지만, high BS에서 throughput을 해치기 때문에 full deployment에서의 전체 utility가 제한된다.

이 두 문제는 같은 요구로 수렴한다. 더 나은 SD system은 hardware constraint에 따라 optimal K를 control해야 하며, 그래야 full production system과 large-scale RL rollout에서 계속 유용하다.

### Dynamic speculative decoding

여기서 hardware-aware dynamic SD(DSD)가 등장한다. DSD는 draft token 수를 adaptive하게 만들어 standard SD를 개선한다. SD에서는 K가 fixed다. DSD에서는 model과 hardware의 상호작용을 기준으로 optimal K를 선택한다. DSD는 inference가 memory bandwidth-bound일 때 K를 늘리고, compute-bound일 때 K를 줄인다.

Dense model에서는 일반적으로 low BS에서 K가 높고 high BS에서 K가 낮다. BS가 커질수록 optimal K가 단조 감소하는 패턴이다. MoE(Mixture-of-Experts) model에서는 optimal K가 BS에 대해 비단조적이다.

- Low BS에서는 verification이 추가 expert를 load하므로 optimal K가 낮게 시작한다.
- Mid BS에서는 거의 모든 expert가 이미 load되어 있으므로 verification이 추가 expert loading을 거의 유발하지 않아 optimal K가 증가한다.
- High BS에서는 dense model과 마찬가지로 computation이 compute-bound가 되므로 optimal K가 다시 감소한다.

이 메커니즘을 더 깊게 다룬 내용은 SD와 MoE의 상호작용을 설명한 Cohere의 이전 [blog post](https://cohere.com/blog/mixture-of-experts-models-get-more-from-speculative-decoding)를 참고하면 된다.

그렇다면 optimal draft token 수는 어떻게 찾을 수 있을까? K에서 K+1 draft token으로 이동할 때의 marginal contribution을 이해해야 한다. 하나의 draft token을 처리하는 computational cost는 그 token의 위치와 무관하게 동일하다. 첫 번째 draft token과 마지막 draft token의 비용은 같다. 그러나 Acceptance Length(AL)에 대한 기여는 위치에 크게 의존한다. 이 기여는 [exponential decay](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf)하므로, 앞쪽 token이 뒤쪽 token보다 accept될 가능성이 훨씬 높다. 따라서 draft token을 하나 더 추가할 때의 tradeoff를 포착하는 metric이 필요하다.

![Speculative decoding diagram](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/4ce7215f061995e994d9aeea67f1f06d4b58de7c-846x923.png?auto=format&fit=max&q=90&w=846)

[TurboSpec](https://arxiv.org/pdf/2406.14066) 같은 기존 DSD work는 이 metric으로 goodput을 사용한다. Cohere도 goodput을 사용하지만, 다음처럼 단순화한다.

> **goodput = AL / ITL**

AL은 acceptance length이고, ITL은 inter-token latency이며 대체로 draft time과 verify time의 합이다. 이 식은 K개 draft token이 AL에 주는 marginal contribution과 wall clock cost 사이의 tradeoff를 포착한다. 값이 높을수록 더 나은 speedup을 의미한다. 이 단순한 formulation은 DSD를 future model architecture에 쉽게 adapt할 수 있게 해준다. 또한 ITL이 이미 모든 operation의 combined impact를 담고 있으므로, 각 component를 개별 profiling한 뒤 다시 recombine할 필요가 없다. Cohere는 offline profiling을 통해 AL과 ITL을 측정하고, optimal K를 찾아 runtime에서 사용하는 lookup table로 저장한다. 이 offline table은 cold-start 문제를 해결하며 확장 가능하다. Engine의 runtime metric에서 얻은 live AL/ITL statistics를 통합하면 DSD가 workload 변화에 adapt할 수 있다.

### Results

Cohere는 세 가지 configuration을 비교한다. Speculative decoding이 없는 vanilla, fixed-K SD(SD baseline, fixed `K=3`의 EAGLE draft head), 그리고 dynamic K를 쓰는 DSD다. Dataset은 MT-Bench이며 sample 수를 `20 * BS`로 upsample하여 BS가 20 wave 사용되도록 했다.

Cohere는 Command A(Dense)와 Command A+(MoE)에 대해 DSD가 선택한 optimal K를 profiling했다. Empirical result는 위에서 설명한 trend를 검증한다. Dense model에서는 BS가 증가할수록 optimal K가 단조 감소하지만, MoE model에서는 그렇지 않다. Command A+는 mid BS에서 더 높은 optimal K에 도달할 수 있다.

![Optimal K profiling for Command A](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/ee7bd1c976530af746df68d3e474b00f4a535ead-1127x688.png?auto=format&fit=max&q=90&w=1127)

![Optimal K profiling for Command A+](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/8c6c36b8dfa3bddc245eb69f585484484c5dd389-1501x851.png?auto=format&fit=max&q=90&w=1501)

Cohere는 TOPS/user(token output per second, per user)도 benchmark했다. Command A(Dense)에서는 전체 BS range에서 DSD의 gain이 분명하다.

- Low BS에서 DSD는 SD(`K=3`)의 speedup과 맞먹는다.
- High BS(64/128)에서 DSD는 SD와 vanilla model보다 모두 빠르다.
- Very high BS(256)에서 DSD는 vanilla TOPS와 맞먹는다. 반면 SD는 BS 128과 256에서 regression을 보인다.

구체적으로 DSD는 BS 128과 BS 256에서 SD보다 약 23% 빠르다. 또한 BS 128에서는 vanilla보다 7.5%, BS 256에서는 1.82% 빠르다. 반면 SD는 이 구간에서 vanilla 대비 regression을 보인다. 다시 말해 DSD는 SD가 도움이 되는 곳에서는 speedup을 가져가고, fixed-K SD가 해를 끼칠 구간에서는 vanilla performance에 가깝게 graceful fallback한다.

![TOPS per user results](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/c1b035156bd085729df45dfe4300b3356747def7-1297x639.png?auto=format&fit=max&q=90&w=1297)

Command A+(MoE)에서는 SD와 DSD가 비슷한 speedup을 보인다. 이는 DSD가 BS 16-32 사이를 제외한 대부분의 BS range에서 `K=3`을 선택해 fixed-K SD와 일치하기 때문이다. BS 16-32 사이에서는 `K=5`를 선택하지만, 이 더 높은 K가 추가 speedup으로 이어지지는 않았다. 가장 그럴듯한 이유는 EAGLE head가 single timestep용으로 학습되었지만 `K > 1` timestep에 재사용되기 때문에, acceptance가 boost를 만들 만큼 충분히 높지 않다는 점이다. Cohere는 [EAGLE-3](https://arxiv.org/abs/2503.01840)나 [DFlash](https://arxiv.org/abs/2602.06036) 같은 더 최근 방법이 이 scenario에서 더 분명한 gain을 보일 것으로 기대한다.

### vLLM에 대한 Cohere의 contribution

Cohere는 올해 초 이 optimization을 vLLM에 기여했다. 관련 [pull request](https://github.com/vllm-project/vllm/pull/32374)와 사용법을 설명한 [vLLM docs](https://docs.vllm.ai/en/latest/features/speculative_decoding/dynamic_speculative_decoding/)가 있다. DSD라는 아이디어 자체가 새롭지는 않고 naive implementation도 간단해 보일 수 있지만, 진짜 어려움은 이를 vLLM처럼 highly optimized inference framework 안에 채택하는 데 있었다. vLLM에는 async scheduling과 Full CUDA Graph 같은 여러 optimization이 들어 있으며, DSD가 vLLM의 효율을 온전히 끌어내려면 이들과 모두 compatible해야 한다. Cohere는 그중 가장 중요한 두 가지를 설명한다.

### Async scheduling과의 compatibility

Inference framework는 먼저 request를 schedule한다. 이는 CPU work다. 그다음 model inference를 실행한다. 이는 GPU work다. 역사적으로 GPU가 bottleneck이었지만, production-grade GPU가 더 빨라지면서 CPU scheduling overhead가 상대적으로 커졌다. GPU가 일찍 끝나고 다음 batch가 schedule되기를 기다리는 상황이 생긴다. 이를 해결하기 위해 vLLM은 [asynchronous scheduling](https://vllm.ai/blog/2026-03-24-mrv2)을 도입했다. 이는 timestep **T+1**의 scheduler(CPU)를 timestep **T**의 model runner(GPU)와 overlap하여 scheduler latency를 숨긴다. 그 결과 CPU의 scheduler overhead를 최소화한다.

중요한 점은 T+1의 scheduler가 T에서 아직 parallel 실행 중인 model runner의 output 없이 실행된다는 것이다. 이것이 가능한 이유는 scheduler가 CPU에서 count와 placeholder만 사용해 한 step 앞서 동작하기 때문이다. 실제 token value는 GPU에 있고, 한 step 뒤 model runner가 GPU-side scatter를 통해 소비한다. Process boundary를 비동기적으로 건너는 것은 placeholder와 token count 같은 lightweight count뿐이다.

Scheduler는 model runner에게 얼마나 많은 draft token을 생성할지, 그리고 이전 timestep의 draft token 중 현재 timestep에서 몇 개를 verify할지를 알려준다. DSD는 모든 timestep에서 같은 수의 draft token이 생성되고 verify된다는 가정을 깨뜨리므로, scheduler와 model runner 양쪽의 bookkeeping을 바꾼다.

아래 diagram은 timestep에 걸친 async scheduling 아래의 DSD를 보여준다. 여기서 system은 T-1까지 token 다섯 개를 draft하고, T에서는 세 개로 전환한 뒤, T+1에서는 일곱 개로 전환한다.

![DSD with async scheduling across timesteps](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/7de97f03dd0172b4036f69413904b533f3741216-4766x2979.png?auto=format&fit=max&q=90&w=2383)

### Full CUDA Graph와의 compatibility

Model forward pass는 많은 CUDA kernel을 launch하며, 각 kernel launch에는 CPU overhead가 발생한다. 현대 production-grade GPU가 더 빨라지면서, 많은 kernel에 걸쳐 누적되는 per-launch overhead가 전체 inference time의 상당 부분을 차지하게 되었다. Full CUDA Graph(FCG)는 warmup 동안 모든 kernel launch를 capture하고, 이후에는 개별 launch 여러 개 대신 단일 graph launch로 replay하여 이 overhead를 제거한다.

vLLM은 decode request에 대해 `<number of tokens in a batch, fixed K>` tuple을 capture하는 방식으로 [FCG support](https://docs.vllm.ai/en/latest/design/cuda_graphs/#full-cuda-graph-capturing-warm-up)를 제공한다. DSD는 이를 `<number of tokens in a batch, different optimal K>` capture로 확장한다. 더 많은 combination을 record하여 runtime에서 K가 바뀌어도 captured CUDA Graph를 hit하도록 한다. 관련 [pull request](https://github.com/vllm-project/vllm/pull/45953)도 있다.

아래 diagram은 max `K=3`인 예를 보여준다. 이 예에서 batch에 token이 여덟 개 있을 때 standard SD는 `<8 tokens, K=3>`만 capture한다. 반면 DSD는 token 수가 `K+1`로 나누어떨어지는 모든 valid K를 capture한다. 즉 `<8 tokens, K=1>`과 `<8 tokens, K=3>`이다. `K+1`로 나누어떨어진다는 것은 batch의 모든 request가 decode request라는 뜻이며, 이것이 vLLM에서 FCG로 route되는 조건이다.

![Full CUDA Graph capture combinations for DSD](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/1db1f5e315306f2a403f5521f16a2e9b372e5571-1085x723.png?auto=format&fit=max&q=90&w=1085)

### Acknowledgements

Cohere 측에서는 이 work 전반에 기술 지원을 제공한 Acyr Locatelli와 Bharat Venkitesh에게 감사를 전한다. 또한 vLLM PR에 대한 논의와 review를 제공한 Lucas Wilkinson(Red Hat)과 Benjamin Chislett(Nvidia)에게 특별한 감사를 전한다.
