---
title: "Microsoft Agent Governance Toolkit: AI agent를 위한 deterministic governance layer"
date: 2026-07-28
draft: false
source_url: "https://github.com/microsoft/agent-governance-toolkit"
author: "Microsoft"
tags: ["AI", "Agents", "Governance", "Security", "MCP", "Developer Tools"]
summary: "Agent Governance Toolkit은 autonomous AI agent의 tool call, delegation, message, resource access를 prompt-level guardrail이 아니라 deterministic application-layer policy로 통제하려는 toolkit이다. Policy engine, identity/trust, audit log, execution rings, SRE, MCP Security Gateway, multi-language SDK와 framework adapter를 포함한다."
---

> **원문:** [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) — Microsoft, GitHub repository
>
> 아래 글은 README와 주요 docs를 바탕으로, repository landing page를 그대로 덤프하지 않고 practitioner가 검토해야 할 구조·설치·policy model·지원 범위·한계를 한국어로 정리한 것이다. Repository snapshot은 2026-07-28 기준이며, star/fork/version 수치는 이후 바뀔 수 있다.

## 한 줄 요약

Agent Governance Toolkit, 줄여서 AGT는 autonomous AI agent가 tool을 호출하거나 다른 agent에 delegation하거나 외부 resource에 접근하기 전에, deterministic application code에서 policy를 평가하고 allow/deny/audit하는 governance layer다. 핵심 메시지는 “prompt에게 규칙을 지키라고 부탁하지 말고, forbidden action이 wire에 도달하기 전에 구조적으로 불가능하게 만들라”는 것이다.

GitHub metadata snapshot 기준으로 repository는 Python 중심이며 MIT License를 사용한다. GitHub API 확인 시점의 description은 “policy enforcement, zero-trust identity, execution sandboxing, reliability engineering for autonomous AI agents”이고, topic은 `ai-agents`, `governance`, `owasp`, `policy-engine`, `security`, `zero-trust` 등이다. 확인 시점의 repository stats는 약 5.1k stars, 833 forks였고, default branch는 `main`이다.

## AGT가 풀려는 문제

README는 production agent 운영에서 세 가지 질문을 제시한다.

1. 이 action은 허용되는가? `send_email`과 `query_database`에 접근 가능한 agent가 `drop_table`까지 할 수 있어서는 안 된다. OAuth scope나 IAM role은 어떤 service에 연결할 수 있는지만 통제하고, 연결 뒤에 무엇을 하는지는 충분히 통제하지 못한다.
2. 어떤 agent가 이 일을 했는가? Multi-agent system에서 여러 agent가 하나의 API key를 공유하면 incident response는 “어떤 agent가 했다” 수준에서 멈춘다.
3. 무슨 일이 있었는지 증명할 수 있는가? Auditor와 regulator는 어떤 policy가 active였고, agent가 무엇을 요청했으며, 왜 allow/deny되었는지를 tamper-evident record로 요구한다.

AGT의 문제의식은 prompt-level safety가 control surface가 아니라는 점이다. “규칙을 지켜라”는 instruction은 stochastic system에 대한 polite request일 뿐이다. AGT는 prompt injection 방어를 model 내부에서 이기려 하지 않고, tool call, message send, delegation을 model intent가 외부로 나가기 전에 deterministic application code로 intercept한다.

## Quick start와 policy shape

Python quick start는 다음 설치에서 시작한다.

```bash
pip install agent-governance-toolkit[full]
```

README에 따르면 base `agent-governance-toolkit` wheel은 compliance CLI 중심이고, quick-start import에 필요한 governance modules는 consolidated core distribution에 있다. 새 policy-engine host code에는 AGT 5의 `agt-policies`/ACS API를 선호하라는 caveat도 붙어 있다. 즉, README의 legacy compatibility 예제와 현재 권장 API가 섞여 있으므로 production 도입 전에 package별 README와 changelog를 같이 확인해야 한다.

Claude Code integration은 plugin marketplace로 설치하는 흐름을 제공한다.

```text
/plugin marketplace add microsoft/agent-governance-toolkit
/plugin install agt-governance@agent-governance-toolkit
```

가장 작은 사용 패턴은 tool function을 `govern()`으로 감싸는 방식이다.

```python
from agentmesh.governance import govern

safe_tool = govern(my_tool, policy="policy.yaml")
```

