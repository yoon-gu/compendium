---
title: "Tunix로 Agentic RL training throughput 확장하기"
date: 2026-07-21
draft: false
source_url: "https://developers.googleblog.com/scaling-agentic-rl-high-throughput-agentic-training-with-tunix/"
author: "Haoyu Gao, Lance Wang, Shadi Noghabi, Tianshu Bao, Weiren Yu, Google"
tags: ["AI", "Agentic RL", "Tunix", "JAX", "TPU", "Post-training"]
summary: "Google의 JAX-native post-training library Tunix는 agentic RL에서 rollout과 training을 decouple하고 async rollout, producer-consumer pipeline, composable agent/environment abstraction, RL-specific lightweight profiling을 제공한다. 핵심 목표는 tool call과 environment latency 때문에 TPU가 idle 상태로 빠지는 문제를 줄이고, multi-turn reasoning agent training을 high-throughput으로 확장하는 것이다."
---

> **원문:** [Scaling Agentic RL: High-Throughput Agentic Training with Tunix](https://developers.googleblog.com/scaling-agentic-rl-high-throughput-agentic-training-with-tunix/) — Haoyu Gao, Lance Wang, Shadi Noghabi, Tianshu Bao, Weiren Yu, Google, 2026-07-21
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. Agentic RL, rollout, trainer, TPU, JAX, vLLM, SGLang, GRPO, environment, profiler 같은 practitioner term은 English를 기본으로 유지했다.

![Banner Image](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Banner_Image.original.png)

LLM alignment의 초점은 static chatbot alignment에서 dynamic agentic workflow로 빠르게 이동했다. 오늘날의 model은 단순히 말만 하지 않는다. Multi-step reasoning을 수행하고, external API를 호출하며, complex environment와 상호작용한다.

Reasoning agent를 training할 때는 특별한 challenge와 bottleneck이 생긴다. Agentic RL training의 최근 진화는 process를 single-turn alignment에서 complex environment interaction과 tool usage가 포함된 multi-turn decision-making으로 옮겨 놓았다. 이 변화는 infrastructure 측면에서 rollout performance와 efficiency에 새로운 challenge를 만든다. Agent가 code를 실행하거나, database를 query하거나, web search를 기다리기 위해 멈추면, expensive AI accelerator utilization은 급락하고 TPU는 environment step을 기다리며 idle 상태가 된다.

Google의 post-training library인 Tunix는 최신 release에서 이 bottleneck을 native하게 해결한다. Tunix는 scale에서 LLM agent를 training하기 위한 efficient, composable framework를 도입하고, 두 측면에서 accelerator가 계속 활용되도록 만든다.

- Asynchronous Rollouts: high-concurrency rollout engine이 TPU execution을 network I/O나 tool execution 같은 host-side environment latency에서 완전히 decouple한다.
- Barrier-Free Pipelining: dynamic producer-consumer architecture가 variable-length trajectory를 trainer로 계속 batch/stream하여 pipeline stall을 막는다.

Orchestration을 넘어서, agentic RL에는 specialized observability도 필요하다. XProf 같은 standard profiler는 deep operator-level trace를 제공하지만 overhead가 높아 짧고 sporadic한 capture에 제한된다. Tunix는 domain-specific RL metric을 중심으로 직접 구축된 continuous, lightweight instrumentation을 도입한다. Developer는 high-level loop metric과 TPU timeline을 correlate함으로써 execution efficiency의 global view를 얻고 system bottleneck을 빠르게 찾고 해결할 수 있다.

결국 Tunix는 TPU throughput을 최대화하고, environment를 modular하게 유지하며, multi-turn training efficiency를 완전히 transparent하게 만들기 위해 설계되었다. 아래는 내부 동작 방식이다.

## 1. Asynchronous & Decoupled Rollouts: idle time을 거의 없애고 throughput 최대화하기

Peak hardware throughput을 달성하려면 TPU가 계속 busy 상태여야 한다. Tunix는 asynchronous rollout으로 execution bubble과 straggler를 제거하고, decoupled pipeline으로 data를 trainer에 지속적으로 stream한다.

### Asynchronous Rollouts

Agentic RL에서 trajectory generation, 즉 rollout은 가장 시간이 많이 드는 phase다. 그러나 traditional synchronous rollout architecture는 아래 figure처럼 두 가지 큰 문제를 만든다.

- Execution bubbles: rollout이 environment initialization, state, reward 반환을 synchronously 기다리면 accelerator에 execution bubble이 생기고 efficiency가 낮아진다.
- Straggler effect: batched generation은 long-tail problem에도 취약하다. Group의 가장 느린 trajectory가 전체 latency를 결정한다.

![Synchronous rollout bottlenecks](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Screenshot_2026-07-13_at_10.15.53AM.original.png)

Tunix는 Asynchronous Trajectory Collector Engine으로 이 문제를 해결한다.

- High-Concurrency Execution: framework는 `RolloutOrchestrator` 안에서 Python의 `asyncio`를 활용해 대규모 concurrent agent-environment interaction pool을 관리한다. 한 agent가 host-side tool execution 때문에 멈추면, inference engine은 즉시 다른 active trajectory의 token generation으로 전환한다.
- Async vLLM & SGLang Integration: Tunix는 vLLM-TPU, SGLang-Jax 같은 performant inference engine과 native하게 integrate한다. Async request handling을 enable함으로써 engine은 TPU 위에서 non-blocking sampling과 maximum concurrency를 보장한다.

이 architecture는 model inference, tool execution, reward computation을 완전히 overlap하여 high hardware utilization을 유지한다.

### Decoupled Rollout & Training Pipelining

Async rollout은 trajectory generation bottleneck을 해결하지만, end-to-end RL workflow의 hardware efficiency에는 또 다른 중요한 challenge가 있다. Dynamic하고 variable-length이며 potentially long-tail인 rollout을 strictly synchronous training loop와 연결해야 한다는 점이다. Naive approach는 전체 trajectory batch가 완료될 때까지 accelerator가 기다리도록 만드는 synchronization point에 의존한다. 그 결과 trainer TPU가 굶주리게 된다.

Tunix는 rollout과 training을 continuous producer-consumer pipeline으로 decouple해 이 bottleneck을 제거한다.

- Producer: async rollout orchestrator가 completed trajectory를 high-throughput queue로 계속 yield한다.
- Consumer: `AgenticRLLearner`가 이 queue에서 consume한다. GRPO처럼 group advantage를 계산하기 위해 prompt당 여러 reasoning path가 필요한 algorithm의 경우, Tunix는 asynchronous trajectory를 on the fly로 dynamic grouping한다.

![Decoupled rollout and training pipeline](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Screenshot_2026-07-13_at_10.16.08AM.original.png)

Trajectory group이 complete되는 즉시 post-process, score가 수행되고 trainer로 직접 stream된다. 이 pipeline은 synchronous trainer가 계속 fed 상태를 유지하도록 하여 end-to-end throughput을 극대화한다.

## 2. Composable Agent and Environment Abstractions: OSS environment를 plug-and-play로 붙이기

RL framework에서 큰 friction point는 algorithm이 environment loop와 rigid하게 coupling된다는 점이다. SWE-bench, WebArena, custom game engine 같은 새로운 open-source software(OSS) benchmark를 지원하기 위해 codebase를 수정하려면 대규모 rewrite가 필요한 경우가 많다.

Tunix는 decoupled, composable architecture로 이를 해결한다. Clean API boundary를 expose함으로써 Tunix는 step invocation과 lifecycle management를 자동화하고, 사용자는 core interaction logic에만 집중할 수 있다.

- Agent Layer: prompt formatting, action generation, conversation history를 관리한다. Policy model의 chat parser를 자동 적용하고, multi-turn boundary에서 special token을 보존한다. 이는 strict Token-In, Token-Out(TITO) behavior를 보장하는 데 중요하다. `ConversationAgentBase`를 subclass하여 generation logic을 쉽게 customize할 수 있다.
- Environment Layer: Tunix는 기본적으로 `TaskEnvironment`와 `ToolEnvironment` class를 제공한다. External system과 interface하려면 `BaseTaskEnv`를 상속할 수도 있다. Tunix는 multi-turn episode lifecycle, observation routing, reward processing을 자동으로 처리한다.

중요한 점은 어떤 open-source RL environment든 몇 분 안에 onboard할 수 있다는 것이다. Agent와 environment logic이 training workflow에서 완전히 decouple되어 있으므로, single-turn math verifier를 interactive bash terminal로 바꾸더라도 training code를 수정할 필요가 없다. 이 composable design의 힘을 보여주기 위해 원문은 새 agent, model, environment를 얼마나 쉽게 사용할 수 있는지 몇 가지 example을 제시한다. 더 자세한 customized Agent/Env example은 Google Tunix repository의 [recipes](https://github.com/google/tunix/tree/main/examples)에서 볼 수 있다.

### Example 1: Prebuilt vs. Custom Agents

Tunix는 configuration만으로 바로 동작하는 `ModelAgent`, `ToolAgent` 같은 built-in class를 제공한다.

```python
from tunix.rl.agentic.agentic_grpo_learner import GRPOLearner
from tunix.rl.agentic.agents.model_agent import ModelAgent, ToolAgent


# Non tool calling single turn agent
learner = GRPOLearner(
    agent_class=ModelAgent, 
    agent_kwargs={"system_prompt": "my system prompt"},
    ...
)


# Customized tool call agent
tool_map = {"calculator": CustomizedCalculatorClass, ...}
learner = GRPOLearner(
    agent_class=ToolAgent, 
    agent_kwargs={
        "system_prompt": "my system prompt",
        "tool_parser_name": "gemma",
        "tool_map": tool_map,
    },
    ...
)
```

또는 custom Agent를 직접 만들고 model response를 어떻게 처리할지에 대한 specific logic을 추가할 수도 있다. Tunix는 이 agent를 end-to-end training workflow에 자동으로 wire한다. 예를 들어 `SWEAgent`, `FrozenLakeAgent` 같은 방식이다.

```python
from tunix.rl.agentic.agents.base_agent import ConversationAgentBase
from tunix.rl.agentic.agents import agent_types


# Bring your own agent! 
# Notice how the agent doesn't need to know anything about the model (if it is Qwen, Llama, or Gemma)
class MyAgent(ConversationAgentBase):
    def __init__(self, args):
        ...


    def update_from_model(self, response: str, **kwargs) -> agent_types.Action:
        # Custom logic to process the raw response (e.g., extracting <answer> tags)
        ...


# Tunix automatically wires up the e2e workflow
learner = GRPOLearner(agent_class=MyAgent, agent_kwargs={...}, ...)
```

### Example 2: Bringing in Custom Environments

Agent와 마찬가지로 Tunix는 `TaskEnvironment`, `ToolEnvironment`를 포함한 여러 pre-built environment를 제공한다. 또는 아래 Gymnasium example처럼 몇 가지 main API만 구현해 custom environment를 가져올 수 있다.

```python
import gymnasium as gym
from tunix.rl.agentic.agentic_grpo_learner import GRPOLearner
from tunix.rl.agentic.environments.base_environment import BaseTaskEnv, EnvStepResult


# You only need to focus on the core logic of environment interactions, and Tunix will automatically handle the rest of the lifecycle management and function invocation.
class MyEnv(BaseTaskEnv):
    def _initial_observation(self):
        # handle env creation and initial observation
        self.env = gym.make("your_chosen_env")
        observation, info = self.env.reset(seed=42)
        return observation


    def _step_impl(self, action):
        # compute observation, reward, done, info
        action = self.env.action_space.sample() 
        obs, reward, done, info = self.env.step(action)
        return EnvStepResult(obs, reward, done, info)


    def close(self):
        self.env.close() # clean up env after trajectory is done


learner = GRPOLearner(env_class=MyEnv, ...)
```

## 3. Eliminating the Black Box: RL-specific lightweight profiling

Scale에서 asynchronous agentic training을 실행할 때 traditional logging만으로는 부족하다. Efficiency problem을 식별하려면 granular하면서도 domain-specific한 visibility가 필요하다. Bottleneck이 generation phase에 있는가? Tool call이 너무 오래 걸리는가? Data-loader가 느린가?

[XProf](https://openxla.org/xprof) 같은 standard profiler는 kernel과 model execution 같은 micro-level performance를 이해하기 위해 detailed op-level trace를 제공한다. 그러나 이런 tool로 long-spanning trace를 capture하는 것은 보통 cost-prohibitive하며, low-level data의 noise 속에서 macro-level bottleneck을 식별하기도 어렵다. Agentic RL의 complex workflow에서는 RL stage에 직접 mapping되는 domain-specific metric 기반의 lightweight, macro-level view가 필요하다.

Tunix는 global pipeline과 important sub-step을 모두 나타내는 최소한의 critical RL-specific metric을 신중하게 track하여 이 big picture를 제공한다. Global pipeline은 rollout, training, weight sync phase가 어떻게 interaction하는지 보여주고, sub-step은 각 model call, environment interaction 등을 보여준다. Metric이 lightweight하므로 전체 training job 내내 continuous하게 실행된다. User는 workflow가 global하게 어디에서 stall되는지 빠르게 식별하고, 이후 XProf 같은 tool을 targeted debugging에 사용할 수 있다.

![Perfetto trace for multi-turn agentic training](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/blog-perfetto.original.png)

위 figure는 multi-turn agentic training job에서 capture한 Perfetto trace를 보여준다. CPU thread와 TPU device 전반의 staged execution timeline이 자세히 나타난다. Trace에서 보듯 TPU device utilization은 CPU thread보다 훨씬 높으며, CPU thread의 idle time은 주로 environment execution latency 때문이다.

이 staged RL pipeline의 macro-level tracing은 다음을 가능하게 한다.

- Pinpoint TPU Starvation: Python tool call이나 environment execution이 asynchronous pipeline을 block하는 정확한 시점을 visualize한다. 반대로 parallel rollout이 accelerator saturation을 유지하도록 성공적으로 overlap되는지도 확인할 수 있다.
- Verify Pipeline Alignment: macro-stage의 정확한 timing을 track하여 hidden latency bubble 없이 align되는지 확인한다. Trainer가 rollout generation을 기다리지 않는지, weight synchronization이 심각한 execution delay를 만들지 않는지 쉽게 검증할 수 있다.
- Optimize Training Configuration: metric data를 사용해 performance를 dynamic하게 tune한다. 예를 들어 thread pool을 TPU idle time과 직접 correlate하여 max rollout concurrency를 조정하거나, data generation rate와 HBM constraint를 바탕으로 training micro-batch size를 optimize할 수 있다.

Tunix는 distributed multi-turn RL의 “black box”를 training job에 대한 transparent하고 optimizable한 timeline으로 바꾼다.

## How Tunix Compares to the Ecosystem

Agentic RL framework를 평가하고 있다면, Tunix는 다음과 같은 차별점을 가진다.

- vs. OpenRLHF / veRL: OpenRLHF와 veRL은 Ray + vLLM을 사용해 상당한 진전을 만들었다. 그러나 이들은 주로 PyTorch ecosystem을 중심으로 구축되어 있다. Tunix는 이 capability를 JAX/TPU ecosystem에 native하게 가져온다. JAX, Flax, Optax 위에 seamless하게 위치하며, XLA compiler optimization을 활용하는 native Pathways multi-host distributed training을 제공한다.
- vs. Hugging Face TRL: TRL은 standard single-turn SFT(Supervised Fine-Tuning)와 RLHF(Reinforcement Learning from Human Feedback)에 잘 맞는다. 그러나 complex multi-turn async loop를 orchestration하려면 상당한 custom glue code가 필요한 경우가 많다. Tunix는 multi-turn, tool-use environment를 out-of-the-box first-class citizen으로 만든다.
- vs. Ray RLlib: RLlib은 comprehensive general-purpose RL powerhouse다. 그러나 modern LLM을 accelerator 위에서 native하게 mapping해 heavy overhead 없이 weight를 share하도록 만드는 일은 복잡하다. Tunix는 관점을 뒤집는다. High-performance RL을 native LLM serving infrastructure에 직접 가져오는 LLM-first library다.

## Start Building Your Agents Today

SOTA reasoning model을 reproduce하든, Gemma나 Qwen family가 “think”하도록 fine-tune하든, complex multi-agent system을 deploy하든, Tunix는 다음 세대 reasoning agent에 필요한 high-performance foundation을 제공한다. 지금 바로 build를 시작할 수 있다.

- Repo에 star를 주고 code 살펴보기: [github.com/google/tunix](https://github.com/google/tunix)
- Recipes: SWE coding agent, math, gaming agent.
- Docs 읽기: [tunix.readthedocs.io](https://tunix.readthedocs.io/)
- Quick Start 시도하기: `/examples` folder에서 다양한 recipe를 살펴보고 첫 training job을 실행할 수 있다.

*Tunix는 Google과 wider community가 active하게 open-source development 중이다. 다음 세대 reasoning agent를 만들고 있다면 GitHub Issues에 들러 어떤 environment를 plug in하고 있는지 알려 달라고 원문은 권한다.*

## Practitioner 관점에서 읽을 포인트

1. Agentic RL throughput 문제의 본질은 model FLOPs만이 아니다. Tool call, web/search/database I/O, environment step latency 때문에 rollout이 길어지고 TPU가 idle해지는 pipeline 문제다.
2. Tunix의 핵심 design은 rollout과 training의 decoupling이다. Async rollout은 inference와 environment latency를 overlap하고, producer-consumer pipeline은 trainer가 completed trajectory group을 계속 받게 만든다.
3. Agent/environment abstraction은 benchmark onboarding 비용을 줄인다. Training loop를 바꾸지 않고 agent parser나 external environment만 교체할 수 있는 boundary가 중요하다.
4. Observability는 agentic RL에서 first-class concern이다. Long-running multi-turn job에서는 XProf 같은 op-level profiler만으로는 부족하고, rollout/training/weight sync/environment step을 이어 보는 domain-specific metric이 필요하다.
5. Tunix는 PyTorch/Ray 중심 stack과 달리 JAX/TPU native path를 택한다. TPU pod, Pathways, XLA optimization을 이미 사용하는 team에는 이 점이 핵심 차별점이 된다.
