---
title: "AWS로 구축하는 AI 기반 지식 관리 시스템"
date: 2026-08-24
draft: false
source_url: "https://aws.amazon.com/blogs/machine-learning/democratizing-institutional-knowledge-building-an-ai-powered-knowledge-management-system-with-aws/"
author: "Nneoma Okoroafor, Kenneth Walsh, Olalekan Fagbo, Adeogo Olajide"
tags: ["AI", "AWS", "Knowledge Management", "RAG", "Amazon Bedrock"]
summary: "AWS Blog가 소개한 AI 기반 institutional knowledge 관리 시스템 구현 글이다. Amazon Bedrock Knowledge Bases, S3, OpenSearch Serverless, DynamoDB cache, Lambda, Cognito, API Gateway, Polly, Transcribe, avatar UI를 조합해 조직 내부 지식을 voice-first 인터페이스로 제공하는 reference architecture와 배포 절차, 비용·성능·운영 caveat를 설명한다."
---

> **원문:** [Democratizing institutional knowledge: Building an AI-powered knowledge management system with AWS](https://aws.amazon.com/blogs/machine-learning/democratizing-institutional-knowledge-building-an-ai-powered-knowledge-management-system-with-aws/) — Nneoma Okoroafor, Kenneth Walsh, Olalekan Fagbo, Adeogo Olajide, 2026년 8월 24일
>
> 아래 글은 AWS Machine Learning Blog 원문의 구조와 서술을 따라가며 한국어로 옮기고, foundation model / BERT practitioner가 architecture와 운영 caveat를 빠르게 파악할 수 있도록 일부 practitioner notes를 덧붙인 것이다.

여러 산업의 조직은 오랜 운영 과정에서 축적된 집단적 지혜와 경험, 즉 institutional knowledge를 관리하는 데 어려움을 겪는다. 흔히 “tribal knowledge”라고 불리는 이 지식은 핵심 인력이 떠날 때 함께 사라지곤 하며, 그 결과 효율성과 혁신에 영향을 주는 knowledge gap이 생긴다. 전통적인 문서화 방식은 충분하지 않은 경우가 많았고, 정작 필요할 때 정보가 오래되었거나 접근하기 어려운 상태로 남는 문제가 반복됐다.

이 글은 AWS 서비스로 구동되는 intelligent avatar system을 통해 institutional knowledge를 capture, maintain, deliver하는 customizable, smart-caching cloud 기반 solution을 소개한다.

## 누가 이 solution을 써야 하는가

다양한 산업의 조직이 이 system을 사용해 중요한 지식을 보존할 수 있다. 예를 들어 제조 조직은 숙련 technician이 은퇴하기 전에 생산 절차와 maintenance protocol을 capture할 수 있다. Healthcare, financial services, energy, government agency 같은 다른 조직도 각자의 use case에 맞게 solution을 조정할 수 있다. Knowledge worker는 여러 repository를 직접 검색하는 대신 natural language query로 절차와 policy에 접근할 수 있고, subject matter expert나 은퇴 예정 직원은 자신의 expertise를 미래 세대를 위해 문서로 upload할 수 있다.

조직은 상세 research를 위한 desktop browser access, hands-free operation을 위한 voice interaction, 빠른 참조를 위한 text-based query를 함께 배포할 수 있으며, 각 산업의 operational context에 맞춰 system을 조정할 수 있다.

## Solution overview

이 solution은 AWS 서비스를 사용해 조직의 필요에 맞게 조정할 수 있는 scalable, configurable knowledge management system을 만든다. Architecture의 중심에는 advanced AI capability와 robust cloud infrastructure를 결합해 intuitive하고 responsive한 knowledge delivery system을 제공하는 설계가 있다.

핵심 foundation은 text와 voice interaction을 모두 지원하는 browser-based interface다. 사용자는 자연스러운 대화를 통해 지식에 접근할 수 있다. 이 interface는 configurable avatar system에 연결되며, 어떤 AI avatar solution과도 함께 동작할 수 있도록 설계되어 조직이 선호하는 avatar technology를 선택하거나 나중에 바꿀 수 있는 flexibility를 제공한다.

![Knowledge management system solution architecture](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-1-2.png)

*Figure 1: Knowledge management system의 solution architecture.*

Behind the scenes에서 [Amazon Cognito](https://aws.amazon.com/cognito/)는 access management를 보호하고, Amazon API Gateway는 system component에 대한 controlled, monitored access를 제공한다. Knowledge-processing core는 managed Retrieval Augmented Generation(RAG)을 위해 Amazon Bedrock Knowledge Bases를 사용한다. Amazon Simple Storage Service(Amazon S3)에 저장된 institutional knowledge가 data source가 되고, Amazon Bedrock이 chunking, Amazon Titan Text Embeddings 기반 embedding, retrieval을 처리해 각 answer를 조직 고유 문서에 grounding한다. Knowledge base는 Amazon OpenSearch Serverless vector store로 뒷받침된다. Amazon DynamoDB는 response caching을 제공하고, AWS Lambda function은 workflow를 orchestrate한다.

비용상 중요한 점이 있다. Amazon OpenSearch Serverless vector store는 deployment 과정에서 사용자의 account 안에 생성되며, query volume과 별개로 always-on minimum이 있는 OpenSearch Compute Unit(OCU) 기준으로 과금된다. Budget을 잡을 때 이는 고정 baseline cost로 봐야 하며, 기본 floor 기준으로 월 수백 달러 수준이 될 수 있다. 이 solution에서 가장 큰 fixed cost component다. 아래의 smart caching을 통한 cost optimization은 이 baseline 위에 variable inference cost를 줄이는 방식이다.

## 왜 이 solution인가?

Institutional knowledge를 보존하려는 조직은 Amazon Bedrock 위에 custom solution을 만들거나 text-based chat agent를 배포하는 등 여러 접근을 택할 수 있다. 이 solution은 세 가지 핵심 capability로 차별화된다.

Voice-first, avatar-driven delivery. 이 solution은 text-only chat interface가 아니라 AI-powered avatar와의 voice interaction을 중심으로 설계됐다. Non-technical end user는 거의 learning curve 없이 사용할 수 있다. 동료에게 묻듯 avatar에게 말하고 spoken answer를 받는다. Training room, control room, quality lab, maintenance-planning office처럼 connected setting에서 일하는 worker는 절차를 검토하면서 hands-free로 system에 query할 수 있다. Avatar-based interaction은 text-only chatbot보다 non-technical population의 adoption과 trust를 높일 수도 있다. 단, 이것은 cloud-connected design이다. Connectivity requirement는 아래 scalability/performance 특성에서 다시 다룬다.

Simplicity for knowledge owners. Content management에는 technical expertise가 필요하지 않다. Knowledge owner는 Word, PDF, plain text, Markdown, JSON 같은 기존 문서를 Amazon S3에 upload하기만 하면 된다. Ingestion sync가 각 document를 chunk하고 vector store에 embed한 뒤 query 가능하게 만든다. 새 document는 automated sync가 끝난 직후부터 query 가능하지만, 즉시 반영되는 것은 아니다. Content를 재구성하거나 metadata를 tag하거나 retrieval pipeline을 수작업으로 만들 필요가 없다.

Rapid deployment with built-in cost optimization. 전체 prototype은 AWS CloudFormation을 통해 몇 시간 안에 배포할 수 있다. Built-in DynamoDB cache는 반복 질문에 대해 이전 answer를 재사용해 variable AI inference cost를 낮춘다. AWS의 테스트에서는 반복 질문이 많은 workload에서 50-70% cache hit rate가 가능했다. 실제 savings는 query mix가 얼마나 반복적인지에 달려 있다.

### 대안과 비교하면

Amazon Bedrock 위에 custom solution을 직접 만들면 full architectural control을 얻을 수 있지만, voice processing, avatar rendering, caching, retrieval pipeline을 각각 설계하고 통합해야 한다. 보통 수 주에서 수개월이 걸리고, 여러 AWS service에 대한 깊은 technical expertise가 필요하다.

Amazon Q나 custom Amazon Bedrock chat interface 같은 text-based chat agent는 더 빠른 deployment path를 제공하며 typed knowledge retrieval에 강하다. 이 solution은 그 위에 voice-first interaction과 avatar engagement를 더해, hands-free access가 중요한 frontline worker의 adoption을 개선한다.

따라서 이 solution은 gap을 메운다. 몇 시간 안에 배포할 수 있는 production-quality accelerator이고, voice-first visual avatar engagement를 제공하며, smart caching으로 비용을 최적화한다. Non-technical worker에게 institutional knowledge를 빠르고 비용 효율적으로 제공해야 하는 조직에는 이런 capability를 독립적으로 조립하는 복잡성을 줄여 준다.

### 이 solution을 선택할 때

다음이 필요하다면 이 accelerator를 선택할 수 있다.

- Non-technical worker나 frontline worker에게 voice와 visual interaction으로 institutional knowledge를 전달해야 한다.
- 처음부터 직접 구축하기보다 검증된 prototype을 빠르게 배포해야 한다.
- Intelligent caching으로 AI inference cost를 줄여야 한다.
- 은퇴하는 expert의 knowledge를 최소 friction으로 보존해야 한다.

## Implementation journey

Implementation journey는 knowledge foundation setup, infrastructure deployment, AI integration의 세 단계로 구성된다. 각 단계는 이전 단계 위에 쌓여 comprehensive knowledge management system을 만든다.

Phase 1: Knowledge foundation setup. 구현은 institutional knowledge를 정리하는 것에서 시작한다. Document를 Amazon S3 knowledge repository에 upload하고, Amazon Bedrock Knowledge Bases가 그곳에서 ingest한다. Source content가 다른 system이나 format에 있다면 AWS Glue ETL job을 선택적으로 추가해 upload 전에 AI-optimized format으로 변환할 수 있다. 이 ETL step은 별도의 optional integration이며 CloudFormation deployment가 자동 생성하지 않는다. 이미 아래 supported format에 해당하는 문서를 가진 조직은 S3에 바로 upload하면 된다.

Key considerations:

- Supported formats: Word, PDF, plain text, Markdown, JSON 등 다양한 format을 사용할 수 있다.
- Optimal output: 가장 좋은 AI retrieval performance를 위해 Markdown(`.md`)이나 structured JSON을 권장한다.
- ETL handles the conversion: optional AWS Glue ETL job을 사용하는 경우 source document를 S3에 upload하기 전에 권장 output format으로 변환한다.

Data extraction과 transformation에서 AWS Glue를 사용하는 자세한 방법은 [AWS Glue ETL documentation](https://docs.aws.amazon.com/glue/latest/dg/author-job-glue.html)을 참고한다.

Phase 2: Infrastructure deployment. Core infrastructure deployment는 AWS CloudFormation template에서 시작한다. 이를 통해 consistent하고 repeatable한 deployment를 만든다. 이 단계에는 다음이 포함된다.

- Secure user authentication과 access control을 위한 Amazon Cognito 설정.
- Component 간 communication을 관리하는 API Gateway endpoint 구성.
- Knowledge storage를 위한 S3-based repository 구축.
- Response caching을 위한 DynamoDB 구현.

Phase 3: AI integration. 마지막 단계는 AI capability와 processing pipeline을 통합한다.

- Knowledge processing과 query understanding을 위한 Amazon Bedrock 구성.
- Request orchestration과 response handling을 위한 Lambda function 설정.
- Audio processing pipeline 구현:
  - Voice input을 text로 변환하는 Amazon Transcribe.
  - Text response를 natural speech로 바꾸는 Amazon Polly.
- Human-like interaction을 위한 chosen avatar system 통합.

System은 intelligent caching algorithm으로 response time을 크게 줄이면서 information accuracy를 유지한다. 이 component 조합 덕분에 text든 voice든 선호하는 communication method로 knowledge base와 상호작용할 수 있다.

Implementation steps는 Auto Demo application을 배포하는 절차를 설명한다. 아래 단계는 `us-east-1`에서 작성·테스트됐다. 이 Region은 여기서 사용하는 foundation model(FM)과 avatar streaming의 availability가 가장 넓기 때문에 선택됐다. 다른 AWS Region에 배포한다면 시작 전에 선택한 Amazon Bedrock model과 avatar provider가 해당 Region에서 사용 가능한지 확인하고, source 안에 hardcoded Region이 있다면 수정해야 한다.

## Prerequisites

Initial deployment에는 IT 또는 DevOps team의 일회성 technical capability가 필요하다. AWS Management Console 기본 navigation, infrastructure-as-code 이해, identity management familiarity가 포함된다.

End user에게는 technical capability가 필요하지 않다. Conversational interface가 barrier를 줄인다. 사용자는 URL에 접속한 뒤 human expert와 대화하듯 text나 voice로 자연스럽게 interaction하면 된다.

### AWS account

- S3 bucket 생성, CloudFormation stack 생성, Amazon Bedrock model invocation이 가능한 AWS account access.
- AWS resource를 deploy하고 manage하기 위한 적절한 AWS Identity and Access Management(IAM) permission.

### Service별 required IAM permissions

CloudFormation stack은 여러 AWS service에 걸쳐 resource를 만들고 관리한다. 이 solution을 deploy하고 operate하려면 deployment IAM role 또는 user가 다음 service에 대한 permission을 가져야 한다.

- Amazon Bedrock: foundation model invocation과 Amazon Bedrock Knowledge Bases retrieval.
- Amazon S3: knowledge base storage와 application file.
- AWS Lambda: request orchestration을 위한 serverless compute.
- Amazon Cognito: user authentication과 access management.
- API Gateway: HTTP endpoint management.
- Amazon OpenSearch Serverless: Amazon Bedrock knowledge base를 backing하는 vector store.
- Amazon Polly: voice response를 위한 text-to-speech.
- Amazon Transcribe: voice input을 위한 speech-to-text.
- Amazon CloudWatch Logs: centralized logging.
- IAM PassRole: Lambda와 knowledge-base execution role을 위한 service-role delegation.

Production deployment에서는 least privilege principle을 따르고 resource ARN을 특정 account와 Region으로 scope하는 것이 좋다. CloudFormation stack은 runtime operation에 필요한 execution role을 적절히 scoped된 permission으로 자동 생성한다.

Foundation model access도 확인해야 한다. 이 solution은 document를 vector store에 embed하기 위해 Amazon Titan Text Embeddings(`amazon.titan-embed-text-v1`)를 사용하고, answer generation을 위한 selectable model로 Amazon Nova Pro(`amazon.nova-pro-v1:0`)와 Anthropic Claude 3 Sonnet(`anthropic.claude-3-sonnet-20240229-v1:0`)을 사용한다. Amazon Bedrock은 Amazon-owned serverless model에 대한 automatic access를 제공하므로 Amazon Nova Pro와 Amazon Titan Text Embeddings는 manual enablement 없이 기본적으로 사용할 수 있다. Anthropic Claude model은 모든 Region에서 automatic access 대상이 아니므로, 첫 Claude request 전에 Amazon Bedrock console에서 one-time Anthropic model-access request를 완료하고 account에 필요한 AWS Marketplace subscription permission이 있는지 확인해야 한다. Account administrator는 IAM policy와 Service Control Policy(SCP)를 통해 model을 더 제한하거나 대체할 수 있다. 자세한 내용은 [Amazon Bedrock now provides automatic access to serverless foundation models in your AWS Region](https://aws.amazon.com/blogs/security/simplified-amazon-bedrock-model-access/)을 참고한다.

## Walkthrough: Code installation steps

Application source code는 GitHub의 public [sample-bedrock-knowledge-management-avatar-system repository](https://github.com/aws-samples/sample-bedrock-knowledge-management-avatar-system)를 clone해 가져온다. Application은 `bedkbauto/` folder 아래에 있으며, `src`와 `web` subfolder를 사용한다.

### S3 bucket 생성

- AWS Management Console에 로그인한다.
- S3 service로 이동한다.
- Application file을 저장할 새 S3 bucket을 생성한다.
- 다음 구조를 따르도록 추가 folder를 만든다: `s3://<amzn-s3-demo-bucket>/content/bedkbauto/`.

### Application file upload

- Application source code가 들어 있는 downloaded folder의 압축을 푼다.
- 앞 단계에서 만든 S3 bucket에 압축 해제된 folder content를 upload한다. 이때 `src`와 `web` folder만 upload한다.

![src와 web subfolder upload](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-2-2.jpeg)

*Figure 2: Amazon S3에 upload할 `src`와 `web` subfolder.*

### S3 object URL 가져오기

- S3 console로 이동한다.
- Uploaded application file의 `src` folder에서 `setup.json` file을 찾는다.
- `setup.json` file의 URL을 복사한다. 예시는 다음과 같다: `https://<amzn-s3-demo-bucket>/content/bedkbauto/src/setup.json`.

### CloudFormation stack 생성

- [CloudFormation console](https://us-east-1.console.aws.amazon.com/cloudformation/home)로 이동한다.
- **Create stack**을 선택한 뒤 **With new resources (standard)**를 선택한다.
- **Specify template** 단계에서 **Amazon S3 URL**을 선택하고, 앞에서 복사한 URL을 붙여 넣는다.

![CloudFormation template URL 지정](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-3-2.jpeg)

*Figure 3: Amazon S3 URL로 template 지정.*

- Stack creation 과정에서 stack name, app login용 one-time password를 받을 **email address**, `demo-user` 같은 app login용 **username**, 그리고 앞에서 만든 S3 bucket name(예: `<amzn-s3-demo-bucket>`)을 parameter로 제공한다.

![CloudFormation stack parameter 입력](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-4-2.jpeg)

*Figure 4: Stack parameter 제공.*

- 나머지 setting은 default로 두고, **I acknowledge that AWS CloudFormation might create IAM resources with custom names**와 **I acknowledge that AWS CloudFormation might require the following capability: CAPABILITY_AUTO_EXPAND** 두 acknowledgment checkbox를 선택한다.

![CloudFormation required capabilities 확인](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-5-2.jpeg)

*Figure 5: Required capability acknowledgement.*

- Review page에서 **Submit**을 선택해 stack을 생성한다.

![CloudFormation stack review와 submit](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-6-2.jpeg)

*Figure 6: Stack review와 submit.*

### Deployment verify

- CloudFormation stack creation이 완료되면 **Outputs** tab을 열어 application에 접근한다.

![CloudFormation Outputs의 FrontendURL](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-7-2.jpeg)

*Figure 7: Outputs tab에서 `FrontendURL` 찾기.*

- `FrontendURL` 값을 새 tab에 복사하고 **Enter**를 누른다.
- Stack creation 때 설정한 username과 email address로 받은 password를 입력한다.

![Temporary password로 sign-in](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-8-1.jpeg)

*Figure 8: Temporary password로 sign in.*

- 원하는 password로 변경하고 **Send**를 선택한다.

![새 password 설정](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-9-2.jpeg)

*Figure 9: 새 password 설정.*

이제 UI에 접근할 수 있다.

![Deployed Knowledge Base Demo interface](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-10-1.jpeg)

*Figure 10: 배포된 Knowledge Base Demo interface.*

![Avatar가 질문에 답하는 Knowledge Base Demo](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/10/ML-18543-11.png)

*Figure 11: Avatar를 통해 질문에 답하는 Knowledge Base Demo.*

## Performance와 user experience 최적화

이 knowledge management system은 response speed와 efficiency를 극대화하기 위해 dual-layer caching strategy를 사용한다. Front end에서는 browser-side caching이 LRU(Least Recently Used) algorithm을 사용해 최근 interaction을 user browser memory에 직접 저장한다. 이 local cache는 반복 질문에 대해 server request를 최소화하고 common query에 instant response를 제공한다. Backend DynamoDB cache는 더 넓은 knowledge repository를 유지하며, content type에 따라 달라지는 intelligent TTL(Time-To-Live) setting을 사용한다. Fundamental knowledge는 더 오래 보존하고, operational procedure는 중간 기간, time-sensitive information은 짧은 기간으로 유지한다. 이 tiered approach는 information freshness를 유지하면서 AI service의 processing load를 줄인다. 다만 current implementation은 exact query text 기준으로 cache entry를 match하므로, established, frequently recurring question을 사용자가 반복할 때 가장 효과적이다. Semantic, embedding-based matching은 자연스러운 enhancement지만 이 prototype에는 포함되어 있지 않다.

Avatar system은 단순한 visual interface 이상이다. Complex information을 accessible하고 engaging하게 만드는 핵심 component다. DeepBrain AI technology 위에 구축된 avatar는 real-time lip synchronization, contextual facial expression, natural gesture를 제공하며 conversation flow에 맞춘다. 조직은 avatar의 appearance, voice, behavior를 brand identity와 communication style에 맞게 customize할 수 있다.

Technical implementation은 smooth video streaming을 위해 WebRTC를 사용하고 natural speech synthesis를 위해 Amazon Polly와 통합된다. WebSocket connection은 responsive avatar control을 가능하게 한다.

Amazon CloudWatch를 통한 performance monitoring은 cache effectiveness와 response time에 대한 continuous insight를 제공한다. System은 usage pattern을 기반으로 caching strategy를 자동 조정하고, 자주 access되는 information을 warming하며 TTL setting을 최적화한다. Efficient caching과 natural avatar interaction의 조합은 조직 규모에 맞게 scale되는 responsive, engaging knowledge delivery system을 만든다.

## Scalability와 performance characteristics

Serverless architecture는 component 전반에 automatic horizontal scaling을 제공하므로, pilot에서 enterprise deployment까지 growth를 manual intervention 없이 처리할 수 있다. Concurrent request가 증가하면 function은 추가 execution environment를 provision하고, traffic spike도 performance degradation 없이 처리한다. API layer는 throttling을 제공하면서 varying load를 처리하도록 scale되고, caching layer도 query volume 변동에 맞춰 capacity를 자동 조정한다.

Concurrent user support는 configuration에 따라 scale된다. 다음 수치는 AWS 테스트에서 나온 indicative estimate이지 guarantee가 아니며, Region, model choice, document size, cache hit rate, configured service quota에 따라 달라진다. Default setup은 cached query에 대해 sub-second response로 약 50-100 concurrent user를 처리했다. 관련 service quota를 올리면 약 500-1,000 concurrent user까지 확장할 수 있고, 같은 architecture로 5,000명 이상의 enterprise-scale concurrent usage도 가능하지만 proactive service-quota increase가 필요하다.

Performance는 caching effectiveness에 따라 달라진다. AWS 테스트에서 cached response는 1초보다 훨씬 빠르게 반환됐고, fresh knowledge-base query는 model과 document size에 따라 대략 2-4초가 걸렸다. Voice interaction은 여기에 speech-processing time을 추가한다. 이는 indicative figure이므로 latency target을 약속하기 전에 자체 workload로 측정해야 한다. 또한 이것은 cloud-dependent design이다. 모든 query는 AWS로 round-trip하며, avatar는 live WebRTC/WebSocket streaming에 의존하므로 stable하고 low-latency이며 충분한 bandwidth의 connectivity가 필요하다. 이 prototype에는 edge, offline, degraded-mode capability가 없다. 따라서 training room, engineering/maintenance-planning office, quality lab, control room, kiosk station 같은 connected environment에 적합하며, disconnected 또는 intermittent connectivity가 있는 plant-floor/OT setting에는 그대로 맞지 않는다. 그런 환경을 지원하려면 local caching, offline fallback, graceful degradation to text 같은 별도 edge pattern이 필요하다.

Growth를 계획하는 조직은 pilot 단계에서는 default configuration으로 시작하고, metric을 monitoring해 bottleneck을 찾고, threshold에 접근할 때 capacity limit을 높이며, enterprise deployment 전 service quota increase를 proactive하게 요청하는 방식이 좋다. Serverless architecture는 실제 사용량에 대해서만 비용을 지불하도록 도와 작은 규모로 시작해 adoption에 따라 scale하기 쉽게 만든다.

## Smart caching을 통한 cost optimization

Efficiency의 핵심 contributor는 caching layer다. 이 layer는 가장 큰 variable cost인 repeated foundation model call을 줄인다. DynamoDB cache는 반복 query에 대한 answer를 저장하고 재사용하므로, 이미 answer된 question은 또 다른 model invocation을 trigger하지 않는다. AWS 테스트에서 이는 cache hit rate에 거의 비례해 inference cost를 줄였다. 50-70%의 question이 반복되는 workload에서는 inference cost도 비슷한 정도로 줄었다. Saving은 hit rate의 직접 함수이므로, AWS는 이를 독립적인 guarantee 두 개로 보지 않고 하나의 figure로 제시한다. 이 variable saving은 앞서 언급한 fixed Amazon OpenSearch Serverless baseline 위에 얹히므로, 두 비용을 모두 budget에 포함해야 한다.

System의 smart-caching mechanism은 많은 질문이 established procedure, policy, institutional practice와 관련된 tribal knowledge use case에서 특히 효과적이다. Time-based cache invalidation을 구현함으로써 cost efficiency와 information accuracy 사이의 balance를 유지한다.

## System 유지와 진화

장기적 성공의 핵심은 knowledge management system을 조직과 함께 성장하는 dynamic system으로 다루는 것이다. Knowledge base를 최신 상태로 유지하기 위해 deployment는 knowledge repository의 Amazon S3 event notification을 구성한다. Document가 추가되거나 제거되면 bucket이 AWS Lambda function을 호출하고, 이 function이 Bedrock Knowledge Bases ingestion job을 자동으로 시작해 변경 사항을 vector store에 다시 embed한다. Manual step은 없다. Ingestion은 즉시 완료되지 않으므로 updated content는 sync가 끝난 뒤 shortly query 가능해진다. Response cache의 content-type-aware TTL setting은 이를 보완한다. Fundamental process는 더 오래 유지하고 dynamic information은 더 자주 refresh한다.

Accuracy를 지원하기 위해 answer는 Amazon Bedrock Knowledge Bases로 생성된다. 이 방식은 model의 general training data가 아니라 조직이 검증한 문서에서 retrieved passage에 각 response를 grounding한다. Grounding은 fabricated answer나 off-base answer의 가능성을 줄이며, knowledge base가 source citation을 반환할 수 있으므로 user에게 verification을 위해 노출할 수 있다. 하지만 grounding은 incorrect answer risk를 줄일 뿐 제거하지 않는다. High-consequence 또는 safety-relevant decision에서는 human-in-the-loop을 유지하고, system을 authoritative source가 아니라 decision support로 다뤄야 한다. Explicit confidence threshold나 answer-validation check는 이런 use case의 권장 enhancement지만 이 prototype에는 구현되어 있지 않다.

Security도 system maintenance에서 핵심이다. Regular automated audit은 access control과 data protection measure를 verify하고, modular architecture는 security update를 straightforward하게 만든다. 조직은 기존 functionality를 중단하지 않고 새로운 security requirement나 compliance measure를 통합할 수 있다.

System의 flexibility는 content management까지 확장된다. Team이 새 procedure를 문서화하거나 기존 procedure를 update하면 knowledge base에 upload할 수 있고, system은 이런 변경 사항을 자동으로 incorporate한다. 이러한 continuous evolution은 system이 organizational change에 적응하면서 historical context를 유지하는 reliable source of institutional knowledge로 남게 한다.

## Conclusion

이 knowledge management solution을 사용하면 institutional knowledge를 보존하는 강력한 tool을 만들 수 있다. AWS service와 modular design을 사용함으로써 조직은 intellectual capital을 유지하고 workforce 전체에서 efficient knowledge transfer를 촉진할 수 있다. System의 flexibility와 scalability는 여러 industry와 use case에 적합하며, digital age의 sustainable knowledge management를 위한 foundation을 제공한다. 시작하려면 GitHub의 [sample repository](https://github.com/aws-samples/sample-bedrock-knowledge-management-avatar-system)를 clone해 자신의 AWS account에 solution을 deploy하면 된다. 더 알아보려면 Amazon Bedrock console에서 Amazon Bedrock Knowledge Bases를 탐색할 수 있다.

## Practitioner notes

이 글은 vendor implementation article이지만, architecture pattern 자체는 일반적인 enterprise RAG deployment에서도 유용하다.

- Retrieval layer는 Amazon Bedrock Knowledge Bases에 맡기고, source of truth는 S3 document repository로 둔다. 이때 ingestion latency와 source citation 노출 여부가 production UX의 핵심이다.
- Cache layer는 cost optimization뿐 아니라 latency UX에도 직접 영향을 준다. 다만 exact query match cache는 paraphrase에 약하므로, 반복 질문이 많은 help-desk/operations workload에는 잘 맞지만 open-ended research workload에는 semantic cache가 필요할 수 있다.
- Avatar/voice UI는 adoption에는 도움이 될 수 있지만, WebRTC/WebSocket connectivity와 speech-processing latency라는 새로운 failure mode를 만든다. Critical operation 환경에서는 text fallback과 operator verification path를 별도로 설계해야 한다.
- OpenSearch Serverless OCU baseline은 “serverless라서 거의 0부터 시작한다”는 기대와 다를 수 있다. Pilot budget에서도 fixed baseline과 variable inference cost를 분리해 계산해야 한다.
- Grounded RAG라도 hallucination risk가 0이 되지는 않는다. 특히 safety, legal, regulated workflow에서는 citation display, confidence threshold, approval workflow, audit log가 필요하다.

## About the authors

Nneoma Okoroafor는 AWS Partner Solutions Architect로, 조직이 next-generation cloud와 AI solution을 architect, scale, optimize하도록 돕는다. Machine learning과 generative AI workflow에 대한 깊은 전문성을 바탕으로 global startup partner ecosystem과 함께 secure하고 efficient한 cloud architecture를 만든다.

Olalekan Fagbo는 AWS Prototyping and AI Customer Engineering(PACE) team의 Prototyping Architect다. Customer와 직접 협업해 AWS service로 가능한 것을 보여 주는 functional prototype을 빠르게 만들며, generative AI, machine learning, security solution을 전문으로 한다.

Kenneth Walsh는 New York 기반 Senior AI Acceleration Architect로, generative AI automation tool을 사용해 AWS builder productivity를 높이는 일을 돕는다. Technical expertise와 passion을 바탕으로 customer의 generative AI journey를 지원한다.

Adeogo Olajide는 AWS Solutions Architect로, GovTech customer와 public sector customer의 cloud transformation을 지원한다. Secure, scalable, compliant architecture를 설계해 public sector organization이 digital service를 modernize하도록 돕는다.
