---
title: "Secure MCP Tunnel: 비공개 MCP 서버를 공개하지 않고 OpenAI 제품에 연결하기"
date: 2026-07-02
draft: false
source_url: "https://developers.openai.com/api/docs/guides/secure-mcp-tunnels"
author: "OpenAI Developers"
tags: ["OpenAI", "MCP", "Security", "Networking", "ChatGPT", "Codex"]
summary: "Secure MCP Tunnel은 사설망·온프레미스·방화벽 뒤에 있는 MCP 서버를 public ingress 없이 ChatGPT, Codex, Responses API 등 지원되는 OpenAI 표면에서 사용할 수 있게 해 주는 outbound-only 터널이다. 이 문서는 tunnel-client의 동작 방식, 권한·네트워크 요구사항, 배포 패턴, 보안 경계와 troubleshooting을 설명한다."
---

> **원문:** [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) — OpenAI Developers
>
> 아래 글은 원문 문서의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 상대 경로였던 OpenAI 문서·이미지 링크는 공개 URL에서 바로 열리도록 절대 경로로 정리했다.

# Secure MCP Tunnel

비공개 MCP 서버를 public internet에 노출하지 않고, 지원되는 OpenAI 제품에 연결한다.

Secure MCP Tunnel은 inbound firewall port를 열거나 서버를 public internet에 노출하지 않고도, private MCP server를 지원되는 OpenAI 제품에 연결할 수 있게 해 준다. 이미 MCP 서버에 접근할 수 있는 네트워크 안에서 `tunnel-client`를 실행하면, 이 클라이언트가 OpenAI로 outbound HTTPS 경로를 열고, queue에 쌓인 MCP 작업을 가져오고, 요청을 local로 전달한 다음, 같은 터널을 통해 응답을 돌려준다.

## MCP tunnel이란 무엇인가?

MCP tunnel은 네트워크 내부의 host에서 OpenAI-hosted MCP endpoint로 나가는 outbound-only connection이다. MCP 서버가 private network, on-premises, firewall 뒤에 있지만 ChatGPT, Codex, Responses API 또는 다른 지원 OpenAI surface가 그 서버를 호출해야 할 때 사용한다.

Secure MCP Tunnel은 MCP 서버를 private 상태로 유지하면서, 지원되는 OpenAI 제품에는 일반적인 MCP request path를 제공한다. `tunnel-client`는 OpenAI에 작업이 있는지 polling하고, MCP 요청을 local로 forward한 뒤, 응답을 같은 tunnel을 통해 돌려준다.

## Secure MCP Tunnel을 사용할 때

다음 상황에서 Secure MCP Tunnel을 사용한다.

- MCP 서버가 private network, on-premises, developer machine, 또는 기존 access control 뒤에서 실행된다.
- ChatGPT, Codex, Responses API, 또는 다른 지원 OpenAI surface가 그 서버를 사용해야 하지만 MCP 서버를 public으로 만들고 싶지 않다.
- `tunnel-client`가 실행되는 host가 기본적으로 `api.openai.com:443`으로 outbound HTTPS request를 보낼 수 있거나, control-plane mTLS가 구성되어 있을 때 `mtls.api.openai.com:443`에 접근할 수 있으며, 동시에 private MCP 서버에도 접근할 수 있다.
- 일반 MCP 개념은 [MCP and Connectors guide](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)에서 먼저 확인한다.

## 동작 방식

1. Platform tunnel settings에서 OpenAI-hosted MCP tunnel endpoint를 만들거나 관리한다.
2. private MCP 서버에 접근할 수 있는 네트워크 안에서 `tunnel-client`를 실행한다.
3. tunnel identity와 private MCP server address로 `tunnel-client`를 구성한다.
4. OpenAI 제품은 MCP 요청을 OpenAI-hosted tunnel endpoint로 보낸다.
5. `tunnel-client`는 queue에 쌓인 작업을 long-polling하고, 각 `JSON-RPC` request를 private MCP 서버로 forward하며, 응답을 다시 tunnel을 통해 post한다.

private MCP 서버는 public listener가 필요 없다. OpenAI-hosted endpoint는 지원 제품에 일반적인 MCP request path를 제공하고, network initiation point는 사용자의 boundary 안에 남는다. connector가 streamed result를 요청하면, tunnel path는 중간 server-sent events도 forward할 수 있다.