예시 `policy.yaml`은 `default_action`, `rules`, `condition`, `action`, `approvers`를 사용한다.

```yaml
apiVersion: governance.toolkit/v1
name: production-policy
default_action: allow
rules:
  - name: block-destructive
    condition: "action.type in ['drop', 'delete', 'truncate']"
    action: deny
    description: "Destructive operations require human approval"

  - name: require-approval-for-send
    condition: "action.type == 'send_email'"
    action: require_approval
    approvers: ["security-team"]
```

이 policy에서 `read` action은 통과하지만 `drop` action은 `GovernanceDenied`로 차단된다. AGT의 핵심은 “나중에 log에서 발견”이 아니라 “execution 전에 fail-closed로 판단”하는 데 있다.

CLI surface는 compliance와 policy hygiene 쪽에 초점이 있다.

```bash
agt doctor                                          # installation check
agt verify                                          # OWASP compliance check
agt verify --evidence ./agt-evidence.json --strict  # weak evidence면 CI fail
agt red-team scan ./prompts/ --min-grade B          # prompt injection audit
agt lint-policy policies/                           # policy file validation
```

## Architecture: policy, identity, runtime, SRE의 조합

Architecture docs는 AGT를 deterministic application-layer interception으로 설명한다. 모든 agent action은 execution 전에 policy에 대해 평가되고, high-security environment에서는 container/VM isolation과 조합해 defense-in-depth로 써야 한다.

README의 흐름은 다음과 같다.

```text
Agent ──► Policy Engine ──► Identity ──► Audit Log
            (YAML/OPA/Cedar)  (SPIFFE/DID/mTLS)  (Tamper-evident)
                 │                                      │
                 ├── Allowed ──► Tool executes           │
                 └── Denied  ──► GovernanceDenied        │
                                                        ▼
                                                 Decision Record
```

중요한 점은 모든 layer가 optional이라는 것이다. 낮은 risk profile에서는 `govern()`과 policy enforcement + audit logging만 시작해도 되고, 필요해질수록 identity, trust mesh, execution rings, SRE, MCP gateway를 추가한다.

주요 component는 다음과 같다.

| Component | 역할 |
| --- | --- |
| Agent OS Engine | Policy Engine, Capability Model, Governance Gate, Decision BOM |
| AgentMesh | Zero-trust identity, Ed25519/SPIFFE credential, trust scoring, delegation chain |
| Agent Runtime | Execution rings, resource limit, runtime sandboxing, termination control |
| Agent SRE | SLO, error budget, replay, chaos testing, circuit breaker |
| Agent Hypervisor | Execution audit, delta engine, in-memory commitment tracking, command denylist |
| Agent Marketplace | Plugin discovery, signing/verification, trust scoring |
| MCP Security Gateway | Tool poisoning, drift monitoring, typosquatting, hidden instruction scanning |
| Framework adapters | LangChain, CrewAI, AutoGen, OpenAI Agents SDK, ADK, smolagents 등과 연결 |

Architecture docs는 policy evaluation latency를 sub-millisecond로 제시하지만, 이 수치는 policy engine 자체 benchmark다. Distributed multi-agent deployment에서는 Ed25519 verification, trust score lookup, first-contact handshake, network round trip이 더해져 inter-agent interaction당 5-50ms 정도를 기대해야 한다고 limitation docs가 설명한다.

## Package와 language support

README와 Package Feature Matrix 기준으로 AGT는 Python을 primary implementation으로 두고, TypeScript, .NET, Rust, Go package도 제공한다. Core governance primitive는 5개 language에서 제공되는 것으로 문서화되어 있다.

| Language | Install | 메모 |
| --- | --- | --- |
| Python | `pip install agent-governance-toolkit[full]` | Full stack, unified `agt` CLI, dashboard, OWASP verification 중심 |
| TypeScript | `npm install @microsoft/agent-governance-sdk` | `PolicyEngine`, `AgentIdentity`, `TrustEngine`, `AuditLogger`, MCP scanner 등 |
| .NET | `dotnet add package Microsoft.AgentGovernance` | YAML/JSON policy, OPA/Rego/Cedar backend, ASP.NET/Agent Framework middleware |
| Rust | `cargo add agentmesh` 또는 `cargo add agentmesh-mcp` | Governance stack 또는 MCP-specific primitives |
| Go | `go get github.com/microsoft/agent-governance-toolkit/agent-governance-golang` | Core governance, MCP security, execution rings, kill switch, SLO 등 |

