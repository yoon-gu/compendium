---
title: "A2A Python SDK: 내 에이전트를 다른 에이전트가 부를 수 있는 서버로 공개하기"
date: 2026-09-14
draft: false
source_url: "https://discuss.pytorch.kr/t/a2a-2-a2a-python-sdk-a2a/11893"
author: "9bow (박정환), PyTorchKR"
tags: ["AI", "Agent", "A2A", "Python", "SDK", "Starlette", "JSON-RPC"]
summary: "A2A Python SDK를 쓰면 개발자가 채우는 건 AgentCard와 AgentExecutor 둘뿐이고, 카드 공개·태스크 상태 관리·스트리밍 이벤트·오류 응답은 SDK가 맡는다. helloworld 예제를 기준으로 구성 요소와 실제로 오가는 JSON을 정리했다."
---

> **출처:** [\[A2A 알아보기 2편\] A2A Python SDK](https://discuss.pytorch.kr/t/a2a-2-a2a-python-sdk-a2a/11893) — 9bow(박정환), PyTorchKR, 2026-09-14
>
> 한국어 원문이라 번역이 아니라 정리 노트다. 코드는 [a2aproject/a2a-python](https://github.com/a2aproject/a2a-python)과 [a2a-samples](https://github.com/a2aproject/a2a-samples)의 helloworld 예제 기준(a2a-sdk 1.1.0).
>
> 시리즈: [1편 프로토콜](/compendium/notes/a2a-protocol-1-0/) · **2편 Python SDK**

## 한 줄 요약

이미 돌아가는 에이전트를 남에게 열어 주려 하면 할 일이 전부 에이전트 로직 **바깥**에 몰려 있다. 능력 문서를 정해진 경로에 올리고, 요청을 태스크로 만들어 상태를 관리하고, 진행 상황을 스트리밍으로 흘리고, 선언하지 않은 기능을 호출받으면 규격대로 거절해야 한다. 직접 짜면 주변 코드가 에이전트보다 커진다. SDK는 그 주변부를 맡는다.

## 개발자가 채우는 두 칸

SDK를 쓸 때 직접 작성하는 것은 둘뿐이다.

- `AgentCard` — 이 에이전트가 무엇을 할 수 있는지
- `AgentExecutor` 구현 — 실제로 일을 하는 부분

나머지는 SDK의 요청 핸들러와 라우트 생성 함수가 처리한다. 라우트는 Starlette나 FastAPI 같은 ASGI(Asynchronous Server Gateway Interface) 앱에 그대로 붙일 수 있어서, 기존 인증·로깅 미들웨어 구성을 유지한 채 A2A 엔드포인트만 얹으면 된다.

지원 범위는 1.0 명세를 JSON-RPC / REST / gRPC 세 바인딩 모두에서 클라이언트·서버 양쪽으로 지원하고, 0.3에 대해서도 호환 모드를 제공한다. 선택 의존성으로 gRPC, OpenTelemetry 추적, 그리고 PostgreSQL·MySQL·SQLite를 쓰는 SQL 태스크 저장소가 있다.

## 함정 셋

실습을 따라가다 걸리기 쉬운 지점이 세 군데다.

**의존성 버전.** 공식 튜토리얼은 저장소 최상위 `samples/python/requirements.txt`를 설치하라고 하는데, 이 파일은 `a2a-sdk[http-server]>=0.3.0`처럼 하한만 건다. 예제를 그대로 재현하려면 `a2a-sdk==1.1.0`으로 고정하고 `sse-starlette`까지 포함한 helloworld 쪽 requirements를 쓰는 게 안전하다. Python 3.10 이상이 필요하다.

**문서와 코드의 불일치.** 튜토리얼 산문은 기능 이름을 `hello_world`("Returns hello world")라고 적지만 저장소 실제 코드는 `echo_bot`을 쓴다. 문서가 코드 변경을 못 따라온 경우라, 이름이 안 맞으면 `__main__.py`를 기준으로 삼으면 된다.

**메모리 저장소.** 예제가 쓰는 `InMemoryTaskStore`는 프로세스가 내려가면 태스크가 사라진다. 오래 사는 태스크를 다루려면 SQL 저장소로 바꿔야 한다.

## 에이전트 카드 정의

능력은 `AgentSkill`로 하나씩 기술하고, 이를 모아 `AgentCard`를 만든다. 카드에는 정체성, 기본 입출력 미디어 타입, 지원 기능, 접속 가능한 인터페이스 목록이 들어간다.

```python
public_agent_card = AgentCard(
    name='Hello World Agent',
    version='0.0.1',
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    capabilities=AgentCapabilities(streaming=True, extended_agent_card=True),
    supported_interfaces=[
        AgentInterface(
            protocol_binding='JSONRPC',
            url='http://127.0.0.1:9999',
            protocol_version='1.0',
        )
    ],
    skills=[skill],
)
```

파이썬 필드는 snake_case지만 공개되는 JSON은 camelCase다. 코드의 `default_input_modes`는 카드에서 `defaultInputModes`로 나온다.

예제는 인증한 상대에게만 보여 줄 확장 카드도 함께 정의한다. 공개 카드에는 기능 하나만, 확장 카드에는 하나를 더해 둘을 싣는다. 어떤 기능은 아무나 보게 하고 어떤 기능은 계약을 맺은 쪽에만 알리는 상황이 이 구조로 표현된다.

## 실행기 구현

`AgentExecutor`의 `execute` 메서드 하나가 요청 하나를 처리한다. 흐름은 다섯 단계다.

1. 요청 맥락에서 태스크를 꺼내고, 없으면 새로 만들어 이벤트 큐에 넣는다
2. `TaskUpdater`로 상태를 `TASK_STATE_WORKING`으로 바꾼다
3. 사용자 입력을 꺼내 에이전트를 호출한다
4. 생성한 응답을 **아티팩트로** 붙인다 (`add_artifact`)
5. 상태를 `TASK_STATE_COMPLETED`로 바꾼다

4번이 핵심이다. 1편에서 본 규칙 — 결과는 메시지가 아니라 아티팩트로 — 이 여기서 코드로 나타난다. 메시지는 태스크 기록에 보존된다는 보장이 없기 때문이다. `TaskUpdater`가 상태 갱신 이벤트와 아티팩트 갱신 이벤트를 각각 만들어 큐에 넣어 준다.

인터페이스에는 `cancel`도 있다. helloworld는 `NotImplementedError`를 던지지만, 실제 에이전트라면 진행 중인 작업을 어떻게 중단할지 여기에 구현해야 한다.

## 서버 구성

요청 핸들러가 실행기·태스크 저장소·두 종류의 카드를 묶고, 라우트 생성 함수가 엔드포인트를 만든다.

```python
request_handler = DefaultRequestHandler(
    agent_executor=HelloWorldAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=public_agent_card,
    extended_agent_card=extended_agent_card,
)

routes = []
routes.extend(create_agent_card_routes(public_agent_card))
routes.extend(create_jsonrpc_routes(request_handler, '/'))
app = Starlette(routes=routes)
```

`create_agent_card_routes`가 카드를 `/.well-known/agent-card.json`으로 공개하고, `create_jsonrpc_routes`가 JSON-RPC 호출을 핸들러로 넘긴다. REST로 서비스하려면 `create_rest_routes`를 쓰고, 둘을 같은 앱에 함께 붙일 수도 있다.

핸들러에 카드를 넘기는 이유는 선언된 기능을 검사하기 위해서다. `streaming=False`인 에이전트가 스트리밍 요청을 받으면 핸들러가 정해진 오류를 돌려준다. 1편의 "선언하지 않은 기능은 오류" 규칙이 SDK 층에서 자동으로 지켜지는 셈이다.

## 실제로 오가는 JSON

이 글에서 가장 볼 만한 부분은 1편의 명세 변경이 실물로 확인되는 대목이다.

응답의 파트가 `{"text": "..."}` 형태이고 `kind` 판별자가 없다. 0.3에서는 같은 자리에 `{"kind":"text","text":"..."}`가 왔다. 열거형이 `TASK_STATE_COMPLETED`, `ROLE_USER`처럼 대문자로 나오는 것도 ProtoJSON 직렬화 규칙 그대로다. 요청에는 `A2A-Version: 1.0` 헤더가 붙는다.

같은 메시지를 `SendStreamingMessage`로 보내면 Server-Sent Events **네 건**으로 쪼개져 도착한다.

1. 태스크 객체 (`TASK_STATE_SUBMITTED`)
2. `statusUpdate` — `TASK_STATE_WORKING`
3. `artifactUpdate` — 결과물
4. `statusUpdate` — `TASK_STATE_COMPLETED`, 여기서 스트림이 닫힌다

실행기 코드에서 `update_status`와 `add_artifact`를 부른 순서가 그대로 네 건의 이벤트가 됐다. 상태 갱신이 `statusUpdate`로, 아티팩트 갱신이 `artifactUpdate`로 감싸인 것 역시 1.0에서 바뀐 표현이다.

## 클라이언트 쪽

직접 JSON을 만들 필요는 없다. `A2ACardResolver`가 잘 알려진 경로에서 카드를 받아 오고, `create_client`가 그 카드를 보고 전송 방식을 골라 클라이언트를 만든다. 카드 조회 → 바인딩 선택이라는 1편의 흐름이 두 줄로 압축된다.

## 누구에게 맞나

이미 동작하는 파이썬 에이전트가 있고 그걸 조직 밖이나 다른 팀의 에이전트에게 열어 줘야 하는 경우다. 반대로 에이전트를 아직 만드는 중이라면 순서가 뒤바뀐 것이다.

주의할 점 하나. 저장소의 LangGraph 예제는 현재 1.1.0과 호환되지 않는다. 0.3에서 1.0으로 넘어오며 필드 이름과 상태 열거형이 바뀐 탓이라, 옛 예제를 참고할 때는 [마이그레이션 가이드](https://github.com/a2aproject/a2a-python/blob/main/docs/migrations/v1_0/README.md)를 같이 봐야 한다. 라이선스는 Apache License 2.0이다.

## 함께 읽기

- [A2A 프로토콜 1.0](/compendium/notes/a2a-protocol-1-0/) — 이 시리즈 1편, 여기 나온 태스크·아티팩트·바인딩 개념의 출처
- [Agent-Safe Pipeline](/compendium/notes/agent-safe-pipeline/) — 외부 에이전트의 요청을 받아 실행하기 전에 policy boundary를 두는 문제
- [Secure MCP Tunnels](/compendium/notes/secure-mcp-tunnels/) — 에이전트 엔드포인트를 외부에 노출할 때의 보안 고려
