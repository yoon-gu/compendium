---
title: "Modular Prompt Transpilation으로 scalable AI agent 만들기"
date: 2026-07-16
draft: false
source_url: "https://developers.googleblog.com/building-scalable-ai-agents-with-modular-prompt-transpilation/"
author: "Simerus Mahesh, Google Developers Blog"
tags: ["AI", "AI Agents", "Prompt Engineering", "CI/CD", "Agent Infrastructure"]
summary: "Production AI agent에서 monolithic system prompt는 유지보수성과 reliability를 떨어뜨린다. Google Developers Blog 글은 prompt를 static text가 아니라 build artifact로 다루고, modular skill file, transpiler, build-time validation, CI/CD drift check를 통해 agent instruction layer를 software처럼 versioning·검증·배포하는 방식을 제안한다."
---

> **원문:** [Building scalable AI agents with modular prompt transpilation](https://developers.googleblog.com/building-scalable-ai-agents-with-modular-prompt-transpilation/) — Simerus Mahesh, Google Developers Blog, 2026-07-16
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. Prompt, skill, transpiler, build artifact, CI/CD 같은 practitioner term은 English를 기본으로 유지했다.

![Agent Development Kit: Making it easy to build multi-agent applications](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Ai-1-banner.original.png)

AI agent를 처음 만들 때는 하나의 monolithic system prompt만으로도 보통 충분하다. Instruction 몇 줄, tool definition 한두 개가 있고, 모든 것이 읽기 쉬운 하나의 file 안에 들어 있다.

하지만 production 목적으로 사용하기 시작하면 이 format은 곧 무너진다. Team은 safety policy, domain-specific rule, formatting requirement, escalation behavior를 계속 덧붙이기 시작한다. 어느 순간 agent의 control plane 전체가 단일 instruction file 안에 들어가고, 바로 거기서 문제가 시작된다.

이것은 전형적인 software engineering scaling problem이다. 모든 concern을 하나의 file에 밀어 넣으면 system을 추론하는 능력을 잃는다. Collaboration은 악몽이 되고, testing은 까다로워지며, 한 workflow를 개선하려는 작은 change가 다른 workflow를 조용히 깨뜨릴 수 있다.

Production scale에서는 prompt maintainability가 곧 agent reliability가 된다.

## Why monolithic prompts break down

Prompt가 일정 크기를 넘어서면 보통 세 가지 주요 failure mode가 나타난다.

1. Obscured blast radius: 일반적인 software engineering에서는 module boundary, call site, test를 통해 reviewer가 change scope를 추론하기 쉽다. 그러나 system prompt diff는 더 어렵다. Sentence 하나를 추가하는 것만으로 agent 전체에 unintended side effect가 생길 수 있고, 이를 예측하거나 test하기가 어렵다.
2. Copy-paste drift: Organization이 scale하면서 많은 team은 internal service 사용 instruction, PII handling, safety policy, escalation protocol 같은 shared logic을 여러 application에 복제하게 된다. 그 결과 같은 functionality를 copy-paste하거나 여러 version으로 유지하게 되고, inconsistency가 생긴다.
3. Deferred runtime errors: Prompt sprawl을 관리하기 위해 team은 흔히 ad-hoc string formatting이나 simple template에 의존한다. Authoring에는 도움이 되지만, error detection이 runtime으로 밀린다. Missing variable이나 invalid import path 때문에 특정하고 드물게 사용되는 workflow가 trigger될 때만 실패하는 prompt를 deploy할 수도 있다.

Template은 좋은 출발점이지만 충분하지 않다. Production system에는 deterministic build, static validation, CI/CD integration이 필요하다.

## Treat prompts like software artifacts

해결책은 prompt를 단순한 static text가 아니라 build artifact처럼 다루는 것이다.

하나의 monolithic prompt file을 유지하는 대신 modular skill file을 작성할 수 있다. 이렇게 하면 각 file의 scope를 줄이고 특정 behavior를 encapsulate할 수 있으며, team은 concern을 분리하고 component별로 iterate할 수 있다.

Top-level agent prompt template은 다음과 비슷할 수 있다.

```plaintext
# agents/sre_agent.prompt.md (prompt template file)

{% include "shared/safety.prompt.md" %}
{% include "shared/tool_usage.prompt.md" %}

You are an SRE triage agent operating in the {{ environment }} environment.

{% if allow_remediation %}
You may recommend remediation steps, but destructive actions require human approval.
{% else %}
You may inspect, summarize, and explain the issue, but do not recommend remediation actions.
{% endif %}

{% macro bullet_section(title, items) %}
## {{ title.rstrip() }}
{% for item in items %}
- {{ item.rstrip() }}
{% endfor %}
{% endmacro %}

{{ bullet_section("Required investigation steps", [
  "Inspect recent deployment events",
  "Check service metrics for latency or error-rate changes",
  "Review logs for repeated failure patterns"
]) }}
```

이 방식은 두 세계의 장점을 모두 제공한다. Templating layer는 shared instruction을 compose하고, environment-specific value를 inject하며, macro를 활용하게 해준다. 그러나 build system 입장에서는 모든 include가 dependency이고, 모든 variable이 requirement다. 그 결과 model에 도달하기 전에 test, audit, diff할 수 있는 deterministic fully-rendered artifact가 만들어진다. 이후 transpiler를 사용해 template import를 resolve하고, agent가 ingest할 준비가 된 file을 생성할 수 있다.

예를 들어 `environment = production`이고 `allow_remediation = true`라면 transpiled artifact는 다음과 같다.

```plaintext
You are an SRE triage agent operating in the production environment.

You may recommend remediation steps, but destructive actions require human approval.

## Required investigation steps

- Inspect recent deployment events
- Check service metrics for latency or error-rate changes
- Review logs for repeated failure patterns
```

High-level transpilation pipeline은 다음과 같은 형태가 된다.

![Figure 1: high-level transpilation pipeline](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Figure1.original.png)

## Build-time validation is mandatory

Production-grade transpiler는 runtime 이전에 error를 잡아야 한다.

Build process 중에 missing import, undefined variable, circular dependency에 대한 validation check를 실행해야 한다. 여기서는 dependency graph가 매우 중요하며, solid template engine이 필요하다는 점을 다시 강조한다. 각 prompt fragment를 directed graph의 node로 다루면, production에서 silent failure를 만들 수 있는 recursive import를 쉽게 잡아낼 수 있다.

![Figure 2: dependency validation](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Figure2.original.png)

이 방식은 drift checking도 가능하게 한다. CI pipeline이 source에서 transpiled prompt를 다시 생성하도록 설정하고, 이를 현재 commit된 artifact, 즉 golden file과 비교할 수 있다. Output이 다르면 build는 실패한다. 이렇게 하면 repo 안의 code가 production에서 실행 중인 것과 정확히 같다는 것을 보장하고, source file과 deployed artifact 사이의 gap을 제거한다.

![Figure 3: drift checking with a golden file](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Figure3.original.png)

## Dynamic skills and agent-authored updates

Modular prompt fragment로 이루어진 skill library가 커지면, 모든 agent가 매번 모든 skill을 load하기를 원하지는 않는다. 그렇게 하면 token을 소비하고 noise가 늘어나며, agent의 task-specific performance를 방해할 수 있다.

더 나은 architecture pattern은 progressive disclosure를 활용하는 것이다. 여기서는 stable control plane과 task-specific context를 분리한다. Compiled base prompt는 identity와 safety boundary 같은 non-negotiable behavior를 enforce해야 한다. 그런 다음 runtime에서 agent는 tool을 사용해 현재 task에 필요한 specific skill module만 dynamic하게 retrieve할 수 있다. 이는 context exhaustion을 줄이고 agent가 task에 집중하도록 돕는다.

![Figure 4: dynamic retrieval of task-specific skill modules](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Figure4.original.png)

이 modular system을 갖추면 강력한 workflow가 열린다. Agent가 자기 자신의 instruction layer를 유지하는 데 도움을 줄 수 있고, self-sustaining agentic system을 만들 수 있다. Agent가 새로운 incident type을 해결했다면, 이론적으로 새로운 skill module을 draft하고, 관련 import를 update하며, pull request를 열 수 있다.

Agent가 자신의 instruction을 real-time으로 mutate하는 것은 아니다. Agent는 code change를 propose한다. Transpiler는 그 proposal을 다른 code change와 동일한 validation과 review rigor에 통과시킨다. Human reviewer는 PR을 inspect하고, eval을 실행한 뒤, change를 merge할 수 있다.

![Figure 5: agent-authored updates through normal code review](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Figure5.original.png)

## Conclusion

Production prompt transpiler는 prompt engineering을 build-system problem으로 다시 framing한다.

Modular skill file을 만들면, 일반 software infrastructure에서 하는 것처럼 dependency를 resolve하고, import를 validate하며, drift check를 enforce할 수 있다. Agent는 자신의 logic에 대한 improvement를 suggest할 수 있게 되지만, 그 change는 기존 validation과 review process를 통과해야 한다.

AI agent가 critical workflow에 깊이 integrate될수록, 그 instruction layer에는 software에 요구하는 것과 같은 reliability standard가 필요하다. Prompt는 단지 edit되는 것이 아니라 build되고, validate되고, versioning되고, deploy되어야 한다.

## Practitioner 관점에서 읽을 포인트

이 글은 prompt engineering을 “문장 잘 쓰기”가 아니라 agent infrastructure의 build pipeline 문제로 옮긴다. 특히 Hermes/Compendium처럼 skill, tool, context compaction, scheduled workflow를 다루는 system에서는 몇 가지 시사점이 크다.

1. Prompt는 source와 artifact를 분리해야 한다. 사람이 유지하는 modular source와 model이 실제로 읽는 rendered prompt를 구분하면 review와 validation이 쉬워진다.
2. Skill은 documentation이 아니라 dependency가 된다. Include graph, required variable, circular dependency를 build-time에 검증해야 production incident를 줄일 수 있다.
3. Golden file drift check는 prompt 운영에도 잘 맞는다. “현재 repo의 prompt source”와 “실제로 deploy된 rendered instruction”이 다르면 CI가 실패해야 한다.
4. Dynamic skill retrieval은 context window 관리의 핵심 pattern이다. 모든 skill을 항상 넣는 대신, base prompt는 invariant를 담고 task-specific skill은 runtime에 retrieve하는 편이 더 scalable하다.
5. Agent-authored skill update는 위험한 self-modification이 아니라 PR workflow로 제한될 때 의미가 있다. Agent가 제안하고, transpiler와 CI가 검증하며, human reviewer가 merge하는 구조가 안전한 loop를 만든다.
