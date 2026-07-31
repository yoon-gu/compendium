---
title: "Open Multi-Agent: goal에서 task DAG까지 운영 가능한 TypeScript orchestration"
date: 2026-07-31
draft: false
source_url: "https://open-multi-agent.com/"
author: "Open Multi-Agent"
tags: ["AI", "Agents", "Multi-Agent", "Orchestration", "TypeScript"]
summary: "Open Multi-Agent는 Node.js backend 안에서 goal-driven multi-agent 실행을 task DAG, event-driven scheduling, approvals, checkpoint, trace, evaluation으로 묶는 TypeScript-native orchestration framework다. LangGraph처럼 graph를 직접 작성하는 접근과 달리 goal에서 plan을 만들되, 운영 단계에서 필요한 검토·재생·예산·증빙 경계를 함께 제공한다."
---

> **원문:** [Open Multi-Agent: open-source TypeScript AI Agent framework](https://open-multi-agent.com/) — Open Multi-Agent, 2026-07-31 확인
>
> 아래 글은 Open Multi-Agent의 landing page, introduction docs, comparison page, GitHub repository metadata를 바탕으로 작성한 Korean practitioner note다. 이 URL은 논문이나 일반 blog article이 아니라 product/documentation landing page이므로, UI markup을 그대로 번역하지 않고 runtime model, 사용 방식, 운영 caveat를 중심으로 구조화했다.

## 한눈에 보기

Open Multi-Agent(OMA)는 Node.js backend에 붙이는 TypeScript-native AI agent orchestration framework다. 핵심 구호는 “Describe the goal, not the graph”다. 사용자가 outcome을 주면 `runTeam()`이 coordinator를 통해 task DAG를 만들고, scheduler가 dependency가 풀린 task부터 병렬로 실행하며, 마지막에 결과를 synthesize한다. 단순히 model call을 감싼 toolkit이라기보다, 여러 specialist agent가 필요하고 작업 dependency·approval·recovery·trace가 함께 필요한 backend orchestration layer에 가깝다.

2026-07-31 확인 기준으로 GitHub repository는 약 6.7k stars, 2.4k forks를 기록하고 있고, latest release와 npm package 버전은 `v1.13.0` / `@open-multi-agent/core@1.13.0`이다. License는 MIT다. 수치는 시점 의존적이므로 adoption signal로만 읽는 것이 좋다.

## 실행 model: goal-driven DAG와 explicit DAG를 모두 지원

OMA가 반복해서 강조하는 구분은 “goal을 줄 것인가, graph를 직접 줄 것인가”다.

- `runTeam()`은 goal과 team definition을 받아 coordinator가 runtime에 task, dependency, assignment를 만든다. 문제 구조가 input마다 달라지고 specialist role이 여러 개 필요할 때 쓰는 경로다.
- `runAgent()`는 하나의 agent와 focused task만 실행한다. orchestration overhead가 필요 없는 단일 agent 작업에 맞다.
- `runTasks()`는 사람이 이미 알고 있는 explicit task graph를 그대로 실행한다. compliance review, contract review, incident postmortem처럼 graph와 assignment를 통제해야 할 때 유용하다.

Docs의 introduction은 OMA가 잘 맞는 조건을 비교적 명확히 둔다. 서로 다른 specialist role이 필요하고, 일부 work가 병렬로 진행될 수 있으며, input에 따라 step이 바뀔 수 있고, orchestration을 기존 Node.js backend 내부에서 유지하고 싶을 때가 주 사용처다. 반대로 model call 하나로 끝나는 문제, 모든 transition을 고정 graph로만 유지해야 하는 문제, provider SDK나 chat UI만 필요한 문제에는 더 단순한 도구가 낫다.

## 최소 사용 흐름

새 project는 scaffolder로 시작한다.

```bash
npm create oma-app@latest my-oma
```

이 command는 template과 runtime을 고르고 dependency를 설치한 뒤 no-key local demo를 실행하는 경로를 제공한다. demo는 API key 없이 deterministic local response로 OMA scheduler, result synthesis, offline dashboard 흐름을 확인하게 해 준다. 기존 backend에 core만 붙일 때는 package를 직접 설치한다.

```bash
npm install @open-multi-agent/core
```

기본적인 team 실행은 role과 instruction을 가진 agent를 만들고 goal을 넘기는 형태다.

```ts
import { OpenMultiAgent } from '@open-multi-agent/core'

const oma = new OpenMultiAgent({ defaultProvider: 'openai', defaultModel: 'gpt-5.4' })

const team = oma.createTeam('research-team', {
  name: 'research-team',
  agents: [
    { name: 'researcher', systemPrompt: 'Find the relevant facts.' },
    { name: 'analyst', systemPrompt: 'Compare evidence and identify tradeoffs.' },
  ],
  sharedMemory: true,
})

const result = await oma.runTeam(team, 'Compare three approaches and recommend one.')
console.log(result.agentResults.get('coordinator')?.output)
```

이 예에서 developer가 고정하는 것은 team boundary, role, instruction, provider 정도다. 실제 task 분해와 dependency는 `runTeam()` 경로에서 runtime에 만들어진다.

## 운영 control: 동적 plan을 그냥 풀어 두지 않는 장치

Goal-driven planning은 유연하지만, production에서는 “plan이 왜 이렇게 됐는가”, “어디서 멈췄는가”, “누가 승인했는가”, “비용이 어디까지 커질 수 있는가”를 남기지 않으면 위험하다. OMA의 landing page와 docs가 강조하는 runtime surface는 이 지점에 있다.

- Execution routing: single-agent, team, explicit graph 같은 topology를 선택하거나 routing decision으로 분기한다.
- Event-driven scheduling: dependency가 완료된 task를 round barrier 없이 dispatch하고, capability와 hard requirement를 확인한다.
- Approval/governance: 전체 plan이나 개별 dispatch, consequential tool call을 검토·승인하는 boundary를 둔다.
- Plan preview/replay: 생성된 plan을 inspect하고 freeze한 뒤 같은 plan을 재생할 수 있다.
- Budget control: token/cost budget, timeout, retry, loop detection으로 runaway execution을 제한한다.
- Checkpoint/resume: 중단된 run을 checkpoint에서 이어 가고, 필요하면 task boundary에서 recovery한다.
- Default-deny tools: tool access는 기본 거부에서 시작하며 필요한 call만 허용하는 방향을 전제한다.

실무적으로는 “agent가 알아서 해 준다”보다 “agent가 만든 task DAG를 backend가 승인·제한·추적 가능한 실행 단위로 다룬다”에 가까운 abstraction이다.

## Observability와 evaluation

OMA는 run마다 stable ID, execution receipt, trace를 남기는 방향을 취한다. Offline Run Viewer는 완료된 run을 task DAG와 span waterfall 관점에서 재생해 task status, assignee, token, cost, tool call을 확인하게 한다. Hosted OMA service로 trace를 보내야 하는 구조가 아니라, 기본적으로 자기 backend/environment 안에서 evidence를 검토하는 모델이다.

이미 central monitoring stack을 쓰는 팀은 `@open-multi-agent/otel` package로 OpenTelemetry export를 붙일 수 있다. 같은 run evidence는 EvalSet, scorer, offline report, CI quality gate, regression baseline, production sampling의 재료가 된다. 즉 observability data를 단순 debugging log로만 쓰지 않고, quality regression을 막는 evaluation loop에 재사용하는 구성이다.

## 다른 framework와의 위치

Comparison page는 OMA의 자리를 “runtime surface를 비교하라”는 방식으로 설명한다.

- LangGraph는 node-by-node fixed graph와 state history/time-travel 중심의 graph authoring이 필요할 때 더 자연스럽다. OMA는 goal에서 plan을 만들고, 그 plan을 inspect·approve·freeze·replay·checkpoint·trace하려는 TypeScript runtime에 맞다.
- Vercel AI SDK는 provider-neutral model call, tool use, streaming을 위한 lightweight toolkit에 가깝다. OMA는 그 위의 dynamic/explicit task DAG, dependency scheduling, recovery, budget, multi-agent trace layer를 담당한다.
- Mastra나 LangChain은 broader framework/integration catalog 성격이 강하다. OMA는 dependency surface를 작게 유지하면서 Node.js backend에서 orchestration과 control boundary를 분명히 두려는 선택지다.

따라서 OMA를 “LangGraph 대체품” 하나로만 보면 좁다. graph를 직접 설계하는 framework와 경쟁하는 부분도 있지만, 더 본질적인 차이는 goal-first runtime planning을 production control surface와 묶었다는 점이다.

## 어떤 팀이 먼저 검토할 만한가

1. TypeScript backend나 AI platform layer 안에서 agent execution을 service primitive로 넣고 싶은 팀.
2. PR review, security review, incident analysis, document extraction처럼 specialist role과 parallel work가 자연스럽게 나뉘는 workflow를 운영하려는 팀.
3. Dynamic planning을 쓰되 approval, budget, checkpoint, trace, evaluation gate 없이는 production에 올리기 어렵다고 보는 팀.
4. Cloud provider와 local/OpenAI-compatible endpoint를 섞어야 하거나, 외부 coding agent/CLI를 process 또는 ACP backend로 orchestration에 포함하고 싶은 팀.
5. Hosted orchestration service보다 자기 environment, 자기 credential, 자기 data boundary 안에서 run evidence를 남기려는 팀.

반대로 graph를 사람이 완전히 정의하고 각 node transition을 framework 수준에서 세밀하게 통제해야 한다면 LangGraph류의 fixed graph tool이 더 적합할 수 있다. 단일 call + tool use + streaming 정도면 OMA까지 가져오지 않아도 된다.

## Practitioner notes

- OMA의 핵심 가치는 “multi-agent”라는 이름보다 task DAG와 execution evidence다. agent 수를 늘리는 것 자체가 목적이면 오히려 cost와 debugging surface만 커진다.
- Goal-driven planning을 쓰더라도 plan preview, approval, budget cap을 default로 켜는 운영 profile을 따로 두는 편이 안전하다.
- Evaluation은 offline report로 끝내지 말고 CI gate와 regression baseline까지 연결해야 framework가 제공하는 trace가 품질 관리 자산이 된다.
- Default-deny tool model은 production agent system에서 중요한 장점이다. 다만 실제 service에 붙일 때는 tool schema, permission policy, secret redaction, stored state retention을 application boundary에 맞춰 별도로 설계해야 한다.
- Local/offline execution 지원은 배포 선택지를 넓혀 주지만, model quality와 context limit은 orchestration layer가 해결해 주지 않는다. 작은 local model을 쓸수록 coordinator plan quality, task granularity, retry budget을 별도로 검증해야 한다.

## 주요 링크

- Homepage: <https://open-multi-agent.com/>
- Introduction docs: <https://open-multi-agent.com/getting-started/introduction/>
- Quick Start: <https://open-multi-agent.com/getting-started/quick-start/>
- Run modes: <https://open-multi-agent.com/getting-started/three-ways-to-run/>
- Comparison hub: <https://open-multi-agent.com/compare/>
- GitHub repository: <https://github.com/open-multi-agent/open-multi-agent>
- npm registry metadata: <https://registry.npmjs.org/%40open-multi-agent%2Fcore>
- Latest release: <https://github.com/open-multi-agent/open-multi-agent/releases/tag/v1.13.0>
