---
title: "에이전트는 다른 에이전트를 어떻게 관리하는가: 2026년의 네 가지 서브에이전트 패턴"
date: 2026-05-05
draft: false
source_url: "https://www.philschmid.de/subagent-patterns-2026"
author: "Philipp Schmid"
tags: ["AI", "에이전트", "서브에이전트", "LLM", "오케스트레이션"]
summary: "메인 에이전트가 서브에이전트의 라이프사이클을 통제하는 정도에 따라 정렬한 네 가지 서브에이전트 패턴 — 인라인 툴, 팬아웃, 에이전트 풀, 팀."
---

> **원문:** [How Agents Manage Other Agents: Four Subagents Patterns in 2026](https://www.philschmid.de/subagent-patterns-2026) — Philipp Schmid
> **작성일:** 2026-05-05

작년에 저는 [서브에이전트의 부상](https://www.philschmid.de/the-rise-of-subagents)에 대해, 그리고 자체 컨텍스트·도구·지침을 가진 집중형 에이전트로 작업을 격리하는 것이 신뢰성을 어떻게 향상시키는지에 대해 글을 썼습니다. 그 글은 서브에이전트가 무엇이고 왜 필요한지를 다뤘습니다. 그 이후로 모델은 계획 수립, 도구 사용, 다단계 지침 수행에서 더 좋아졌습니다. 이는 이전에는 너무 취약했던 패턴들 — 영속적인 워커 풀을 관리하는 에이전트나 서로에게 직접 메시지를 보내는 에이전트들 — 을 가능하게 합니다.

다음은 메인 에이전트가 서브에이전트 라이프사이클에 대해 가지는 통제 수준 순서로 정렬한 네 가지 패턴입니다.

## 1. 인라인 툴: 함수 호출로서의 서브에이전트

가장 단순한 패턴입니다. 메인 에이전트는 서브에이전트를 띄우고 그 결과를 툴 응답으로 반환하는 툴을 호출합니다. 메인 에이전트의 관점에서 서브에이전트를 호출하는 것은 `read_file`이나 `run_command`를 호출하는 것과 동일합니다.

```text
┌─────────────┐   call_agent(task)   ┌──────────────┐
│ Main Agent  │ ───────────────────▶ │  Subagent    │
│             │ ◀─────────────────── │  (own ctx)   │
└─────────────┘     tool response    └──────────────┘
```

메인 에이전트는 예를 들어 `call_agent`라는 툴을 가집니다. 작업을 보내고 결과를 받습니다. 서브에이전트는 자체 도구와 지침으로 자신의 컨텍스트에서 실행됩니다. 메인 에이전트는 서브에이전트의 라이프사이클을 직접 관리하지 않습니다.

```json
[
  { "role": "user", "content": "PR #42를 보안 이슈로 검토해줘" },
  { "role": "assistant", "tool_calls": [
    { "name": "call_agent", "arguments": { "task": "PR #42를 보안 이슈로 검토. 인증 변경에 집중.", "agent": "security-reviewer", "tools": ["read_file", "search_code"] } }
  ]},
  { "role": "tool", "name": "call_agent", "content": "2개 이슈 발견: 1) /api/users 엔드포인트에서 인증 토큰이 검증되지 않음. 2) login 핸들러에서 세션 쿠키에 HttpOnly 플래그가 없음." },
  { "role": "assistant", "content": "검토에서 2개의 보안 이슈를 발견했습니다..." }
]
```

이 패턴은 툴 수준에서 동기/비동기 구분이 있는데, 툴 자체가 블로킹하거나 즉시 반환할 수 있기 때문입니다.

**동기(위 예시):** 툴 호출이 블로킹됩니다. 메인 에이전트의 턴은 서브에이전트가 완료될 때까지 일시 중지됩니다. 결과는 일반 툴 응답으로 도착합니다.

**비동기:** 툴은 에이전트 ID와 함께 즉시 반환합니다. 서브에이전트의 결과는 완료되면 알림 메시지로 대화에 주입됩니다. 메인 에이전트는 결과가 도착하기 전에 다른 툴 호출을 할 수 있습니다.

```json
[
  { "role": "user", "content": "PR #42를 검토하고 CI 로그도 확인해줘" },
  { "role": "assistant", "tool_calls": [
    { "name": "call_agent", "arguments": { "task": "PR #42를 보안 이슈로 검토", "agent": "security-reviewer", "background": true } },
    { "name": "read_file", "arguments": { "path": "ci/logs/latest.txt" } }
  ]},
  { "role": "tool", "name": "call_agent", "content": "agent_id: agent-x1. 백그라운드에서 실행 중." },
  { "role": "tool", "name": "read_file", "content": "빌드 통과. 142개 테스트 그린." },
  { "role": "assistant", "content": "CI는 깨끗해 보입니다. 보안 검토를 기다리는 중..." },
  { "role": "user", "content": "<notification agent_id='agent-x1' status='completed'>2개 이슈 발견: ...</notification>" },
  { "role": "assistant", "content": "보안 검토에서 2개의 이슈를 발견했습니다..." }
]
```

동기에서는 툴 응답에 결과가 포함됩니다. 비동기에서는 툴 응답에 ID가 포함되고, 결과는 나중에 주입된 사용자 메시지로 도착합니다.

**언제 사용하나:** 자기 완결적인 작업. 리서치 조회, 코드 리뷰, 파일 분석, 테스트 생성. 대부분의 서브에이전트 사용 사례는 여기서 시작하고 여기에 머뭅니다.

**한계:** 더 작고 저렴한 모델을 포함해 도구 사용을 지원하는 모든 모델과 작동합니다. 결과는 단일 툴 응답(동기) 또는 주입된 알림 메시지(비동기)로 도착합니다. 후속 지침을 보내거나, 진행 상황을 확인하거나, 조기에 취소할 방법이 없습니다. 서브에이전트가 작업을 잘못 이해하면 결과가 돌아올 때 알게 됩니다.

## 2. 팬아웃(Fan-Out): 에이전트를 띄우고 결과를 기다리기

메인 에이전트가 서브에이전트들을 띄우고 `wait_agent` 툴을 사용해 결과를 수집합니다. 인라인 툴과 달리, 띄우기와 수집은 별도의 단계입니다. `spawn_agent`는 항상 즉시 반환합니다. 모델은 다음에 무엇을 할지 결정합니다 — 즉시 `wait_agent`를 호출하거나, 자체 작업을 먼저 하거나, 대기 전에 더 많은 에이전트를 띄울 수 있습니다.

```text
                    spawn_agent(A) ─────▶ ┌──────────┐
                                          │ Agent A  │
┌─────────────┐    spawn_agent(B) ─────▶ ┌──────────┐
│ Main Agent  │                          │ Agent B  │
│             │    spawn_agent(C) ─────▶ ┌──────────┐
└──────┬──────┘                          │ Agent C  │
       │                                  └────┬─────┘
       │            wait_agent()               │
       └◀──────────────────────────────────────┘
                  (results in batch)
```

두 개의 툴: `spawn_agent`는 작업을 디스패치하고 ID와 함께 즉시 반환합니다. `wait_agent`는 하나 이상의 에이전트가 완료될 때까지 블로킹됩니다.

모델이 시퀀싱을 통제합니다. 에이전트들을 띄우고 즉시 `wait_agent`를 호출(사실상 동기)하거나, 자체 작업을 먼저 인터리브할 수 있습니다.

```json
[
  { "role": "user", "content": "auth 모듈을 리팩터링하고 관련된 모든 테스트를 업데이트해줘" },
  { "role": "assistant", "tool_calls": [
    { "name": "spawn_agent", "arguments": { "task": "JWT 토큰을 사용하도록 auth 모듈 리팩터링", "agent": "backend-engineer" } },
    { "name": "spawn_agent", "arguments": { "task": "새로운 JWT 흐름에 맞춰 모든 auth 관련 테스트 업데이트", "agent": "test-writer" } },
    { "name": "read_file", "arguments": { "path": "docs/auth-spec.md" } }
  ]},
  { "role": "tool", "name": "spawn_agent", "content": "agent-a (backend-engineer) 띄움. 실행 중." },
  { "role": "tool", "name": "spawn_agent", "content": "agent-b (test-writer) 띄움. 실행 중." },
  { "role": "tool", "name": "read_file", "content": "# Auth Spec\nRS256 JWT 토큰..." },
  { "role": "assistant", "content": "두 작업을 시작했습니다. auth 스펙은 RS256을 사용해야 함을 확인했습니다." },
  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": { "timeout": 300 } }]},
  { "role": "tool", "name": "wait_agent", "content": "2개 에이전트 완료:\n- agent-a: 3개 파일 리팩터링 (auth.ts, middleware.ts, config.ts)\n- agent-b: 12개 테스트 업데이트, 모두 통과" },
  { "role": "assistant", "content": "두 작업 모두 완료되었습니다. auth 모듈은 이제 JWT를 사용합니다..." }
]
```

모델은 동일한 툴 호출에서 두 개의 에이전트를 띄우고 파일을 읽었으며, 그런 다음 대기하기로 결정했습니다. 다른 모델은 띄운 직후에 즉시 `wait_agent`를 호출하거나, 먼저 여러 번의 읽기를 할 수도 있습니다. 툴 표면은 동일하며, 모델이 인터리빙을 결정합니다.

패턴 1과의 차이: 모델이 언제 수집할지 통제합니다. 5개의 에이전트를 병렬로 띄우고, 자체 파일 읽기를 한 다음, `wait_agent`를 호출할 수 있습니다. `wait_agent`는 서브에이전트 완료 시 깨어나 사용 가능한 모든 결과를 반환하는 글로벌 메일박스 역할을 할 수 있습니다.

**언제 사용하나:** 동시에 실행할 수 있는 여러 독립적인 작업. 메인 에이전트가 한 서브에이전트의 중간 결과 없이 다른 서브에이전트를 시작할 수 있을 때.

**한계:** 모델이 언제 대기할지 올바르게 결정해야 합니다. 띄울 때마다 즉시 `wait_agent`를 호출하는 모델은 패턴 1보다 이점이 없습니다. 가치는 모델이 띄우기와 대기 사이에 자체 작업을 인터리브하는 능력에 달려 있습니다. 결과는 마지막 호출 이후 완료된 모든 에이전트 출력을 반환하는 `wait_agent`를 통해 일괄 수집됩니다. 여전히 발사 후 망각(fire-and-forget) 방식이며, 서브에이전트에게 후속 지침을 보내거나 작업 중간에 코스를 수정할 방법이 없습니다.

## 3. 에이전트 풀: 메시징을 가진 영속적인 에이전트

메인 에이전트는 장수명 서브에이전트들을 띄우고 메시지를 통해 그들과 소통합니다. 에이전트들은 상호작용 간에 영속됩니다. 메인 에이전트는 후속 지침을 보내고, 상태를 확인하고, 에이전트 간의 작업을 조율할 수 있습니다.

이는 더 풍부한 툴 표면을 필요로 합니다: `spawn_agent`, `send_message`, `wait_agent`, `list_agents`, `kill_agent`.

```text
                send_message ──▶ ┌──────────────┐
                                 │  Agent A     │
                ◀── response ─── │ (stateful)   │
┌─────────────┐                  └──────────────┘
│ Main Agent  │  send_message ──▶ ┌──────────────┐
│ (coordinator)│                  │  Agent B     │
└─────────────┘ ◀── response ─── │ (stateful)   │
                                 └──────────────┘
   tools: spawn_agent, send_message, wait_agent,
          list_agents, kill_agent
```

패턴 2와 달리, 여기서 에이전트는 상태를 가지며 상호작용형입니다. 메인 에이전트는 메시지를 보내고, 응답을 받고, 같은 에이전트에게 또 다른 메시지를 보냅니다. 에이전트는 전체 대화 기록을 유지합니다. 이는 메인 에이전트가 전문가들 사이를 조율하는 다단계 워크플로우를 지원합니다.

모델은 한 번에 하나의 에이전트와 작업할지(순차적) 또는 대기 사이에 여러 에이전트에게 메시지를 보낼지(병렬) 통제합니다. 리서처와 작가에게 동시에 보내거나, 리서처를 먼저 기다릴 수 있습니다.

```json
[
  { "role": "user", "content": "WebAssembly 성능에 대한 블로그 포스트를 써줘" },

  { "role": "assistant", "tool_calls": [
    { "name": "spawn_agent", "arguments": { "role": "researcher", "tools": ["web_search", "read_url"] }},
    { "name": "spawn_agent", "arguments": { "role": "writer", "tools": ["write_file", "read_file"] }}
  ]},
  { "role": "tool", "name": "spawn_agent", "content": "agent-r (researcher) 띄움" },
  { "role": "tool", "name": "spawn_agent", "content": "agent-w (writer) 띄움" },

  { "role": "assistant", "tool_calls": [
    { "name": "send_message", "arguments": { "to": "agent-r", "message": "WebAssembly 성능 벤치마크를 리서치. 구체적인 수치가 있는 5개 출처를 찾아줘." } },
    { "name": "send_message", "arguments": { "to": "agent-w", "message": "WebAssembly 성능에 대한 블로그 포스트 구조를 잡아줘. 4개 섹션." } }
  ]},
  { "role": "tool", "name": "send_message", "content": "agent-r에 전달됨" },
  { "role": "tool", "name": "send_message", "content": "agent-w에 전달됨" },

  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": {} }]},
  { "role": "tool", "name": "wait_agent", "content": "agent-w 응답: 개요 준비 완료: 도입, 벤치마크, 실제 사례, 결론" },

  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": {} }]},
  { "role": "tool", "name": "wait_agent", "content": "agent-r 응답: 5개 출처 발견: 1) Chrome 벤치마크는 네이티브 속도의 1.2배..." },

  { "role": "assistant", "tool_calls": [{ "name": "send_message", "arguments": { "to": "agent-w", "message": "이 출처들을 사용해 개요를 채워줘: 1) Chrome 벤치마크는 네이티브 속도의 1.2배..." } }]},
  { "role": "tool", "name": "send_message", "content": "agent-w에 전달됨" },

  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": {} }]},
  { "role": "tool", "name": "wait_agent", "content": "agent-w 응답: 초안 완료. 제목: 'WebAssembly Is Faster Than You Think'..." },

  { "role": "assistant", "tool_calls": [{ "name": "send_message", "arguments": { "to": "agent-r", "message": "이 초안을 너의 출처와 대조해 사실 확인: 'WebAssembly Is Faster Than You Think'..." } }]},
  { "role": "tool", "name": "send_message", "content": "agent-r에 전달됨" },

  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": {} }]},
  { "role": "tool", "name": "wait_agent", "content": "agent-r 응답: 2개 수정 사항: 3번째 단락은 2배 속도라고 인용했지만 출처는 1.5배라고 함..." },

  { "role": "assistant", "tool_calls": [
    { "name": "send_message", "arguments": { "to": "agent-w", "message": "이 수정 사항들을 적용해줘: 3번째 단락은 2배가 아니라 1.5배여야 함..." } },
    { "name": "kill_agent", "arguments": { "agent_id": "agent-r" }}
  ]},
  { "role": "tool", "name": "send_message", "content": "agent-w에 전달됨" },
  { "role": "tool", "name": "kill_agent", "content": "agent-r 종료됨" },

  { "role": "assistant", "content": "최종 포스트는 다음과 같습니다..." }
]
```

agent-r은 두 번 메시지를 받고(리서치, 그 다음 사실 확인) 첫 번째 작업의 출처를 유지합니다. 모델은 시작에서 두 에이전트에게 병렬로 작업을 보낸 다음, 사실 확인을 위해 순차적으로 조율했습니다. 다른 모델은 모든 것을 직렬화할 수도 있습니다. 툴은 동일하며, 모델이 오케스트레이션을 통제합니다.

결과는 `wait_agent`를 통해 메시지별로 도착합니다. `wait_agent`에 대한 각 호출은 다음 에이전트 응답을 반환하므로, 메인 에이전트는 결과를 점진적으로 처리하고 돌아온 내용에 따라 다음 메시지를 조정할 수 있습니다.

**언제 사용하나:** 에이전트들이 협업해야 하는 다단계 워크플로우. 메인 에이전트가 전문가들 사이에서 정보를 라우팅합니다.

**한계:** 메인 에이전트는 여러 에이전트 상태를 추적하고, 후속 메시지를 보낼지 대기할지 결정하고, 정보를 올바르게 라우팅해야 합니다. 더 작은 모델은 어떤 에이전트가 어떤 컨텍스트를 가졌는지 추적을 잃거나, 완료 시 `kill_agent` 호출을 잊어버립니다. 프론티어 모델은 2-4개의 에이전트를 그럭저럭 처리할 수 있습니다.

## 4. 팀: 에이전트들이 서로 대화하기

에이전트들이 메인 에이전트를 거치지 않고 서로에게 직접 메시지를 보냅니다. 메인 에이전트는 팀을 설정하고, 역할을 정의하고, 한 발 물러납니다. 에이전트들은 직접 메시징이나 공유 메일박스를 사용해 자기들끼리 조율합니다.

```text
┌─────────────┐   kickoff   ┌──────────────┐
│ Main Agent  │ ──────────▶ │   Planner    │
│ (supervisor)│             └───┬──────┬───┘
└─────────────┘                 │      │
       ▲                send_msg│      │send_msg
       │ final report           ▼      ▼
       │                ┌────────────┐  ┌────────────┐
       │                │ Implementer│◀▶│  Reviewer  │
       └─── reports ─── └────────────┘  └────────────┘
                         (agents talk to each other)
```

툴 표면에 교차 에이전트 어드레싱이 포함됩니다. 각 에이전트는 자체 툴 셋에 `send_message`를 가지며 이름이나 경로로 다른 에이전트를 어드레싱할 수 있습니다.

메인 에이전트의 관점에서 대화는 짧습니다. 팀을 설정하고, 플래너를 시작시키고, 최종 보고서를 기다립니다. 모델은 조용히 대기하거나, `list_agents`를 사용해 주기적으로 확인할 수 있습니다.

```json
[
  { "role": "user", "content": "기능 X를 빌드해줘" },

  { "role": "assistant", "tool_calls": [
    { "name": "spawn_agent", "arguments": { "role": "planner", "tools": ["read_file", "search_code", "send_message"] } },
    { "name": "spawn_agent", "arguments": { "role": "implementer", "tools": ["read_file", "write_file", "run_command", "send_message"] } },
    { "name": "spawn_agent", "arguments": { "role": "reviewer", "tools": ["read_file", "search_code", "send_message"] } }
  ]},
  { "role": "tool", "name": "spawn_agent", "content": "agent-p (planner) 띄움" },
  { "role": "tool", "name": "spawn_agent", "content": "agent-i (implementer) 띄움" },
  { "role": "tool", "name": "spawn_agent", "content": "agent-v (reviewer) 띄움" },

  { "role": "assistant", "tool_calls": [{ "name": "send_message", "arguments": { "to": "agent-p", "message": "기능 X를 계획하고 조율해줘. 너의 팀원: agent-i (implementer), agent-v (reviewer). 그들에게 직접 메시지를 보내. 완료되면 나에게 보고해." } }]},
  { "role": "tool", "name": "send_message", "content": "agent-p에 전달됨" },

  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": { "timeout": 60 } }]},
  { "role": "tool", "name": "wait_agent", "content": "타임아웃. 응답한 에이전트 없음." },

  { "role": "assistant", "tool_calls": [{ "name": "list_agents", "arguments": {} }]},
  { "role": "tool", "name": "list_agents", "content": "agent-p: 실행 중, agent-i: 실행 중, agent-v: 유휴" },

  { "role": "assistant", "tool_calls": [{ "name": "wait_agent", "arguments": { "timeout": 120 } }]},
  { "role": "tool", "name": "wait_agent", "content": "agent-p 응답: 기능 X 완료. 3개 파일 변경, 모든 테스트 통과. 요약: ..." },

  { "role": "assistant", "content": "기능 X가 빌드되었습니다. 수행된 작업은 다음과 같습니다..." }
]
```

플래너가 구현자에게 메시지를 보내고, 구현자가 리뷰어에게 코드를 보내고, 리뷰어가 수정을 요청하는 모든 일이 에이전트들 자신의 대화 안에서 일어납니다. 메인 에이전트의 컨텍스트는 깨끗하게 유지됩니다. 모델은 타임아웃 후 `list_agents`로 확인했습니다. 타임아웃 없이 `wait_agent`를 호출하고 완료까지 블로킹할 수도 있었습니다.

메인 에이전트는 에이전트가 명시적으로 메시지를 보내올 때만 결과를 수집합니다(여기서는 플래너가 완료를 보고함). 그 외 모든 것은 메인 에이전트에게 보이지 않습니다. 구현은 교차 에이전트 어드레싱이 어떻게 작동하는지에 따라 다양합니다: 계층적 경로(`/root/planner`에서 `/root/implementer`로), 파일 기반 메일박스, 또는 IPC 프로토콜.

**언제 사용하나:** 단일 에이전트가 단계별로 관리할 수 있는 것을 넘어서는 조율 로직이 필요한 큰 작업.

**한계:** 메인 에이전트뿐만 아니라 팀의 모든 에이전트가 프론티어급 모델 능력을 필요로 합니다. 각 팀원은 언제 팀원에게 메시지를 보낼지, 무엇을 포함할지, 언제 보고할지를 독립적으로 결정해야 합니다. 모델은 잘못된 에이전트에게 메시지를 보내거나, 완료 보고를 잊거나, 루프에 빠질 수 있습니다. 모델 능력 외에도 인프라 과제가 있습니다: 사이클 감지(A가 B를 기다리고, B가 A를 기다림), 충돌 해결(두 에이전트가 같은 파일을 편집), 그리고 셧다운 조율. 에이전트 간 메시지 체인은 추적하기 어렵고 실패가 연쇄적으로 일어나기 때문에 디버깅이 어렵습니다.

## 패턴 선택하기

| 패턴 | 툴 | 메인 에이전트 역할 | 에이전트 수명 |
|------|-----|----------------|----------|
| 인라인 툴 | `call_agent` | 호출자 | 단일 작업 |
| 팬아웃 | `spawn_agent`, `wait_agent` | 디스패처 | 단일 작업 |
| 에이전트 풀 | `spawn`, `send`, `wait`, `list`, `kill` | 코디네이터 | 다중 턴 |
| 팀 | 위의 모든 것 + 교차 에이전트 `send_message` | 슈퍼바이저 | 영속적 |

패턴 1로 시작하세요. 다중 에이전트 시스템이 필요하다고 느끼는 대부분의 작업은 잘 프롬프팅된 인라인 툴 호출로 잘 작동합니다. 진정으로 독립적인 병렬 작업에는 패턴 2로 이동하세요. 에이전트들이 여러 단계에 걸쳐 협업해야 할 때는 패턴 3으로 이동하세요. 패턴 4는 조율 로직이 단일 에이전트가 관리할 수 있는 것을 넘어설 때를 위한 것입니다.

각 단계 상승은 더 능력 있는 모델을 필요로 합니다. 패턴 1은 도구를 호출할 수 있는 모든 모델과 작동합니다. 패턴 2는 언제 대기할지 추론하는 모델이 필요합니다. 패턴 3은 턴에 걸쳐 다중 에이전트 상태를 추적하는 모델이 필요합니다. 패턴 4는 모든 에이전트에 대해 프론티어 모델이 필요합니다. 더 작거나 저렴한 모델로는 패턴 1 또는 2에 머무세요.

결과 수집도 패턴에 따라 달라집니다. 패턴 1은 결과를 툴 응답으로 인라인 반환합니다. 패턴 2는 `wait_agent`를 통해 결과를 일괄 처리합니다. 패턴 3은 결과를 점진적으로 전달합니다. 패턴 4는 에이전트가 명시적으로 보고하는 것만 표면화하며, 그 외 모든 것은 에이전트 간 대화 안에 남아 있습니다.

패턴 2-4의 경우, `spawn_agent`는 항상 즉시 반환하고 `wait_agent`는 모델이 호출하기로 결정할 때 결과를 수집합니다. 프레임워크는 툴을 제공합니다. 모델은 오케스트레이션을 통제합니다. 오늘 4개의 조율된 에이전트가 필요한 작업은 내일 더 좋은 모델을 가진 단일 에이전트로 해결 가능할 수 있습니다.
