---
title: "A2A 프로토콜 1.0: 프레임워크가 달라도 에이전트끼리 일을 넘기게 하는 규격"
date: 2026-09-14
draft: false
source_url: "https://discuss.pytorch.kr/t/a2a-1-0/11892"
author: "9bow (박정환), PyTorchKR"
tags: ["AI", "Agent", "A2A", "프로토콜", "MCP", "상호운용성"]
summary: "A2A는 서로 다른 프레임워크로 만든 에이전트가 내부를 드러내지 않고 작업을 위임하게 하는 개방형 규격이다. 2026년 3월 1.0에 도달했고 Linux Foundation이 관리한다. 데이터 모델·추상 오퍼레이션·프로토콜 바인딩의 3계층 구조와, 0.3에서 넘어올 때 깨지는 지점을 정리했다."
---

> **출처:** [\[A2A 알아보기 1편\] A2A 프로토콜](https://discuss.pytorch.kr/t/a2a-1-0/11892) — 9bow(박정환), PyTorchKR, 2026-09-11
>
> 한국어 원문이라 번역이 아니라 정리 노트다. 명세 내용은 [A2A 공식 명세](https://a2a-protocol.org/latest/)를 함께 확인했다.
>
> 시리즈: **1편 프로토콜** · [2편 Python SDK](/compendium/notes/a2a-python-sdk/)

## 한 줄 요약

A2A(Agent2Agent)는 A팀의 에이전트가 B팀의 에이전트에게 일을 맡길 때마다 둘 사이에만 통하는 연동 코드를 새로 짜는 상황을 없애려는 규격이다. 에이전트는 자기 능력을 적은 JSON 문서 하나만 공개하고, 상대는 그것만 읽고 표준 방식으로 요청한다.

## 무엇을 하지 않는가

이 프로토콜을 이해하는 가장 빠른 길은 경계를 보는 것이다.

- 에이전트 개발 키트가 아니다. LangGraph, CrewAI, Google ADK 자리를 대체하지 않는다.
- 에이전트가 자기 하위 에이전트나 도구를 부르는 방법은 정하지 않는다. 그건 프레임워크나 MCP의 몫이다.
- 사람이 쓰는 메신저가 아니다. 자율 에이전트 사이의 기계 대 기계 통신 규격이다.

MCP(Model Context Protocol)와의 관계도 경쟁이 아니라 분업이다. MCP는 에이전트 하나가 도구·API·데이터에 닿는 법을, A2A는 그렇게 무장한 에이전트들이 서로를 찾아 일을 나누는 법을 표준화한다.

설계 원칙 중 눈에 띄는 것은 불투명한 실행(opaque execution)이다. 협력은 공개한 능력과 주고받은 정보만으로 이뤄지고, 내부 계획이나 도구 구현은 공유하지 않는다. 요청하는 쪽은 상대가 LangGraph인지 Java인지 알 필요가 없고 알 수도 없다.

## 거버넌스와 버전

Google이 만들어 Linux Foundation에 기부했고, 지금은 AWS·Cisco·Google·IBM Research·Microsoft·Salesforce·SAP·ServiceNow가 참여하는 기술 운영 위원회가 관리한다. 명세는 2025년 0.1.0에서 출발해 0.2 계열과 0.3.0을 거쳐 **2026년 3월 1.0.0**에 도달했다. 공식 SDK는 Python, JavaScript, Java, C#/.NET, Go, Rust로 나와 있다.

## 3계층 구조

명세가 세 층으로 갈라져 있고, 이 구분이 읽는 순서를 정해 준다.

1. 정본 데이터 모델(canonical data model) — Task, Message, AgentCard, Part, Artifact, Extension 같은 핵심 구조체. 프로토콜 중립이며 Protocol Buffer로 표현된다. `spec/a2a.proto`가 유일한 정본이라서, 언어별 타입과 JSON Schema는 거기서 생성해야 하고 손으로 고치면 안 된다.
2. 추상 오퍼레이션(abstract operations) — 전송 방식과 무관하게 서술된 11가지 동작. 메시지 전송과 스트리밍 전송, 태스크 조회·목록·취소·구독, 푸시 알림 설정의 CRUD, 확장 카드 조회.
3. 프로토콜 바인딩(protocol binding) — 위 동작을 JSON-RPC, gRPC, HTTP+JSON/REST에 대응시킨다. 예컨대 메시지 전송은 JSON-RPC와 gRPC에서 `SendMessage`, REST에서 `POST /message:send`다.

바인딩이 여러 개여도 클라이언트에게 부담이 되지 않는 이유는 명세가 기능적 동등성을 요구하기 때문이다. 한 에이전트가 여러 바인딩을 열었다면 모두 같은 오퍼레이션과 같은 인증 방식을 제공하고 같은 요청에 의미상 같은 결과를 줘야 한다. 클라이언트는 자기가 다룰 수 있는 걸 고르기만 하면 되고, 무엇을 골랐느냐로 할 수 있는 일이 달라지지 않는다.

## 에이전트 카드

A2A 서버가 반드시 공개해야 하는 JSON 문서다. 클라이언트는 잘 알려진 경로 `/.well-known/agent-card.json`에서 받거나, 목록 서비스를 조회하거나, 미리 설정된 주소를 쓴다.

필수 항목은 name, description, version, supportedInterfaces, capabilities, defaultInputModes, defaultOutputModes, skills다. 이 중 실무에서 중요한 건 둘이다.

`supportedInterfaces`는 접속 주소와 바인딩(`JSONRPC` / `GRPC` / `HTTP+JSON`), 그리고 그 주소가 제공하는 프로토콜 버전을 담는 배열이다. **순서에 의미가 있어서** 앞쪽이 선호 인터페이스이고, 클라이언트는 자기가 지원하는 것 중 가장 앞의 항목을 골라야 한다.

`capabilities`에는 선택 기능이 모여 있다 — streaming, pushNotifications, extendedAgentCard, extensions. 카드에 선언하지 않은 기능을 호출받으면 서버는 정해진 오류를 돌려줘야 하므로, 오퍼레이션 호출 전에 카드부터 확인하는 것이 정석이다. 카드는 RFC 7515의 JSON Web Signature로 서명할 수도 있다.

## 태스크, 메시지, 아티팩트

작업 단위는 태스크(Task)다. 서버가 발급한 식별자와 함께 현재 상태, 결과물 목록, 메시지 기록을 담는다. 상태는 아홉 가지이고 그중 넷(COMPLETED, FAILED, CANCELED, REJECTED)이 종료 상태다. 진행이 막히는 두 상태 INPUT_REQUIRED와 AUTH_REQUIRED가 따로 있는 것이 이 프로토콜의 성격을 보여준다.

헷갈리기 쉬운 구분 하나. **메시지는 대화의 한 턴이고, 아티팩트는 태스크가 만들어 낸 결과물이다.** 명세는 결과를 메시지가 아니라 아티팩트로 돌려주라고 권고하는데, 태스크 기록에 모든 메시지가 보존된다는 보장이 없기 때문이다. 스트림이 끊겼다 다시 붙은 클라이언트는 중간 메시지를 놓칠 수 있으므로, 메시지를 신뢰할 수 있는 전달 수단으로 여기지 말라고 명시한다.

둘의 내용은 파트(Part) 단위로 채워진다. 파트는 text, raw(바이트), url, data(구조화된 JSON) 중 정확히 하나만 갖는다. 여러 태스크를 한 대화로 묶을 때는 contextId를 쓴다.

## 진행 상황을 전달하는 세 경로

오래 걸리는 작업이 설계 전제라서 경로가 셋이다.

- 폴링 — 클라이언트가 주기적으로 태스크를 조회한다. 간단한 연동이나 방화벽 제약이 큰 쪽에 맞는다.
- 스트리밍 — 이벤트를 발생 즉시 흘려보낸다. 대화형 앱, 진행률 표시에 맞는다.
- 푸시 알림 — 서버가 클라이언트 웹훅으로 HTTP POST를 보낸다. 서버 대 서버, 아주 긴 작업에 맞는다. 바인딩과 무관하게 동작해서, gRPC로 서비스하더라도 웹훅은 평범한 HTTP와 JSON을 쓴다.

스트리밍에서 중요한 규정은 순서 보장이다. 이벤트는 생성된 순서대로 전달해야 하고, 한 태스크에 여러 스트림이 붙으면 모두 같은 이벤트를 같은 순서로 받아야 하며, 한 스트림을 닫아도 나머지는 영향받지 않아야 한다. 끊긴 클라이언트가 새 스트림으로 다시 붙는 시나리오가 이 규정 위에서 성립한다.

## 0.3 → 1.0에서 깨지는 것

1.0은 하위 호환이 아니다. 0.3 시절 예제를 그대로 따라 하면 동작하지 않는다. 실무에서 가장 자주 걸리는 둘:

**`kind` 판별자 필드가 사라졌다.** 이제 JSON 멤버 이름 자체가 판별자다. 텍스트 파트는 `{"kind":"text","text":"..."}`에서 `{"text":"..."}`로 납작해졌고, 스트리밍 이벤트는 `{"statusUpdate":{...}}`처럼 감싸인다. Protocol Buffers의 `oneof` 의미론에 맞추기 위한 변경이다.

**`supportsExtendedAgentCard`가 자리를 옮겼다.** 최상위에서 `capabilities.extendedAgentCard`로 들어갔다. 선택 기능은 전부 capabilities 안에 있어야 한다는 정리다.

버전 협상은 요청마다 `A2A-Version` 헤더로 한다. 값은 `1.0`처럼 major.minor까지만 쓴다. **헤더가 비어 있으면 서버는 0.3으로 해석해야 한다** — 이게 조용한 오동작의 흔한 원인이다.

직렬화 규칙도 기억해 둘 만하다. proto의 snake_case는 JSON에서 camelCase가 되고(`context_id` → `contextId`), 열거형은 ProtoJSON 규칙대로 `TASK_STATE_COMPLETED`, `ROLE_USER` 같은 대문자 이름 그대로 나간다.

## 확장

핵심 명세를 건드리지 않고 기능을 덧붙이는 통로가 확장(Extension)이다. 에이전트가 `capabilities.extensions`에 URI와 설명, 필수 여부를 선언하고, 클라이언트는 바인딩별 수단(HTTP 헤더, gRPC 메타데이터)으로 사용할 확장을 밝힌다.

## 함께 읽기

- [A2A Python SDK로 에이전트를 서버로 공개하기](/compendium/notes/a2a-python-sdk/) — 이 시리즈 2편, 여기 나온 개념이 실제 코드와 JSON으로 어떻게 나타나는지
- [Agent-Safe Pipeline](/compendium/notes/agent-safe-pipeline/) — 에이전트가 제안한 action을 policy boundary 뒤에 두는 문제, A2A로 외부 에이전트를 부를 때 같이 생각할 지점
- [지능형 AI Delegation](/compendium/papers/intelligent-ai-delegation/) — 에이전트 간 작업 위임을 언제 어떻게 할 것인가