![OpenAI products call the OpenAI-hosted tunnel endpoint; tunnel-client long-polls for queued work and returns the MCP response through the same tunnel.](https://developers.openai.com/images/platform/guides/secure-mcp-tunnels/request-flow-diagram.png)

## 시작하기 전에

필요한 것은 다음과 같다.

- [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels)에서 받은 `tunnel_id`.
- `tunnel-client`용 runtime API key.
- 네트워크 내부에서 `tunnel-client`가 stdio 또는 HTTP로 접근할 수 있는 MCP 서버.

## 권한과 접근

[Platform tunnel permissions](https://developers.openai.com/api/docs/guides/rbac)와 ChatGPT developer-mode access는 별개다.

- tunnel 생성 또는 수정에는 Tunnels **Read** + **Manage**가 필요하다.
- `tunnel-client` 실행 또는 connector settings에서 tunnel 선택에는 Tunnels **Read** + **Use**가 필요하다.
- Tunnel permissions는 Platform organization에 적용된다. Platform organization owner 또는 RBAC administrator가 tunnel role을 부여한다.
- ChatGPT developer mode는 별도의 workspace permission이다. Enterprise/Edu에서는 workspace admin이 **Permissions & Roles** > **Connected Data** > **Developer mode / Create custom MCP connectors**를 부여하고, 사용자는 **Settings** > **Apps** > **Advanced Settings**에서 이를 활성화한다. plan별 정책은 [developer-mode Help Center article](https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta)을 참고한다.

대상 ChatGPT workspace admin에게 developer-mode access를 요청하고, 대상 Platform organization owner/RBAC admin에게 tunnel permissions를 요청한다.

## Tunnel을 올바른 organization과 workspace에 연결하기

하나의 tunnel은 하나 이상의 Platform organization 또는 ChatGPT workspace와 연결될 수 있다. 이 association을 사용해 tunnel을 찾거나 사용할 수 있어야 하는 모든 OpenAI context를 정의한다.

- tunnel을 소유하거나 관리하는 Platform organization을 포함한다.
- connector settings에서 tunnel이 표시되어야 하는 ChatGPT workspace를 포함한다.
- Codex, Responses API 또는 다른 지원 제품이 해당 organization에서 private MCP 서버를 호출해야 한다면, 다른 Platform organization도 포함한다.
- `tunnel-client`에는 같은 `tunnel_id`를 사용한다. organization이나 workspace를 추가해도 두 번째 tunnel이 만들어지거나 private MCP server endpoint가 바뀌지는 않는다.

personal account의 경우 해당 account에 속한 personal Platform organization을 사용한다. ChatGPT와 Codex testing에서는 target ChatGPT workspace와 Codex가 사용할 Platform organization을 tunnel에 연결한다. personal Platform organization에만 연결된 tunnel은 Enterprise/Edu workspace에 자동으로 나타나지 않는다.

Platform organization과 ChatGPT workspace가 이미 linked 상태라면, [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels)에서 누락된 organization 또는 workspace를 추가할 수 있다. Platform organization에 대응되는 ChatGPT workspace가 없는 경우처럼 enterprise setup을 자동으로 검증할 수 없다면, 해당 tunnel을 사용해야 하는 enterprise account mapping에 대해 reviewed manual association override를 OpenAI account team에 요청한다.

## Network requirements

`tunnel-client`에는 inbound internet access가 필요 없다. 필요한 것은 OpenAI로 나가는 outbound HTTPS와 private MCP 서버에 대한 local reachability다.

| From | To | Used for |
| --- | --- | --- |
| `tunnel-client`를 실행하는 host | `/v1/tunnel/*` 경로의 `api.openai.com:443` over HTTPS | 기본 polling과 response posting. |
| `tunnel-client`를 실행하는 host | `/v1/tunnel/*` 경로의 `mtls.api.openai.com:443` over HTTPS | control-plane mTLS가 구성된 경우 polling과 response posting. |
| `tunnel-client`를 실행하는 host | 구성된 stdio command 또는 MCP server URL | 네트워크 내부에서 MCP request를 forwarding. |

## `tunnel-client` 설정

[Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels)를 열고, 거기 있는 download link를 사용하거나 [openai/tunnel-client](https://github.com/openai/tunnel-client/releases/latest)의 최신 public `tunnel-client` release를 사용한다. runbook에는 특정 release URL을 hard-code하지 말고 latest-release URL을 가리키게 한다.

이미 binary가 있다면 `tunnel-client help quickstart`로 시작한다. 이름 있는 local stdio profile에는 다음처럼 사용한다.

```bash
export CONTROL_PLANE_API_KEY="sk-..."

tunnel-client init \
  --sample sample_mcp_stdio_local \
  --profile local-stdio \
  --tunnel-id tunnel_0123456789abcdef0123456789abcdef \
  --mcp-command "python /path/to/server.py"

tunnel-client doctor --profile local-stdio --explain
tunnel-client run --profile local-stdio
```

HTTP MCP server의 경우 `--mcp-command` 대신 `--mcp-server-url https://mcp.internal.example.com/mcp`를 사용한다.

connector를 만들거나 테스트하는 동안 `tunnel-client run ...`이 healthy 상태로 유지되게 한다. connector discovery와 MCP tool call은 실행 중인 client에 의존한다.

![The local admin UI at /ui shows whether the running client is healthy, ready, and connected before you test from ChatGPT, Codex, or an API flow.](https://developers.openai.com/images/platform/guides/secure-mcp-tunnels/tunnel-client-admin-ui.png)

## `tunnel-client`를 어디에서 실행할지 선택하기

`tunnel-client`는 private MCP 서버에 이미 접근할 수 있는 동일 trust boundary 안에서 실행한다. 일반적인 deployment pattern은 다음과 같다.

- Kubernetes sidecar: MCP 서버 옆의 같은 Pod에서 `tunnel-client`를 실행하고 `localhost`로 연결한다.
- Dedicated Kubernetes deployment: MCP 서버가 private Service를 통해 이미 reachable한 경우 `tunnel-client`를 별도로 실행한다.
- VM 또는 systemd service: private networking을 통해 MCP 서버에 접근할 수 있는 host에서 `tunnel-client`를 실행한다.

## ChatGPT에서 연결하기

[ChatGPT connector settings](https://chatgpt.com/#settings/Connectors)를 열고 custom connector를 만든 뒤, **Connection**에서 **Tunnel**을 선택한다. ChatGPT가 사용 가능한 tunnel을 표시하면 선택하거나, 이미 유효한 `tunnel_id`가 있다면 직접 붙여 넣는다.

ChatGPT에 tunnel이 나타나지 않으면, tunnel이 Platform organization에만 연결된 것이 아니라 target ChatGPT workspace에도 연결되어 있는지 확인하고, connector operator에게 Tunnels **Read** + **Use** 권한이 있는지 확인한다.

## Security and networking

![The private MCP server stays inside the customer-controlled environment. tunnel-client reaches OpenAI over outbound HTTPS using the runtime API key and, when required, optional control-plane mTLS.](https://developers.openai.com/images/platform/guides/secure-mcp-tunnels/trust-boundaries-diagram.png)

- MCP server address는 private 상태로 유지되며, `tunnel-client`가 실행되는 환경 내부에서만 사용된다.
- `tunnel-client`는 OpenAI tunnel control plane에 authenticate한다. 지원되는 OpenAI 제품은 OpenAI-hosted tunnel endpoint를 사용한다.
- Tunnel access는 별도의 public ingress path를 도입하지 않고 기존 organization 및 workspace context를 따른다.
- `tunnel-client`는 outbound proxy, custom CA bundle, control-plane client certificate, MCP-side `mTLS` 같은 enterprise networking requirement를 지원한다.

### Logging boundaries

Secure MCP Tunnel은 tunnel transport와 app-level product logging을 분리한다.

- Tunnel control-plane auth, long-poll / response traffic, 개별 tunnel transport request는 tunnel path를 통해 ChatGPT Compliance Platform app event로 emit되지 않는다.
- Tunnel metadata 변경은 API Platform [Audit logs](https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/audit_logs) surface를 통해 `tunnel.created`, `tunnel.updated`, `tunnel.deleted`로 노출된다.
- ChatGPT가 Secure MCP Tunnel을 통해 custom app에 접근할 때, tunnel은 transport path일 뿐이다. app invocation log와, app이 link/unlink될 때의 `APP_AUTH_LOG` 같은 app auth lifecycle log를 포함해 일반 app-level compliance logging은 app path에서 계속 적용된다.

## Advanced: allowlisted HTTP callouts

Secure MCP Tunnel은 지원되는 agent 또는 API flow에서 customer network 안으로 narrowly scoped HTTP callout을 보내는 용도로도 사용할 수 있다. `tunnel-client`에는 Harpoon이라는 embedded MCP server가 포함되어 있으며, 이 서버는 구성된 HTTP target을 label로 노출하고, caller가 bounded request/response limit 안에서 tunnel을 통해 이를 호출할 수 있게 한다.

소수의 private REST endpoint에 접근해야 하지만 public으로 노출하고 싶지 않을 때 사용한다. Harpoon은 general-purpose proxy가 아니다. caller는 arbitrary host를 선택할 수 없고, request는 customer가 구성한 target과 method로 제한된다.

## Troubleshooting

- Tunnel not visible in ChatGPT: tunnel이 Platform organization에만 포함된 것이 아니라 target ChatGPT workspace도 포함하는지 확인한다. 그다음 connector operator의 Tunnels **Use** permission을 확인한다. enterprise account에서 workspace를 자동으로 link할 수 없다면, OpenAI account team에 reviewed manual association override를 요청한다.
- Connector discovery 또는 tool call 실패: `tunnel-client run ...`이 계속 실행 중인지 확인한 뒤, `tunnel-client doctor --profile <name> --explain`을 다시 실행한다.
- Tunnel을 inspect할 수는 있지만 edit할 수 없음: operator에게 Tunnels **Read**는 있지만 Tunnels **Manage**가 없을 가능성이 높다.
- `tunnel-client`는 `/healthz`, `/readyz`, `/metrics`, local admin UI `/ui`를 노출한다.
- admin UI는 기본적으로 loopback-only다. 원격으로 노출하는 것은 operator network가 의도적으로 접근해야 할 때만 한다.
- ChatGPT, Codex 또는 API flow에서 테스트하기 전에 위 surface들을 사용해 client가 healthy, ready, polling 상태인지 확인한다.
- client가 connected 상태가 아니면, `tunnel-client`가 다시 연결될 때까지 tunnel을 통한 request는 실패한다.
- raw HTTP logging은 기본적으로 비활성화되어 있고, support export는 redacted된다.

## OAuth

- OAuth discovery는 tunnel path를 통해 이동할 수 있으므로 MCP server 자체는 private 상태로 남을 수 있다.
- tunnel은 browser-facing OAuth flow에 필요한 upstream authorization server metadata를 보존한다.
- authorization server 자체가 자동으로 tunnel 처리되는 것은 아니다. authorization server가 public internet과 `tunnel-client` host 양쪽에서 모두 reachable하지 않으면, MCP server가 reachable하더라도 OAuth flow가 실패할 수 있다.

## 어디에서 구성하나

- OpenAI-hosted MCP tunnel endpoint는 [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels)에서 관리한다.
- ChatGPT connector를 만들 때는 [ChatGPT connector settings](https://chatgpt.com/#settings/Connectors)에서 tunnel을 사용한다.
- Codex 또는 API flow의 경우, 지원되는 product surface가 노출하는 tunnel-backed MCP target을 사용한다.

## 다음 단계

- [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels)에서 tunnel을 만들거나 관리한다.
- `tunnel-client doctor --profile <profile> --explain`으로 `tunnel-client` profile을 검증한다.
- [ChatGPT connector settings](https://chatgpt.com/#settings/Connectors) 또는 사용 중인 지원 OpenAI surface에서 tunnel을 연결한다.

![Create and manage OpenAI-hosted MCP tunnel endpoints from Platform tunnel settings.](https://developers.openai.com/images/platform/guides/secure-mcp-tunnels/platform-tunnels-settings.png)

![Select Tunnel when connecting a ChatGPT connector to a private MCP server.](https://developers.openai.com/images/platform/guides/secure-mcp-tunnels/chatgpt-connectors-tunnel.png)
