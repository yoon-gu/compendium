---
title: "지능형 AI Delegation"
date: 2026-07-27
draft: false
source_url: "https://arxiv.org/abs/2602.11865"
author: "Nenad Tomašev, Matija Franklin, Simon Osindero"
tags: ["AI", "Agents", "Delegation", "Multi-Agent", "Safety"]
summary: "AI agent가 복잡한 목표를 안전하게 분해하고 다른 AI 또는 인간에게 위임하기 위해 필요한 intelligent delegation 프레임워크를 제안한다. task decomposition, task assignment, monitoring, trust, permission handling, verifiable completion, security를 하나의 protocol 관점으로 묶는다."
---

전문은 [한국어 번역본](/compendium/papers/intelligent-ai-delegation/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/intelligent-ai-delegation.pdf)
- [arXiv 원문 PDF](/compendium/papers/intelligent-ai-delegation-original.pdf)

> **원문:** [Intelligent AI Delegation](https://arxiv.org/abs/2602.11865) — Nenad Tomašev, Matija Franklin, Simon Osindero, 2026-02-12
>
> 아래 글은 원문 논문의 문제의식과 구조를 따라가며 한국어로 정리한 Compendium note이다. 전체 line-by-line 번역과 원문 layout을 보존한 기술 객체는 PDF를 기준으로 확인할 수 있다.

## 핵심 요지

AI agent가 단순 query-response 도구를 넘어 복잡한 목표를 수행하려면, 작업을 작은 sub-task로 나누는 것만으로는 부족하다. 논문은 delegation을 task allocation의 연쇄적 결정이면서 동시에 authority, responsibility, accountability, roles and boundaries, intent clarity, trust mechanism을 포함하는 구조로 정의한다.

저자들은 현재 multi-agent framework의 delegation이 대체로 heuristic하고 정적이며, failure나 환경 변화에 adaptive하게 대응하기 어렵다고 본다. 이를 보완하기 위해 intelligent delegation을 위한 다섯 축을 제시한다.

1. **Dynamic Assessment** — delegatee의 capability, reliability, current state를 지속적으로 추론한다.
2. **Adaptive Execution** — execution 중 context shift, resource constraint, subsystem failure가 발생하면 delegatee나 plan을 바꿀 수 있어야 한다.
3. **Structural Transparency** — process와 outcome 모두를 audit할 수 있어야 하며 monitoring과 verifiable completion이 필요하다.
4. **Scalable Market Coordination** — web-scale agent economy에서는 trust/reputation과 multi-objective optimization이 coordination의 핵심이 된다.
5. **Systemic Resilience** — permission handling과 security를 통해 responsibility diffusion, cascading failure, monoculture risk를 줄여야 한다.

## 왜 중요한가

이 논문은 MCP, A2A, A2P 같은 agent communication/action protocol이 확산되는 상황에서 delegation을 단순 orchestration pattern이 아니라 socio-technical safety problem으로 다룬다. 특히 human organization의 principal-agent problem, span of control, authority gradient, trust calibration, transaction cost economics를 AI agent network 설계로 가져오는 점이 실무적으로 유용하다.

## Practitioner takeaway

Agent system을 만들 때 `delegate(task)` 같은 API만 설계하면 부족하다. 실제 production workflow에서는 task characteristic, verification cost, authority boundary, monitoring frequency, rollback/reversibility, permission scope, trust/reputation update가 함께 protocol에 들어가야 한다. 이 논문은 그런 설계를 위한 vocabulary와 checklist를 제공한다.