Python distribution은 v4.1.0 기준으로 여러 package가 consolidated되어 있다.

| Distribution | 포함 내용 |
| --- | --- |
| `agent-governance-toolkit-core` | Policy engine, capability model, audit, MCP gateway, zero-trust identity, trust scoring, A2A/MCP/IATP bridges |
| `agent-governance-toolkit-runtime` | Privilege rings, saga orchestration, termination control, execution plan validation, command denylist |
| `agent-governance-toolkit-sre` | SLOs, error budgets, chaos engineering, circuit breakers |
| `agent-governance-toolkit-cli` | `agt` CLI, OWASP verification, integrity checks, policy linting |
| `agent-governance-toolkit[full]` | 위 distribution을 모두 설치하는 meta-package |

2026-07-28에 registry를 확인했을 때 PyPI `agent-governance-toolkit` latest는 `4.1.0`, npm `@microsoft/agent-governance-sdk` latest는 `4.0.0`, NuGet `Microsoft.AgentGovernance` latest list에는 `5.0.0`이 포함되어 있었다. README와 docs에는 Public Preview 및 pre-GA breaking change 가능성이 명시되어 있으므로, version skew와 API drift를 전제로 lockfile과 upgrade test를 둬야 한다.

## Framework support와 examples

README의 framework support matrix는 다음 ecosystem을 언급한다.

- Microsoft Agent Framework: native middleware
- Semantic Kernel: .NET + Python native integration
- AutoGen, LangGraph/LangChain, CrewAI, Google ADK, Mastra: adapter 계열
- OpenAI Agents SDK, LlamaIndex: middleware 계열
- Haystack: pipeline
- Dify: plugin
- Azure AI Foundry: deployment guide
- Claude Code와 GitHub Copilot CLI: developer-surface governance package/installer

Examples에는 `openai-agents-governed`, `crewai-governed`, `smolagents-governed`, `maf-integration`, `mcp-trust-verified-server`, `cedarling-governed`, `governance-dashboard` 등이 있다. Repository의 `examples/` tree를 보면 Claude Code, Copilot CLI, cost governance, multi-agent governance, MCP receipt, marketplace governance, prompt defense, SRE, shadow AI discovery 같은 scenario-specific example이 많다.

## Specifications와 compliance surface

AGT는 component별 formal specification과 conformance test를 강조한다. README는 다음 spec들을 나열한다.

| Specification | Scope |
| --- | --- |
| Agent OS Policy Engine | Policy evaluation, rule merging, fail-closed semantics |
| Agent Control Specification | Stateless intervention-point policy runtime, verdicts, transform, fail-closed |
| AgentMesh Identity and Trust | Credentials, trust scoring, delegation chains |
| Agent Hypervisor Execution Control | Privilege rings, saga orchestration, kill switch |
| AgentMesh Trust and Coordination | Peer trust negotiation, mesh-wide policy |
| Agent SRE Governance | SLOs, error budgets, chaos, circuit breakers |
| MCP Security Gateway | Tool poisoning, drift detection, hidden instructions |
| Framework Adapter Contract | Adapter integration and interceptor chain |
| Audit and Compliance | Merkle audit, compliance mapping, Decision BOM |
| AgentMesh Wire Protocol | Message format, routing, serialization |

README는 992 conformance tests와 29 Architecture Decision Records를 언급한다. Compliance mapping은 OWASP Agentic AI Top 10, NIST AI RMF 1.0, EU AI Act, SOC 2, AARM Extended, ATF를 포함한다. 이 부분은 “toolkit이 compliance를 자동으로 보장한다”가 아니라, evidence와 control mapping을 만들 수 있는 substrate로 이해하는 편이 안전하다.

## Security model과 boundary

AGT는 OS kernel이나 hardware isolation이 아니라 application middleware layer다. Policy engine과 agent는 같은 process boundary를 공유할 수 있으므로, production에서는 agent별 container isolation을 권장한다. Architecture docs의 defense-in-depth 조합은 다음과 같다.

