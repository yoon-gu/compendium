---
title: "Agent-Safe Pipeline: AI agent 실행을 policy boundary 뒤에 두는 reference architecture"
date: 2026-08-17
draft: false
source_url: "https://github.com/decionis/agent-safe-pipeline"
author: "Decionis, Inc."
tags: ["AI", "Agent", "AI Safety", "Authorization", "Governance", "TypeScript"]
summary: "Agent-Safe Pipeline은 AI agent가 action을 propose할 수는 있지만 스스로 authorize하거나 privileged API를 직접 실행하지 못하게 만드는 TypeScript reference architecture다. 핵심은 immutable intent capture, Decionis policy verdict, Presence 기반 human approval, single-use grant를 소비하는 SafeExecutor를 분리하는 것이다."
---

> **원문:** [Agent-Safe Pipeline](https://github.com/decionis/agent-safe-pipeline) — Decionis, Inc., GitHub repository
>
> 아래 글은 README와 architecture/threat/security 문서를 바탕으로, agent 실행 권한 경계를 설계하려는 practitioner 관점에서 구조화한 한국어 노트다. Repository metadata는 2026-08-17에 확인했다.

## 한 줄 요약

Agent-Safe Pipeline은 “agent가 action을 제안할 수는 있지만, 그 action을 authorize하거나 privileged handler를 직접 선택해서는 안 된다”는 원칙을 TypeScript reference implementation으로 정리한 프로젝트다. Agent output을 trust하지 않고, exact intent를 canonical hash로 묶은 뒤 독립 policy service인 Decionis가 `ALLOW` / `ESCALATE` / `BLOCK` verdict를 내리며, 실제 실행은 trusted `SafeExecutor`가 single-use grant를 소비한 다음 sealed `ActionRegistry`의 handler를 호출한다.

```text
Agent -> immutable intent -> Decionis -> ALLOW / ESCALATE / BLOCK -> SafeExecutor -> API
                                      |
                                      +-> Presence -> verified human approval -> Decionis re-evaluation
```

중요한 점은 이 repo가 hosted authorization service가 아니라는 것이다. README는 이를 library와 runnable reference implementation으로 설명한다. Provider-side identity, least privilege, network isolation, incident response를 대체하지 않으며, safety claim은 documented trust boundary가 유지될 때만 성립한다.

## 문제 설정: agent가 자기 실행을 허가하면 안 된다

LLM agent application에서 위험한 패턴은 model runtime 안에 model key, policy/authorization key, provider admin token이 함께 들어가는 구조다. 이 경우 prompt injection이나 tool argument 변조가 곧 provider-side action으로 이어질 수 있다.

Agent-Safe Pipeline은 agent runtime을 trusted computing base 밖에 둔다. Agent가 control할 수 있는 것은 `action`, `target`, JSON `parameters`뿐이다. Tenant, actor identity, downstream system, operation, endpoint, idempotency key, credential, registered handler, parameter schema는 trusted runtime에서 resolve해야 한다. Model output에서 identity, role, endpoint, authorization header, approval evidence를 복사하지 않는 것이 기본 invariant다.

## 핵심 component

### `IntentCapture`

`IntentCapture`는 agent proposal과 trusted context를 분리해 검증하고, UUID/timestamp를 부여하며, 최대 5분 lifetime 안에서 canonical intent를 만든다. Authority binding은 `agent-safe.intent/1` format을 사용하고, JSON key를 lexicographic order로 정렬한 뒤 SHA-256 hash를 계산한다.

Execution intent에는 protocol version, tenant, intent ID, idempotency key, capture/expiry timestamp, actor, action/resource/parameters, context, downstream target이 포함된다. Validation은 기본적으로 100 KiB, nesting depth 20, 5,000 entries, array 1,000 values로 bounded되어 있고, cycle, non-JSON prototype, `__proto__`, `prototype`, `constructor` key, non-finite number를 거부한다.

### `DecionisGate`

`DecionisGate`는 exact binding을 authenticated Decionis authority API로 보내 verdict를 받는다. HTTPS가 기본이고, loopback development endpoint는 명시적으로 enable해야 한다. Timeout, response-size limit, malformed response, missing grant, binding mismatch처럼 애매한 상태는 fail-closed `BLOCK`으로 처리된다.

Policy outcome은 세 가지다.

- `ALLOW`: `should_execute`가 true이고, non-expired intent-bound grant가 있을 때만 실행 가능하다.
- `ESCALATE`: 실행을 멈추고 Presence human approval flow를 시작한다.
- `BLOCK`: authority/Presence error, transport failure, malformed response, replay, missing authorization까지 모두 실행 중단으로 귀결된다.

### `PresenceApprovalCoordinator`

Presence는 human approval evidence provider이지 execution authority가 아니다. Coordinator는 action, target, intent hash를 human에게 제시하고 terminal receipt dossier만 evidence로 받아들인다. 이후 Decionis가 그 receipt를 독립적으로 fetch/verify하고 exact same intent에 대해 다시 policy evaluation을 수행한다.

따라서 client-side boolean, screenshot, copied proof string, “user approved”라는 model claim은 충분하지 않다. Intent가 approval 중 바뀌거나 만료되면 새 intent를 capture하고 flow를 다시 시작해야 한다.

### `SafeExecutor`와 sealed `ActionRegistry`

`SafeExecutor`는 `ALLOW`, exact intent binding, grant 존재 여부를 확인하고, verifier가 grant를 atomically consume한 뒤에야 handler를 실행한다. Agent가 arbitrary callback을 넘기는 구조가 아니라, trusted application startup code가 action handler를 등록하고 registry를 seal한 뒤 사용한다.

이 구조의 핵심은 “agent가 어느 code를 실행할지 고르지 못한다”는 점이다. Agent는 proposal만 만들고, 실제 handler selection과 downstream credential은 trusted executor 뒤에 남는다.

### `ShadowPipeline`

`ShadowPipeline`은 기존 execution을 observe하면서 hypothetical authority decision을 얻기 위한 모드다. 결과는 `SHADOW`로 label되어야 하며, execution grant가 되지 않는다. Migration이나 policy dry-run에는 유용하지만, enforcement claim으로 오해하면 안 된다.

## 설치와 five-minute demo

요구사항은 Node.js 22.14 이상과 pnpm 9다.

```bash
git clone https://github.com/decionis/agent-safe-pipeline.git
cd agent-safe-pipeline
pnpm install --frozen-lockfile
pnpm --filter @decionis/agent-safe-example-basic demo
```

Package는 `@decionis/agent-safe-pipeline`로 공개되어 있다. README 기준 stable install은 다음과 같다.

```bash
npm install @decionis/agent-safe-pipeline
```

Prererelease는 explicit version을 지정해야 한다. Repository snapshot의 workspace/package version은 `0.1.3-rc.2`였고, root package는 private workspace이며 실제 library package는 `packages/pipeline` 아래에 있다.

간단한 usage shape는 다음과 같다.

```ts
const captured = intentCapture.capture(agentProposal, trustedContext);
const decision = await gate.evaluate(captured);
const result = await executor.run(captured, decision);
```

Export surface는 `PresenceApprovalCoordinator`, `DecisionAuthority`, `DecionisGate`, `FixtureDecisionAuthority`, `ActionRegistry`, `AuthorizationVerifier`, `ReplayStore`, `SafeExecutor`, `CanonicalIntentHasher`, `ExecutionIntent`, `IntentCapture`, `JsonValue`, `ShadowPipeline`로 구성된다.

## Repository map과 예제

Repository는 reference architecture와 evidence를 함께 제공한다.

- `packages/pipeline`: core TypeScript package. `IntentCapture`, `DecionisGate`, Presence coordination, `SafeExecutor`가 들어 있다.
- `examples/basic-agent`: 가장 작은 `BLOCK` flow demo.
- `examples/shopify-refund-agent`: refund amount에 따른 `ALLOW` / `ESCALATE` / `BLOCK` 예제.
- `examples/github-deploy-agent`: environment와 force-push control 예제.
- `examples/procurement-agent`: 예산 내 software request라도 기존 tool capacity가 남아 있으면 hold하는 예제.
- `examples/mcp-tool-gate`: governed tool을 가진 stdio MCP server 예제.
- `conformance/agent-safe-intent-v1.json`: portable canonical-hash test vector.
- `conformance/vectors/`: Unicode, NFC/NFD, negative zero, fractional/exponent number, nested array, UTF-16 key sort order 같은 canonicalization edge case vector.
- `docs/`: trust boundary, execution intent, ALLOW/ESCALATE/BLOCK, human approval, decision dossier 문서.
- `SECURITY-EVIDENCE.md`: control-to-artifact evidence map과 known gaps.

## Production invariant

README와 architecture 문서에서 반복되는 production invariant는 다음과 같다.

1. Agent input은 proposed `action`, `target`, `parameters`로 제한한다.
2. Tenant, actor, downstream target, credential은 trusted runtime config에서 온다.
3. Exact canonical intent를 hash하고 짧게 expire시킨다.
4. Decionis가 독립적으로 decide한다. Network error, malformed response, missing grant, binding mismatch는 fail closed다.
5. Presence는 exact intent를 human에게 보여주고 receipt evidence를 만들지만, execution authorization을 직접 부여하지 않는다.
6. Grant는 intent, decision, audience, expiry에 bind되고, handler 실행 전에 atomically consume된다.
7. Downstream credential은 trusted executor 뒤에만 존재한다.
8. Agent runtime은 downstream API로 직접 egress할 수 없어야 한다.

이 invariant는 agent framework에 그대로 이식할 수 있는 checklist다. 특히 “approval screen을 띄웠다”보다 “approval evidence가 exact canonical intent hash에 bind되어 있고, policy authority가 재평가했는가”가 더 중요한 구분이다.

## Threat model에서 볼 점

Threat model은 agent, prompt, retrieved content, tool arguments, model output을 모두 untrusted로 본다. Controls는 prompt injection 자체를 없애는 것이 아니라, prompt injection이 privileged execution으로 이어지는 path를 끊는 데 초점을 둔다.

| Threat | Control | 남는 risk |
| --- | --- | --- |
| Prompt injection이 policy bypass를 지시 | Gate가 prompt 밖에서 독립 decide | Developer가 architecture를 우회할 수 있음 |
| Approval 이후 tool argument 변경 | Exact canonical parameter/target을 intent hash에 bind | Downstream interpretation은 deterministic해야 함 |
| Action A approval을 action B에 재사용 | Presence display와 receipt가 exact hash에 bind되고 Decionis가 재검증 | Presence integration이 immutable field를 보존해야 함 |
| Old grant replay | Short expiry, idempotency key, `jti`, atomic single-use consume | Downstream timeout 뒤 recovery에는 provider idempotency가 필요 |
| Agent가 provider를 직접 호출 | Credential/egress를 executor 뒤에 둠 | Network policy가 실제로 agent egress를 막아야 함 |
| Agent가 arbitrary code 선택 | Sealed `ActionRegistry`; no agent-supplied callback | Trusted registration code는 여전히 security-critical |
| Authority unavailable/malformed | Timeout, bounded response, strict validation, fail closed | Availability 손실을 감수 |

Reference library가 인정하는 accepted risk도 명시되어 있다. Trusted executor host compromise는 in-process package만으로 막을 수 없고, authority failure는 availability를 떨어뜨리며, human은 정확히 bound된 action이라도 잘못 승인할 수 있다. Cross-language canonicalization drift와 in-memory replay protection의 process-local 한계도 별도로 적어 둔다.

## Security evidence와 release posture

`SECURITY-EVIDENCE.md`는 독립 certification claim이 아니라 evidence index라고 못박는다. 그래도 실무적으로 흥미로운 guardrail이 많다.

- Gitleaks로 full history secret scanning.
- Apache-2.0 text/package metadata canonical check.
- Production dependency audit과 toolchain audit 분리.
- Dependency license inventory와 policy check.
- GitHub Actions `uses:` reference를 40-character commit SHA로 pin.
- SafeExecutor/trust-boundary tests와 mutation test.
- Canonical intent property fuzzing.
- Fixture provenance check.
- Release tarball, SBOM, checksum, Sigstore bundle, raw in-toto statement, trusted root를 GitHub Release에 첨부하는 release evidence.

Known gap도 숨기지 않는다. npm OIDC prerelease와 registry/GitHub digest comparison은 issue #19에 남아 있고, OpenSSF Best Practices Silver 관련 후속 issue들이 있다. 즉 이 repo는 “완성된 제품”이라기보다, public reference implementation과 supply-chain/security evidence discipline을 같이 보여주는 예제에 가깝다.

## Development workflow

개발 검증은 `pnpm verify`에 많이 모여 있다.

```bash
pnpm install --frozen-lockfile
pnpm verify
```

`pnpm verify`는 formatting, Markdown lint, fixture convention, license check, production/toolchain audit, discovery check, deterministic performance test, typecheck, automation test, package tests, build를 수행한다. README는 lines/functions/statements 90%, branches 85% coverage threshold도 언급한다. `pnpm mutation`은 trust-boundary tests가 deliberate mutation을 죽이는지 확인하고, `pnpm fuzz`는 canonical intent handling을 deterministic property test로 검증한다.

## Agent application에 적용할 때의 판단 기준

이 repo의 value는 특정 vendor API wrapper가 아니라 boundary pattern에 있다. 적용 여부를 볼 때는 다음 질문이 유용하다.

1. Agent runtime이 downstream credential을 직접 갖고 있는가?
2. Action handler 선택이 agent output에 의해 바뀔 수 있는가?
3. Human approval이 exact parameter/target hash에 bind되는가, 아니면 UI text만 승인하는가?
4. Policy authority outage나 malformed response가 fail-open으로 처리되는가?
5. Replay 방지가 process memory에만 의존하는가, production authority의 atomic consume endpoint가 있는가?
6. Shadow/dry-run decision이 실제 authorization으로 오인될 수 있는 UI/log path가 있는가?
7. Cross-language client가 있다면 canonical JSON/hash vector를 공유하고 있는가?

Agent harness, MCP gateway, browser automation, code deployment bot, SaaS admin automation처럼 “LLM이 action을 제안하고 실제 side effect는 큰” 시스템에서는 이 질문이 바로 design review checklist가 된다.

## 주요 링크

- Repository: <https://github.com/decionis/agent-safe-pipeline>
- Architecture: <https://github.com/decionis/agent-safe-pipeline/blob/master/ARCHITECTURE.md>
- Threat model: <https://github.com/decionis/agent-safe-pipeline/blob/master/THREAT-MODEL.md>
- Trust boundary: <https://github.com/decionis/agent-safe-pipeline/blob/master/docs/trust-boundary.md>
- Execution intent: <https://github.com/decionis/agent-safe-pipeline/blob/master/docs/execution-intent.md>
- ALLOW / ESCALATE / BLOCK: <https://github.com/decionis/agent-safe-pipeline/blob/master/docs/allow-escalate-block.md>
- Human approval: <https://github.com/decionis/agent-safe-pipeline/blob/master/docs/human-approval.md>
- Security evidence: <https://github.com/decionis/agent-safe-pipeline/blob/master/SECURITY-EVIDENCE.md>
- npm registry metadata: <https://registry.npmjs.org/%40decionis%2Fagent-safe-pipeline>

## Snapshot

- Repository: `decionis/agent-safe-pipeline`
- Language: TypeScript
- License: Apache-2.0
- Default branch: `master`
- Stars/forks at 확인 시점: 484 / 59
- Repository topics: `agentic-ai`, `ai-agent-permissions`, `ai-governance`, `authorization`, `human-in-the-loop`, `mcp`, `policy-as-code`, `reference-architecture`, `typescript`
