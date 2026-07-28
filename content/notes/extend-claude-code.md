---
title: "Claude Code 확장하기: CLAUDE.md, Skills, Subagents, Hooks, MCP, Plugins"
date: 2026-07-28
draft: false
source_url: "https://code.claude.com/docs/en/features-overview"
author: "Anthropic"
tags: ["AI", "Claude Code", "Agents", "Developer Tools", "MCP"]
summary: "Claude Code의 extension layer를 CLAUDE.md, Skills, Code intelligence, MCP, Subagents, Agent teams, Hooks, Plugins 관점에서 정리한다. 각 feature의 목적, trigger, context cost, layering 방식, 조합 패턴을 practitioner 관점에서 설명한다."
---

> **원문:** [Extend Claude Code](https://code.claude.com/docs/en/features-overview) — Anthropic Claude Code Docs
>
> 아래 글은 원문 문서의 구조와 서술을 따라가며 한국어로 옮긴 것이다. Claude Code의 feature 이름, command, 설정 파일명, agent/workflow 용어는 실무에서 쓰는 English form을 기본으로 유지했다.

Claude Code는 코드에 대해 reasoning하는 model과 file operation, search, execution, web access를 위한 [built-in tools](https://code.claude.com/docs/en/how-claude-code-works#tools)를 결합한다. Built-in tools만으로도 대부분의 coding task를 다룰 수 있다. 이 문서는 그 위의 extension layer, 즉 Claude가 무엇을 알아야 하는지 customize하고, external service에 연결하고, workflow를 automate하기 위해 추가하는 feature들을 다룬다.

> Core agentic loop가 어떻게 작동하는지는 [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)를 참고한다.

Claude Code를 처음 쓴다면 project convention은 [CLAUDE.md](https://code.claude.com/docs/en/memory)에서 시작하고, 이후 [구체적인 trigger가 생길 때](#setup을-시간에-따라-키우기) 다른 extension을 추가하는 편이 좋다.

## Overview

Extension은 agentic loop의 서로 다른 지점에 연결된다.

- [CLAUDE.md](https://code.claude.com/docs/en/memory)는 모든 session에서 Claude가 보는 persistent context를 추가한다.
- [Skills](https://code.claude.com/docs/en/skills)는 reusable knowledge와 호출 가능한 workflow를 추가한다.
- [Code intelligence](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior)는 Claude를 language server에 연결해 symbol-level navigation과 live type error를 제공한다.
- [MCP](https://code.claude.com/docs/en/mcp)는 Claude를 external service와 tool에 연결한다.
- [Subagents](https://code.claude.com/docs/en/sub-agents)는 isolated context에서 독립 loop를 실행하고 summary를 반환한다.
- [Agent teams](https://code.claude.com/docs/en/agent-teams)는 shared task와 peer-to-peer messaging으로 여러 독립 session을 coordinate한다.
- [Hooks](https://code.claude.com/docs/en/hooks-guide)는 lifecycle event에서 fire되며 script, HTTP request, prompt, subagent를 실행할 수 있다.
- [Plugins](https://code.claude.com/docs/en/plugins)와 [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)는 이런 feature를 package하고 배포한다.

Skills는 가장 flexible한 extension이다. Skill은 knowledge, workflow, instruction을 담은 markdown file이다. `/deploy` 같은 command로 호출할 수도 있고, Claude가 관련성이 있다고 판단하면 자동으로 load할 수도 있다. Skill은 현재 conversation 안에서 실행될 수도 있고, subagent를 통해 isolated context에서 실행될 수도 있다.

## Goal에 맞는 feature 고르기

Feature는 모든 session에서 Claude가 보는 always-on context부터, 사용자나 Claude가 필요할 때 호출하는 on-demand capability, 특정 event에서 실행되는 background automation까지 폭이 넓다. 아래 table은 어떤 feature가 있고, 언제 적합한지 정리한다.

| Feature | 하는 일 | 언제 쓰나 | 예시 |
| --- | --- | --- | --- |
| CLAUDE.md | 모든 conversation에 load되는 persistent context | Project convention, “항상 X를 하라”는 rule | “npm이 아니라 pnpm을 써라. Commit 전에 test를 실행하라.” |
| Skill | Claude가 사용할 수 있는 instruction, knowledge, workflow | Reusable content, reference docs, 반복 task | `/deploy`가 deploy checklist를 실행한다. API docs skill이 endpoint pattern을 담는다. |
| Subagent | Summary를 반환하는 isolated execution context | Context isolation, parallel task, specialized worker | 많은 file을 읽는 research task가 핵심 finding만 반환한다. |
| [Agent teams](https://code.claude.com/docs/en/agent-teams) | 여러 독립 Claude Code session을 coordinate | Parallel research, new feature development, competing hypothesis debugging | Security, performance, test reviewer를 동시에 spawn한다. |
| [Code intelligence](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior) | Language-server navigation과 diagnostics | Typed language, grep이 느리거나 부정확한 large codebase | 전체 file을 읽지 않고 symbol definition으로 jump한다. |
| MCP | External service에 연결 | External data 또는 action | Database query, Slack post, browser control |
| Hook | Event가 trigger하는 script, HTTP request, prompt, subagent | 매번 동일하게 실행되어야 하는 automation | File edit 후 ESLint 실행 |
| [Artifact](https://code.claude.com/docs/en/artifacts) | Session output을 private interactive web page로 publish | Terminal text보다 visual하게 보거나 공유해야 하는 output | Claude가 조사하면서 update하는 incident timeline |

[Plugins](https://code.claude.com/docs/en/plugins)는 packaging layer다. Plugin은 skills, hooks, subagents, MCP servers를 하나의 installable unit으로 묶는다. Plugin skill은 `/my-plugin:review`처럼 namespace를 갖기 때문에 여러 plugin이 공존할 수 있다. 같은 setup을 여러 repository에서 재사용하거나 [marketplace](https://code.claude.com/docs/en/plugin-marketplaces)를 통해 다른 사람에게 배포하고 싶을 때 plugin을 쓴다.

### Setup을 시간에 따라 키우기

모든 것을 처음부터 configure할 필요는 없다. 각 feature에는 알아보기 쉬운 trigger가 있으며, 대부분의 team은 대략 다음 순서로 추가한다.

| Trigger | 추가할 것 |
| :--- | :--- |
| Claude가 convention이나 command를 두 번 틀린다 | [CLAUDE.md](https://code.claude.com/docs/en/memory)에 추가한다. |
| Task를 시작할 때 같은 prompt를 계속 입력한다 | 사용자 호출용 [skill](https://code.claude.com/docs/en/skills)로 저장한다. |
| 같은 playbook이나 multi-step procedure를 chat에 세 번째로 붙여 넣는다 | [skill](https://code.claude.com/docs/en/skills)로 capture한다. |
| Claude가 볼 수 없는 browser tab에서 data를 계속 복사한다 | 그 system을 [MCP server](https://code.claude.com/docs/en/mcp)로 연결한다. |
| Claude가 symbol 정의나 사용처를 찾기 위해 많은 file을 읽는다 | 해당 language용 [code intelligence plugin](https://code.claude.com/docs/en/discover-plugins#code-intelligence)을 설치한다. |
| Side task가 다시 참고하지 않을 output으로 conversation을 flood한다 | [subagent](https://code.claude.com/docs/en/sub-agents)를 통해 route한다. |
| 매번 묻지 않아도 어떤 일이 일어나길 원한다 | [hook](https://code.claude.com/docs/en/hooks-guide)을 작성한다. |
| 두 번째 repository에도 같은 setup이 필요하다 | [plugin](https://code.claude.com/docs/en/plugins)으로 package한다. |

같은 trigger는 이미 가진 것을 언제 update해야 하는지도 알려준다. 반복되는 mistake나 recurring review comment는 chat에서 한 번 correction할 것이 아니라 CLAUDE.md edit이다. 계속 손으로 tweak하는 workflow는 새 revision이 필요한 skill이다.

### 비슷한 feature 비교하기

서로 비슷해 보이는 feature들이 있다. 더 긴 guide는 blog 글 [Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)를 참고한다. 아래는 구분 기준이다.

#### Skill vs Subagent

Skills와 subagents는 다른 문제를 푼다.

- Skills는 어떤 context에도 load할 수 있는 reusable content다.
- Subagents는 main conversation과 분리되어 실행되는 isolated worker다.

| Aspect | Skill | Subagent |
| --- | --- | --- |
| What it is | Reusable instruction, knowledge, workflow | 자체 context를 가진 isolated worker |
| Key benefit | Context 전반에 content 공유 | Context isolation. 작업은 별도로 일어나고 summary만 돌아온다. |
| [Context window](https://code.claude.com/docs/en/context-window) impact | Main window에 추가된다. | 자체 input/output token을 가진 별도 window를 쓴다. |
| Best for | Reference material, invocable workflow | 많은 file을 읽는 task, parallel work, specialized worker |

Skills는 reference일 수도 있고 action일 수도 있다. Reference skill은 API style guide처럼 session 내내 Claude가 활용할 knowledge를 제공한다. Action skill은 `/deploy`가 deployment workflow를 실행하는 것처럼 Claude에게 특정 일을 하라고 알려준다.

Context isolation이 필요하거나 context window가 가득 차고 있을 때 subagent를 사용한다. Subagent는 수십 개 file을 읽거나 광범위한 search를 실행할 수 있지만, main conversation에는 summary만 돌아온다. Intermediate work가 main context에 남을 필요가 없을 때도 유용하다. Custom subagent는 자체 instruction을 가질 수 있고, skill을 preload할 수도 있다.

둘은 함께 쓸 수 있다. Subagent는 `skills:` field로 특정 skill을 preload할 수 있다. Skill은 `context: fork`를 사용해 isolated context에서 실행될 수 있다. 자세한 내용은 [Skills](https://code.claude.com/docs/en/skills)를 참고한다.

#### CLAUDE.md vs Skill

둘 다 instruction을 저장하지만 load 방식과 목적이 다르다.

| Aspect | CLAUDE.md | Skill |
| --- | --- | --- |
| Loads | Every session, automatically | On demand |
| Can include files | 가능, `@path` import 사용 | 가능, `@path` import 사용 |
| Can trigger workflows | 아니오 | 가능, `/<name>` 사용 |
| Best for | “항상 X를 하라”는 rule | Reference material, invocable workflow |

Claude가 항상 알아야 하는 내용이면 CLAUDE.md에 둔다. 예를 들어 coding convention, build command, project structure, “never do X” rule이다.

Claude가 가끔만 필요한 reference material(API docs, style guide)이거나 `/<name>`으로 trigger하는 workflow(deploy, review, release)라면 skill에 둔다.

Rule of thumb: CLAUDE.md는 200 lines 아래로 유지한다. 길어지면 reference content를 skills로 옮기거나 [`.claude/rules/`](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/) file로 나눈다.

#### CLAUDE.md vs Rules vs Skills

세 가지 모두 instruction을 저장하지만 load 방식은 다르다.

| Aspect | CLAUDE.md | `.claude/rules/` | Skill |
| --- | --- | --- | --- |
| Loads | Every session | Every session, 또는 matching file이 열릴 때 | On demand, invoked 또는 relevant할 때 |
| Scope | Whole project | File path로 scoped 가능 | Task-specific |
| Best for | Core convention과 build command | Language-specific 또는 directory-specific guideline | Reference material, repeatable workflow |

CLAUDE.md는 모든 session이 알아야 하는 instruction, 즉 build command, test convention, project architecture에 쓴다.

Rules는 CLAUDE.md를 focused하게 유지하는 데 쓴다. [`paths` frontmatter](https://code.claude.com/docs/en/memory#path-specific-rules)가 있는 rule은 Claude가 matching file을 다룰 때만 load되므로 context를 절약한다.

Skills는 Claude가 가끔만 필요한 content, 예를 들어 API documentation이나 `/<name>`으로 trigger하는 deployment checklist에 쓴다.

#### Subagent vs Agent team

둘 다 work를 parallelize하지만 architecture가 다르다.

- Subagents는 session 안에서 실행되고 result를 main context에 보고한다.
- Agent teams는 서로 직접 message를 주고받는 독립 Claude Code session이다.

| Aspect | Subagent | Agent team |
| --- | --- | --- |
| Context | 자체 context window, result는 caller에게 반환 | 자체 context window, 완전히 독립 |
| Communication | Main agent에게만 result 보고 | Teammate끼리 직접 message |
| Coordination | Main agent가 모든 work를 관리 | Shared task list로 self-coordination |
| Best for | Result만 중요한 focused task | Discussion과 collaboration이 필요한 complex work |
| Token cost | 낮음: result가 main context로 summarize됨 | 높음: 각 teammate가 separate Claude instance |

빠르고 focused된 worker가 필요할 때 subagent를 쓴다. 예: 질문 조사, claim verification, file review. Subagent가 작업하고 summary를 반환하므로 main conversation이 clean하게 유지된다.

Teammate들이 finding을 공유하고, 서로 challenge하며, 독립적으로 coordinate해야 한다면 agent team을 쓴다. Agent teams는 competing hypothesis가 있는 research, parallel code review, 각 teammate가 separate piece를 맡는 new feature development에 적합하다.

Transition point: parallel subagent를 돌리다가 context limit에 부딪히거나 subagent끼리 communication이 필요해지면 agent team이 자연스러운 다음 단계다.

> Agent teams는 experimental이며 기본적으로 disabled다. Setup과 현재 limitation은 [agent teams](https://code.claude.com/docs/en/agent-teams)를 참고한다.

#### MCP vs Skill

MCP는 Claude를 external service에 연결한다. Skills는 Claude가 아는 것을 확장하며, 여기에는 그런 service를 효과적으로 사용하는 방법도 포함된다.

| Aspect | MCP | Skill |
| --- | --- | --- |
| What it is | External service에 연결하기 위한 protocol | Knowledge, workflow, reference material |
| Provides | Tools와 data access | Knowledge, workflow, reference material |
| Examples | Slack integration, database query, browser control | Code review checklist, deploy workflow, API style guide |

둘은 서로 다른 문제를 풀며 함께 잘 동작한다.

MCP는 Claude에게 external system용 purpose-built tools를 제공한다. Connection과 authentication은 server가 처리한다.

Skills는 Claude에게 그 tools를 효과적으로 사용하는 방법과 `/<name>`으로 trigger할 수 있는 workflow를 제공한다. 예를 들어 skill은 team의 database schema와 query pattern, 또는 team message formatting rule을 담은 `/post-to-slack` workflow를 포함할 수 있다.

예: MCP server가 Claude를 database에 연결한다. Skill은 Claude에게 data model, common query pattern, task별로 어떤 table을 써야 하는지를 알려준다.

#### Hook vs Skill

Hook은 lifecycle event에서 fire된다. Skill은 Claude가 읽고 적용할 context로 load된다.

| Aspect | Hook | Skill |
| --- | --- | --- |
| Runs | Shell command, HTTP request, LLM prompt, subagent | Claude가 읽고 따르는 instruction |
| Triggered by | `PostToolUse`, `SessionStart` 같은 [lifecycle events](https://code.claude.com/docs/en/hooks#hook-events) | 사용자가 `/<name>`을 입력하거나 Claude가 description을 task에 match |
| Determinism | event에서 항상 fire되며 trigger가 보장됨 | Claude가 instruction을 해석하므로 outcome이 달라질 수 있음 |
| Context cost | Hook이 output을 반환하지 않으면 zero | Description은 session마다 load, full content는 사용 시 load |
| Best for | Edit 후 linting, unsafe command blocking, logging, notification | Reasoning이 필요한 workflow, reference material, multi-step task |

Action이 매번 같은 방식으로 일어나야 하고 Claude의 reasoning이 필요 없다면 hook을 쓴다. 예: format on save, `rm -rf /` reject, session end 때 Slack message post.

Claude가 step을 어떻게 적용할지 판단해야 하거나 content가 script가 아니라 knowledge라면 skill을 쓴다. 예: `/release` checklist, API style guide, debugging playbook.

Guardrail은 hook에 둔다. “`.env`를 절대 edit하지 말라”는 instruction은 CLAUDE.md나 skill에 있으면 request일 뿐 guarantee가 아니다. Edit를 block하는 `PreToolUse` hook이 enforcement다. Rule이 매번 반드시 지켜져야 한다면 prompt instruction보다 hook으로 만든다.

Hook output은 context에 들어간다. Linter를 실행하는 `PostToolUse` hook은 Claude가 읽을 text result를 feed한다. `/fix-lint` skill은 Claude에게 그 결과를 어떻게 해결할지 알려준다.

### Feature가 layer되는 방식 이해하기

Feature는 user-wide, per-project, plugin, managed policy 등 여러 level에서 정의될 수 있다. Subdirectory에 CLAUDE.md file을 중첩하거나 monorepo의 특정 package에 skill을 둘 수도 있다. 같은 feature가 여러 level에 있으면 다음 방식으로 layer된다.

- CLAUDE.md files는 additive하다. 모든 level이 동시에 Claude context에 contribution한다. Working directory와 그 상위 directory의 file은 launch 때 load되고, subdirectory file은 Claude가 그 안에서 작업할 때 load된다. Instruction이 conflict하면 Claude가 판단해 reconcile하며, 보통 더 specific한 instruction이 우선한다. [CLAUDE.md files가 load되는 방식](https://code.claude.com/docs/en/memory#how-claude-md-files-load)을 참고한다.
- Skills와 subagents는 name으로 override된다. 같은 name이 여러 level에 있으면 priority에 따라 하나가 이긴다. Skills는 managed > user > project, subagents는 managed > CLI flag > project > user > plugin 순서다. Plugin skills는 conflict를 피하기 위해 [namespaced](https://code.claude.com/docs/en/plugins#add-skills-to-your-plugin)된다. [skill discovery](https://code.claude.com/docs/en/skills#where-skills-live)와 [subagent scope](https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope)를 참고한다.
- MCP servers는 name으로 override된다. Priority는 local > project > user다. [MCP scope](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence)를 참고한다.
- Hooks는 merge된다. Source와 관계없이 matching event에 등록된 모든 hook이 fire된다. [hooks](https://code.claude.com/docs/en/hooks)를 참고한다.

### Feature 조합하기

각 extension은 다른 문제를 푼다. CLAUDE.md는 always-on context, skills는 on-demand knowledge와 workflow, MCP는 external connection, subagents는 isolation, hooks는 automation을 맡는다. 실제 setup은 workflow에 맞춰 이들을 조합한다.

예를 들어 project convention에는 CLAUDE.md를, deployment workflow에는 skill을, database connection에는 MCP를, edit 후 linting에는 hook을 쓸 수 있다. 각 feature가 자신에게 가장 잘 맞는 일을 맡는 구조다.

| Pattern | 작동 방식 | 예시 |
| --- | --- | --- |
| Skill + MCP | MCP가 connection을 제공하고, skill이 Claude에게 잘 쓰는 법을 알려준다. | MCP는 database에 연결하고, skill은 schema와 query pattern을 문서화한다. |
| Skill + Subagent | Skill이 parallel work를 위해 subagents를 spawn한다. | `/audit` skill이 security, performance, style subagents를 isolated context에서 실행한다. |
| CLAUDE.md + Skills | CLAUDE.md는 always-on rule을, skills는 on-demand reference material을 담는다. | CLAUDE.md는 “우리 API convention을 따르라”고 말하고, skill은 full API style guide를 담는다. |
| Hook + MCP | Hook이 MCP를 통해 external action을 trigger한다. | Post-edit hook이 Claude가 critical file을 modify하면 Slack notification을 보낸다. |

## Context cost 이해하기

추가하는 모든 feature는 Claude의 context를 소비한다. 너무 많으면 context window를 채울 뿐 아니라 noise를 늘려 Claude를 덜 효과적으로 만들 수 있다. Skills가 제대로 trigger되지 않거나 Claude가 convention을 놓칠 수도 있다. 이 trade-off를 이해하면 효과적인 setup을 만들 수 있다. Feature들이 running session에서 어떻게 결합되는지 interactive하게 보고 싶다면 [Explore the context window](https://code.claude.com/docs/en/context-window)를 참고한다.

### Feature별 context cost

각 feature는 loading strategy와 context cost가 다르다.

| Feature | 언제 load되나 | 무엇이 load되나 | Context cost |
| --- | --- | --- | --- |
| CLAUDE.md | Session start | Full content | Every request |
| Skills | Session start + 사용 시 | 시작 때 description, 사용 시 full content | Low, description은 every request |
| MCP servers | Session start | Tool names, full schemas는 on demand | Tool 사용 전까지 low |
| Code intelligence | File edit 후, 필요 시 | Edit 후 diagnostics, lookup 때 symbol location | Low, 다른 file read를 줄여준다. |
| Subagents | Spawn될 때 | 지정 skill을 가진 fresh context | Main session과 isolated |
| Hooks | Trigger 시 | 기본적으로 없음, 외부에서 실행 | Zero, hook이 additional context를 반환하지 않는 한 |

기본적으로 skill description은 session start에 load되어 Claude가 어떤 skill을 사용할지 판단할 수 있다. Skill frontmatter에 `disable-model-invocation: true`를 설정하면 사용자가 직접 invoke할 때까지 Claude에게 완전히 숨길 수 있다. 그러면 직접 trigger하는 skill의 context cost가 zero가 된다. 직접 작성하지 않은 skill이라면 settings의 [`skillOverrides`](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings)를 사용해 같은 효과를 낼 수 있다.

### Feature가 load되는 방식 이해하기

각 feature는 session의 다른 시점에 load된다. 아래 diagram은 CLAUDE.md, MCP, Skills, Subagents, Hooks가 context에 들어오는 타이밍을 보여준다.

![Context loading: CLAUDE.md loads at session start and stays in every request. MCP tool names load at start with full schemas deferred until use. Skills load descriptions at start, full content on invocation. Subagents get isolated context. Hooks run externally.](https://mintcdn.com/claude-code/ikqp3_70mqIahteV/images/context-loading.svg?fit=max&auto=format&n=ikqp3_70mqIahteV&q=85&s=aab139e750494a237ae2e0c8f9139b0a)

#### CLAUDE.md

**When:** Session start

**What loads:** Managed, user, project level의 모든 CLAUDE.md file full content.

**Inheritance:** Claude는 working directory에서 root까지의 CLAUDE.md files를 읽고, file에 access하면서 subdirectory의 nested file도 discover한다. 자세한 내용은 [How CLAUDE.md files load](https://code.claude.com/docs/en/memory#how-claude-md-files-load)를 참고한다.

> Tip: CLAUDE.md는 200 lines 아래로 유지한다. Reference material은 on-demand로 load되는 skills로 옮긴다.

#### Skills

Skills는 Claude의 toolkit에 추가되는 extra capabilities다. API style guide 같은 reference material일 수도 있고, `/deploy` 같은 user-invocable workflow일 수도 있다. Claude Code에는 바로 사용할 수 있는 `/code-review`, `/batch`, `/debug` 같은 [bundled skills](https://code.claude.com/docs/en/commands)가 포함되어 있다. 직접 만들 수도 있다. Claude는 적절할 때 skill을 사용하며, 사용자가 직접 invoke할 수도 있다.

**When:** Skill configuration에 따라 다르다. 기본적으로 description은 session start에 load되고 full content는 사용될 때 load된다. User-only skill(`disable-model-invocation: true`)은 사용자가 invoke하기 전까지 아무것도 load되지 않는다.

**What loads:** Model-invocable skill의 경우 Claude는 every request에서 name과 description을 본다. 사용자가 `/<name>`으로 skill을 invoke하거나 Claude가 자동 load하면 full content가 conversation에 들어간다.

**How Claude chooses skills:** Claude는 task와 skill description을 match해 관련 skill을 고른다. Description이 vague하거나 overlap되면 Claude가 잘못된 skill을 load하거나 필요한 skill을 놓칠 수 있다. 특정 skill을 쓰라고 하려면 `/<name>`으로 invoke한다. `disable-model-invocation: true`인 skill은 사용자가 invoke하기 전까지 Claude에게 보이지 않는다.

**Context cost:** 사용 전까지 low. User-only skill은 invoke 전까지 zero cost다.

**In subagents:** Subagent에서 skills는 다르게 작동한다. On-demand loading 대신 subagent의 `skills` field에 listed된 skills가 launch 때 full preload된다. Subagents는 Skill tool을 통해 listed되지 않은 project, user, plugin skills도 discover하고 invoke할 수 있다.

> Tip: Side effect가 있는 skill에는 `disable-model-invocation: true`를 사용한다. Context를 아끼고 사용자가 직접 trigger할 때만 실행되도록 보장한다.

#### MCP servers

**When:** Session start.

**What loads:** Connected server의 tool names. Full JSON schemas는 Claude가 특정 tool을 필요로 할 때까지 deferred된다.

**Context cost:** [Tool search](https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search)가 기본적으로 켜져 있으므로 idle MCP tools는 minimal context만 소비한다.

> Tip: `/mcp`를 실행해 server별 connection status와 token cost를 확인한다. Claude Code는 remote server가 끊기면 [자동으로 reconnect](https://code.claude.com/docs/en/mcp#automatic-reconnection)하며, 지금 쓰지 않는 server는 disconnect할 수 있다.

#### Code intelligence

**When:** File edit 후, 그리고 Claude가 code를 navigate할 때 on demand.

**What loads:** 각 file edit 후 type error와 warning. Claude가 symbol을 lookup할 때 definition, reference, type information.

**Context cost:** Low. Symbol lookup은 broad file read를 대체하는 경우가 많아 net context use를 줄일 수 있다.

> Tip: LSP tool은 해당 language용 [code intelligence plugin](https://code.claude.com/docs/en/discover-plugins#code-intelligence)을 설치하기 전까지 inactive다.

#### Subagents

**When:** 사용자나 Claude가 task를 위해 spawn할 때 on demand.

**What loads:** 다음을 포함하는 fresh, isolated context.

- Agent 자체 system prompt. Full Claude Code system prompt가 아니다.
- Agent의 `skills:` field에 listed된 skills의 full content.
- CLAUDE.md와 git status. 단, built-in Explore와 Plan agents는 [둘 다 omit](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)한다.
- Lead agent가 prompt로 전달하는 context.

**Context cost:** Main session과 isolated된다. Subagents는 conversation history나 invoked skills를 inherit하지 않는다.

> Tip: Full conversation context가 필요 없는 work에는 subagents를 쓴다. Isolation은 main session bloating을 막는다.

#### Hooks

**When:** Trigger 시. Hooks는 tool execution, session boundary, prompt submission, permission request, compaction 같은 lifecycle event에서 fire된다. 전체 목록은 [Hooks](https://code.claude.com/docs/en/hooks)를 참고한다.

**What loads:** 기본적으로 nothing. Hooks는 main conversation 밖에서 execute된다.

**Context cost:** Zero. 단, hook이 conversation에 추가될 output을 반환하면 그 output은 context cost를 가진다.

> Tip: Hooks는 Claude context에 영향을 줄 필요가 없는 side effect, 예를 들어 linting, logging에 이상적이다.

## Learn more

각 feature에는 setup instruction, example, configuration option을 담은 guide가 있다.

- [CLAUDE.md](https://code.claude.com/docs/en/memory): Project context, convention, instruction 저장
- [Skills](https://code.claude.com/docs/en/skills): Claude에 domain expertise와 reusable workflow 제공
- [Subagents](https://code.claude.com/docs/en/sub-agents): Isolated context로 work offload
- [Agent teams](https://code.claude.com/docs/en/agent-teams): 병렬로 작업하는 여러 session coordinate
- [MCP](https://code.claude.com/docs/en/mcp): Claude를 external service에 연결
- [Hooks](https://code.claude.com/docs/en/hooks-guide): Hooks로 action automate
- [Plugins](https://code.claude.com/docs/en/plugins): Feature set을 bundle하고 share
- [Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces): Plugin collection host 및 distribute