| AGT enforcement | 함께 써야 할 layer |
| --- | --- |
| Agent action을 execution 전에 intercept/evaluate | Docker, gVisor, Kata 같은 container isolation |
| Capability-based least-privilege policy | Cross-agent communication을 위한 network policy |
| Cryptographic agent identity | Certificate lifecycle을 위한 external PKI |
| Append-only audit log / Merkle chain | Azure Monitor, write-once storage 같은 external append-only sink |
| Non-compliant agent termination | Isolated process에 대한 OS-level kill |
| Governance gate fail-closed | Tool-call level interception을 위한 MCP Security Gateway |

Trust score는 0-1000 scale로 정의된다. New agent default는 500, 즉 Standard tier다. 900-1000은 Verified Partner, 700-899는 Trusted, 300-499는 Probationary, 0-299는 Untrusted로 분류된다. Score는 policy compliance history, successful task completion, trust boundary violation 등에 의해 변화한다.

## AGT가 아닌 것과 known limitations

Limitations 문서는 도입 판단에 중요하다. AGT는 “action governance”이지 “reasoning governance”가 아니다. Tool call, resource access, inter-agent message를 막을 수 있지만, agent가 무엇을 생각하거나 말하는지 자체를 완전히 govern하지는 않는다.

주요 boundary는 다음과 같다.

| AGT is | AGT is not |
| --- | --- |
| Runtime action governance | Model safety / content moderation |
| Deterministic policy enforcement | Probabilistic guardrails |
| Application-layer middleware | OS kernel / hardware isolation |
| Framework-agnostic library | Managed cloud service |
| Audit trail of attempts/actions | External-world outcome verification |
| Permission layer | Application logic security 전체 |
| Action governance | Knowledge/data provenance governance |
| Enforcement infrastructure | Turnkey compliance solution |

특히 중요한 gap은 네 가지다.

1. Action sequence gap: 개별 action은 허용되지만 sequence 전체가 malicious workflow가 될 수 있다. Docs는 future workflow-level policies와 intent declaration을 언급한다.
2. Outcome gap: audit log는 agent가 무엇을 시도했고 governance layer가 allow/deny했는지를 기록한다. 외부 world-state가 실제로 바뀌었는지, API result가 stale하지 않았는지는 application-level validation이 필요하다.
3. Knowledge governance gap: RAG document, embedding, retrieved context의 provenance/freshness/authorization을 AGT가 직접 govern하지 않는다.
4. Credential persistence gap: session 안에서 agent가 보유한 API key/OAuth token이 task boundary를 넘어 남아 있는지를 AGT가 직접 관리하지 않는다.

따라서 production architecture는 model safety layer, AGT governance layer, application validation layer, infrastructure isolation layer를 함께 쓰는 layered defense가 되어야 한다.

## Practitioner takeaway

AGT는 “agent에게 안전하게 행동하라고 말하는 것”과 “agent가 위험한 action을 실행할 수 없게 만드는 것”을 구분한다. Agent framework를 production에 넣는 팀이라면 다음 순서가 현실적이다.

1. 먼저 high-risk tool call을 식별한다. 예: email/send, database mutation, shell execution, payment, external post, cross-agent delegation.
2. `govern()` 또는 framework adapter로 execution-before policy gate를 건다.
3. `default_action`, deny rule, approval gate, blocked pattern을 최소 set으로 시작한다.
4. Audit log를 incident response와 compliance evidence에 연결한다.
5. Multi-agent가 되면 agent identity, trust score, delegation chain, MCP gateway를 추가한다.
6. Production에서는 container isolation, network policy, secret manager, content safety, application-level verifier를 반드시 함께 둔다.

이 repository는 README 하나짜리 utility라기보다 agent governance control plane의 reference implementation 모음에 가깝다. 그래서 “one `pip install`, any framework”라는 메시지를 받아들이되, 실제 도입은 package/version skew, Public Preview 상태, framework별 integration maturity, application boundary를 확인하는 architecture review로 시작하는 것이 좋다.

## 주요 링크

- Repository: https://github.com/microsoft/agent-governance-toolkit
- Documentation: https://microsoft.github.io/agent-governance-toolkit/
- PyPI: https://pypi.org/project/agent-governance-toolkit/
- npm registry metadata: https://registry.npmjs.org/%40microsoft%2Fagent-governance-sdk
- NuGet: https://www.nuget.org/packages/Microsoft.AgentGovernance
- Architecture docs: https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/ARCHITECTURE.md
- Package feature matrix: https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/PACKAGE-FEATURE-MATRIX.md
- Known limitations: https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/LIMITATIONS.md
- FAQ: https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/FAQ.md
