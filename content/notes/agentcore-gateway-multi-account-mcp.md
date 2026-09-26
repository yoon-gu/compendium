---
title: "AgentCore Gateway와 MCP로 멀티 어카운트 AI 에이전트 만들기"
date: 2026-09-27
draft: false
source_url: "https://aws.amazon.com/blogs/machine-learning/build-a-multi-account-ai-agent-with-agentcore-gateway-and-mcp/"
author: "AWS Machine Learning Blog"
tags: ["AI", "Agent", "MCP", "AWS", "Bedrock", "AgentCore", "아키텍처", "거버넌스", "블로그"]
summary: "데이터는 각 사업부 계정에 그대로 두고, 중앙 플랫폼 계정의 AgentCore Gateway가 사업부별 MCP 서버를 하나의 엔드포인트로 묶는 허브-스포크 구조. JWT로 최종 사용자 신원을 Gateway까지 전파해 Cedar 정책으로 도구 호출 단위 인가를 걸고, 비용은 계정 경계가 자연히 나눠 준다."
---

> **원문:** [Build a multi-account AI agent with AgentCore Gateway and MCP](https://aws.amazon.com/blogs/machine-learning/build-a-multi-account-ai-agent-with-agentcore-gateway-and-mcp/) — AWS Machine Learning Blog
>
> 아래는 원문을 한국어로 정리한 노트다. 코드와 설정 전문은 원문과 함께 공개된 저장소를 참고.

## 문제 설정

부서마다 자기 AWS 계정에 데이터를 두는 이유는 분명하다 — 소유권이 명확하고, 범위가 격리되고, 배포 주기가 독립적이다. 문제는 에이전트다. 한 계정만 보는 에이전트는 쓸모가 제한되고, 여러 계정을 붙이려 하면 보통 **데이터를 복제하거나 크로스 어카운트 IAM을 엉키게** 만든다.

이 글이 잡는 목표는 그 사이다. 데이터는 원래 있던 사업부(LOB) 계정에 그대로 두고, 요청이 필요로 하는 특정 결과만 질의 시점에 흘러나오게 한다. 원본 데이터셋은 소유 계정을 떠나지 않는다.

## 3계층 구조

**플랫폼 계정 — 에이전트 컨트롤 플레인**

에이전트는 AgentCore Runtime에서 돈다(서버리스, 프레임워크 무관, 전용 microVM 세션 격리, 사용량 과금). 에이전트는 개별 LOB MCP 서버가 아니라 **자기 계정의 Gateway에만** 연결한다.

LLM 추론도 이 계정의 Bedrock에서 돈다. 덕분에 사용 가능한 파운데이션 모델 통제, Guardrails 적용, 비용 추적이 한 경계 안에서 끝난다 — 수십 개 LOB 계정마다 모델 쿼터를 관리하는 오버헤드가 사라진다. 규모가 커지면 추론 전용 계정 여러 개에 분산하고 Gateway를 앞에 세워 Inference Gateway로 쓰는 변형도 언급된다(요청별 프로바이더 선택, 팀별 레이트 리밋).

**LOB 계정 — 데이터와 도구**

S3 버킷이나 DB, Knowledge Base를 날것으로 노출하지 않고, 각 팀이 자기 데이터를 **MCP 서버로 포장**한다. 예시에서 리테일뱅킹 팀은 `get_balance`, `get_profile`을, 여신·자산관리 팀은 `get_credit_score`와 `search_lending_policies`를 내놓는다. 후자는 은행 정책 PDF 위에 올린 Bedrock Knowledge Bases에 RAG 질의를 한다.

MCP 서버도 LOB 계정의 AgentCore Runtime에서 돈다. 여기서 얻는 것은 **도구 표면의 완전한 소유권**이다 — 무엇을 노출하고 그 뒤에 어떤 비즈니스 로직을 둘지 팀이 결정하고, MCP 도구 인터페이스만 유지되면 구현을 바꿔도 플랫폼 에이전트에 영향이 없다.

참고로 원문은 신규 구현이라면 Knowledge Base를 MCP 서버로 감싸는 대신 **Managed Knowledge Base를 Gateway에 네이티브 커넥터로 직접 붙이는** 쪽을 권한다. 검색 인프라를 직접 운영하지 않아도 된다. 레퍼런스 구현이 감싸는 방식을 쓴 것은 검색 파이프라인을 세밀히 통제하기 위해서다.

**Gateway — 허브**

각 LOB는 MCP over Streamable HTTP로 독립 MCP 서버(스포크)를 배포하고, Gateway(허브)가 이들을 하나의 엔드포인트 뒤로 모은다. 에이전트가 보기에 Gateway는 그냥 MCP 서버 하나다. Gateway가 제공하는 것은 시맨틱 검색 기반 통합 도구 탐색, AgentCore Identity를 통한 중앙 인증, Cedar 기반 세분화된 인가, 관측성.

MCP 서버 집계 외에 HTTP 타겟도 지원해서 AgentCore Runtime 에이전트, A2A 서비스, 기타 HTTP 엔드포인트를 각자 서브패스로 같은 거버넌스 엔드포인트에 넣을 수 있다.

## 요청 하나가 계정 경계를 넘는 경로

1. 사용자가 React 웹앱에서 Okta로 로그인 → 신원 클레임(`sub`, `groups`, `audience`)이 담긴 JWT 발급
2. 프롬프트가 CloudFront → ECS/Fargate의 FastAPI 백엔드로
3. 백엔드가 입력에 Bedrock Guardrails로 PII 마스킹(응답에도 다시 적용)
4. 백엔드가 AgentCore Runtime의 Strands Agent를 호출하며 **사용자 JWT를 Authorization 헤더로 그대로 전달** — 신원 전파
5. 에이전트가 Bedrock에 추론 요청 → 어떤 도구를 부를지 판단
6. 에이전트가 JWT를 Gateway로 넘김. Gateway는 시맨틱 검색으로 도구를 찾고, **JWT 클레임을 Cedar 규칙에 대고 평가해** 호출별로 허용/거부
7. 허용된 호출에 대해 Gateway가 AgentCore Identity에서 OAuth 2.0 M2M 자격증명을 받아 붙이고 해당 LOB MCP 서버로 전달. LOB 서버는 인바운드 토큰을 검증한 뒤 처리
8. LOB MCP 서버가 로컬 DynamoDB 조회, 필요하면 S3 + OpenSearch Serverless 위의 Knowledge Base RAG 검색 수행
9. 결과가 같은 경로를 되돌아옴. 샘플 앱의 트레이스 패널이 어떤 LOB가 호출됐고 어떤 정책 거부가 있었는지 보여 줌

여기서 놓치기 쉬운 설계 포인트가 하나 있다. **아웃바운드 호출이 M2M이기 때문에 사용자 단위 인가는 Gateway에서 끝나야 한다.** LOB 서버에 도착하는 토큰은 기계 신원이라 "누가 요청했는가"를 거기서 판단할 수 없다. 그래서 사용자 JWT를 Gateway까지 전파하는 6-7단계가 구조의 핵심이다.

## 인증과 인가

인바운드는 Custom JWT authorizer다. Gateway와 각 LOB Runtime 모두 Okta의 OIDC discovery URL을 가리키고 `aud` 클레임을 검증한다(예시 audience: `lobfederation`).

아웃바운드는 OAuth 2.0 client credentials(M2M). 플랫폼 팀이 AgentCore Identity에 Okta M2M 자격증명을 담은 OAuth credential provider를 등록하고 각 Gateway 타겟에 붙인다. Gateway가 LOB를 호출할 때마다 Identity가 Okta에서 새 액세스 토큰을 받아 헤더에 넣는다.

인가는 Cedar를 쓰는 Policy in AgentCore이고 ENFORCE 모드로 돈다. 규칙은 명시적 `permit` / `forbid` 문장이라, 예컨대 `get_balance` 같은 읽기 도구는 인증된 모든 사용자에게 허용하고, `transfer_funds` 같은 쓰기는 특정 역할로 제한하며, `delete_customer` 같은 파괴적 연산은 누구에게도 금지할 수 있다. **기본 거부(default-deny)** 모델이라 명시적으로 허용된 액션만 통과한다. 플랫폼 팀이 전체 LOB에 걸친 통제권을 갖고, LOB 팀은 MCP 서버 레벨에서 자기 인가를 따로 유지한다.

## 프로덕션으로 가기 전에 짚는 것들

원문이 개발용과 운영용을 구분해 주는 대목들이 실무적으로 유용하다.

- **직접 호출 우회 차단**: LOB Runtime에 `allowedWorkloadConfiguration`을 Gateway ARN으로 설정하면 신원 체인에 그 Gateway가 포함된 요청만 받는다. 이게 없으면 샘플은 OAuth audience 검증에만 의존하는데, 그것만으로는 Gateway 정책과 Cedar 인가를 건너뛰는 직접 호출을 막지 못한다.
- **네트워크**: 레퍼런스 구현은 기본 퍼블릭 네트워크 모드로 HTTPS + OAuth로 공용 인터넷을 지난다. 개발에는 맞지만 운영에는 아니다. 운영에서는 ENI를 통한 VPC 연결, PrivateLink 인터페이스 VPC 엔드포인트로 Gateway 프라이빗 인그레스를 쓴다.
- **Guardrails**: 추론이 중앙화되어 있으니 하나의 guardrail 설정이 모든 LOB 도구 상호작용에 적용된다. 최근 옵션으로는 Gateway에 정책으로 직접 걸어 에이전트 코드 밖에서 검사를 돌릴 수도 있다.
- **감사**: Gateway 로그를 CloudWatch Logs로 내보내면 도구 호출과 요청 메타데이터가 잡힌다. 컨트롤 플레인 작업은 CloudTrail이 기본 수집하고, 개별 도구 호출까지 CloudTrail에 남기려면 advanced event selector로 데이터 이벤트 로깅을 켠다. 중앙 감사는 조직 레벨 트레일로 플랫폼·LOB 계정 로그를 전용 로깅 계정에 모은다.

## 지속적 평가

에이전트가 여러 LOB의 도구를 오케스트레이션하는 구조에서는 도구·모델·프롬프트가 바뀌어도 여전히 제대로 도는지 확인할 방법이 필요하다. AgentCore Evaluations가 두 모드를 제공한다.

- **온라인 평가**: 운영 트래픽의 일부(예: 세션 10%)를 계속 채점한다. 내장 평가자는 Tool Selection Accuracy, Correctness, Goal Success Rate. 에이전트가 이미 OpenTelemetry 트레이스를 내보내고 있으면 코드 변경 없이 Observability 대시보드에 점수가 올라온다. 지연이나 에러율 모니터링이 놓치는 조용한 성능 저하 — 예를 들어 여신 질의를 엉뚱한 LOB로 보내는 것 — 을 잡아낸다.
- **온디맨드 평가**: 개발과 CI/CD용 실시간 API. 시나리오와 기대 응답·도구 궤적·목표 단정을 묶은 평가 데이터셋을 한 번 정의하면 변경마다 재생한다.

두 모드가 **같은 평가자를 공유**한다는 점이 좋다. 배포 전에 게이트로 거는 기준과 운영에서 모니터링하는 기준이 정확히 일치한다. 여기에 AgentCore Optimization이 운영 트레이스를 분석해 프롬프트와 도구 설명 개선안을 제안한다.

## 비용 귀속

이 구조는 비용 경계를 자연스럽게 만든다. LOB의 데이터 플레인 비용(DynamoDB, Knowledge Bases, MCP 서버 컴퓨트)은 자기 계정에 남아 Cost Explorer에 바로 보인다. LLM 추론과 Gateway 호출 비용은 플랫폼 계정에 쌓인다.

플랫폼 계정 비용을 LOB로 되돌리려면 에이전트 실행 역할에 태그(`lob`, `costCenter` 등)를 달고 Billing 콘솔에서 비용 할당 태그를 활성화해 Cost and Usage Report로 흘려보낸다. 도구 트레이스가 어느 LOB의 도구를 불렀는지 기록하니 비례 배분 근거로 쓸 수 있다.

## 새 사업부 온보딩

이 패턴의 확장성이 여기서 드러난다. 플랫폼 팀이 **Gateway 타겟 하나를 추가**하면, 에이전트는 다음 `tools/list` 호출에서 새 도구를 발견한다. 에이전트는 시작 시 AWS Agent Registry(프리뷰)에 질의해 등록된 LOB MCP 서버를 찾는다. 에이전트 코드를 고칠 일이 없다.

## 메모

- 저장소에 딸린 배포 스크립트가 CDK로 4개 계정을 부트스트랩하고, Okta 설정과 MCP 서버·Gateway 타겟 배포, CloudFront 뒤 ECS의 React 앱까지 올린다. 정리 스크립트는 역순으로 제거한다. 계정 4개와 Okta가 필요하니 가볍게 따라 해 볼 성질은 아니다.
- 전제 조건: AWS Organizations 기반 멀티 어카운트, 플랫폼 계정의 Bedrock 모델 접근 권한, 양쪽 계정의 AgentCore 구성, OIDC 호환 IdP(Okta·Cognito·Entra ID 등)의 M2M 앱 클라이언트.
- AWS 자사 서비스 소개 글이라 대안 비교는 없다. 다만 "데이터는 두고 결과만 흘린다", "사용자 신원을 게이트웨이까지 전파해 도구 호출 단위로 인가한다", "기본 거부" 세 가지는 벤더와 무관하게 사내 멀티 계정 에이전트를 설계할 때 그대로 쓸 수 있는 원칙이다.
