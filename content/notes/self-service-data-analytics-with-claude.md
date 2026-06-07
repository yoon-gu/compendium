---
title: "Claude로 셀프서비스 데이터 분석을 가능하게 하는 방법"
date: 2026-06-07
draft: false
source_url: "https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude"
author: "Chen Chang, Clement Peng, Justin Leder, Johanne Jiao, Josh Cherry"
tags: ["AI", "Claude", "데이터 분석", "에이전트", "엔터프라이즈 AI", "데이터 엔지니어링"]
summary: "Anthropic은 비즈니스 분석 질의의 95%를 Claude로 자동화하면서, 정확도를 코드 생성 문제가 아니라 맥락·검증·데이터 거버넌스 문제로 다룬다. 이 글은 데이터 foundation, source of truth, skill, eval, ablation, online validation으로 구성된 agentic analytics stack과 운영 원칙을 정리한다."
---

> **원문:** [How Anthropic enables self-service data analytics with Claude](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude) — Anthropic, 2026년 6월 3일
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 제품명, metric, API, skill 구조처럼 구현에 가까운 용어는 필요할 때 영어 원문을 함께 둔다.

많은 데이터 과학(data science) 팀과 데이터 엔지니어링(data engineering) 팀이 증언할 수 있듯, 셀프서비스 비즈니스 분석(self-service business analytics)을 가능하게 하는 일은 전통적으로 고된 작업이었다.

덜 기술적인 동료들이 데이터 모델에 더 쉽게 접근할 수 있도록 넓고 비정규화된 테이블을 만들면, 비즈니스가 커질수록 정의가 서로 다른 중복 view가 생기기 쉽다. SQL을 배우고 싶어 하지 않는 직원과의 간극을 메우는 데도 별 도움이 되지 않는다. 반대로 사용자를 위해 더 엄격히 구획된 환경을 만들면, 비즈니스 질문의 long tail을 놓치기 쉽고, 팀들이 각자의 방식으로 silo화되면서 metric과 dashboard가 불어난다.

LLM의 등장은 이런 문제를 피할 수 있는 셀프서비스 분석의 또 다른 경로를 제공한다. 하지만 Claude를 warehouse에 연결하고 agent가 실행하게만 두면, 정밀해 보이지만 실제로는 그렇지 않은 false sense of precision이 생길 수 있다.

임시 분석 요청에서 해방되었다는 초기의 기쁨은 곧 불안으로 바뀐다. 그런 설정은 stakeholder를, 이전에는 신중히 curate된 dataset으로 이끌어 주던 underlying infrastructure, documentation, expertise로부터 분리한다는 사실을 깨닫기 때문이다.

Anthropic에서는 비즈니스 분석 질의의 95%가 Claude로 자동화되어 있으며, 집계 기준 약 95%의 정확도를 보인다. 이렇게 종종 판에 박히고 반복적인 일을 Claude에게 맡김으로써, 데이터 과학 팀은 causal modeling, forecasting, machine learning 같은 더 전략적인 일에 집중할 수 있다.

Anthropic의 상위 Claude Code 사용자 수십 명과 만나고, analytics agent를 위한 수많은 design pattern을 본 뒤, Anthropic은 LLM과 함께 일하는 다른 데이터 팀을 위한 몇 가지 best practice를 정리했다. 이 글에서는 Claude가 셀프서비스 비즈니스 insight를 만들어 내는 능력을 극대화하기 위한 팁과 접근법을 공유한다. 구체적으로는 다음을 다룬다.

- 분석 정확도는 code generation 문제가 아니라 context와 verification 문제인 이유
- 대부분의 오류를 일으키는 세 가지 failure mode
- 이 오류들을 다루기 위해 Anthropic이 만든 agentic analytics stack
- 효과를 측정하는 방법
- Anthropic이 대부분의 skill을 만드는 데 사용하는 기본 template, appendix 참고

## 데이터는 소프트웨어가 아니다

LLM의 생성 능력은 양날의 검이다. 복잡한 문제에 대한 창의적 해법을 가능하게 하는 메커니즘은 동시에 잘못된 출력을 hallucinate할 수 있다. analytics agent의 어려움을 온전히 이해하려면 coding agent와 비교하는 것이 유용하다.

코딩은 open-ended solution space이고, 모델의 창의성이 보상받는다. 동시에 documentation과 test가 hallucination을 막는 자연스러운 guardrail을 제공한다. 반면 분석 use case에서는 대개 하나의 올바른 source를 사용해 하나의 올바른 답을 내야 하며, 그 정확성을 결정론적으로 증명할 방법이 없는 경우가 많다.

![데이터 작업에서의 애매성은 코드 생성 능력보다 맥락 매핑과 검증을 더 중요하게 만든다.](https://cdn.prod.website-files.com/68a44d4040f98a4adf2207b6/6a20480bedac32484c00d6b9_4a7645b6.png)

셀프서비스 agentic business analytics에서 복잡성은 주로 데이터의 애매성에 있다. 핵심 문제는 사용자의 질문을 데이터 모델 안의 구체적이고 최신인 entity에 매핑하고, 그것을 올바르게 다루는 방법을 아는 능력이다. 이것을 할 수 있다면, 그 뒤의 execution과 SQL은 사소해진다.

Anthropic은 부정확한 응답의 압도적 다수를 설명하는 이 문제의 세 가지 속성을 식별했다.

1. Concept <> entity ambiguity: 데이터 모델 안에 잠재적으로 수백만 개 field 중 수백 개의 유효한 option이 있을 때, agent가 사용자 질문에 가장 잘 답하는 올바른 field를 고르지 못한다. 예를 들어 active user 수를 측정할 때, 무엇이 “active”라는 행동을 구성하는가? fraud user를 포함하는가? 어떤 lookback window를 사용하는가?

2. Data staleness: 데이터 source, business definition, schema는 계속 바뀐다. asset과 agent knowledge는 낡고, 미묘하게 틀린 답을 내기 시작한다.

3. Retrieval failure: 올바른 정보가 실제로 데이터 모델 안에 있고 제대로 annotate되어 있을 수 있다. 그러나 search space가 너무 넓어서 agent가 그것을 찾지 못한다.

## Anthropic의 agentic analytics stack

Anthropic에서 이 세 가지 오류를 줄이는 주된 방법은 agentic data stack이다. 각 layer는 주로 다음 문제 하나 이상을 공격하기 위해 존재한다.

1. Entity ambiguity: data foundation과 source of truth가 가능한 entity의 공간을 줄여 단일 governed answer가 남도록 한다.

2. Staleness: maintenance와 validation process가 비즈니스 변화에 따라 모든 것이 썩어 가는 것을 막는다.

3. Retrieval failure: skill은 agent가 그 답을 안정적으로 찾고 올바르게 사용하도록 만든다.

이 섹션에서는 각 layer를 어떻게 만들었는지 설명한다.

![Anthropic의 agentic analytics stack은 data foundation, source of truth, skill, validation을 통해 ambiguity, staleness, retrieval failure를 줄인다.](https://cdn.prod.website-files.com/68a44d4040f98a4adf2207b6/6a2049920443016925a3ef72_74528df2.png)

### Data foundations

Analytics agent의 정확도를 보장하는 가장 중요한 측면은 강한 data foundation이다. 여기에는 data warehouse 안의 data model, transform, test, table, 그리고 그것들을 설명하는 metadata가 포함된다. [Dimensional modeling](https://en.wikipedia.org/wiki/Dimensional_modeling), shift-left testing, 중요한 pipeline에 대한 freshness와 completeness check 같은 표준 data engineering과 data quality practice는 여전히 적용된다. 이 글에서는 그것들을 다시 논쟁하지 않는다.

![Dimensional modeling 같은 표준 data engineering practice는 예전과 마찬가지로 중요하다.](https://cdn.prod.website-files.com/68a44d4040f98a4adf2207b6/6a2049920443016925a3ef75_98412372.png)

달라지는 점은 데이터 모델의 최종 사용자가 더 이상 data scientist 같은 데이터 전문가가 아니라는 것이다. 이제 최종 사용자는 underlying infrastructure에 대한 데이터 전문성이나 이해 수준이 다양한 사용자를 대신해 행동하는 agent다. 이 변화는 결과의 underlying correctness를 사용자가 검증해야 하는 형태여서는 안 된다는 과제를 만든다. 최종 사용자는 그것을 알지 못하기 때문이다.

Data foundation layer는 주로 ambiguity를 겨냥한다. 예를 들어 revenue가 40개의 그럴듯한 후보가 아니라 하나의 governed dataset으로 resolve된다면, 문제는 agent가 search를 시작하기 전에 대부분 사라진다. 또한 같은 repo가 canonical model을 정의하므로, 그 모델들이 최신 상태를 유지하도록 강제하는 첫 번째 staleness defense도 이곳에 있다.

Anthropic은 몇 가지 practice가 특히 잘 작동하는 것을 보았다.

- Canonical dataset을 만든다: 가장 흔한 실패는 agent가 concept, 예컨대 “product X의 revenue”를 하나의 올바른 table, column, metric definition으로 매핑하지 못하는 것이다. 보통은 미묘하게 다른 구현을 가진 여러 후보가 있기 때문이다. 해결책은 더 적고, 더 강하게 governed된 logical model이다. 명확한 owner가 있고, consumption-ready이며, discoverable한 작은 canonical single source-of-truth dataset 집합을 curate한 뒤, 거의 중복되는 후보들을 적극적으로 deprecate한다. 비용과 성능을 위해 physical rollup과 cache는 여전히 중요하지만, 그것들은 canonical model 옆에 대안처럼 존재해서는 안 되고 canonical model에서 기계적으로 파생되어야 한다. 목표는 agent가 concept을 search할 때 하나의 governed answer를 찾는 것이다.

- Standard를 강제한다: Anthropic은 canonical model과 metric definition이 tooling, CI, mandate로 강제될 때만 foundation이 유지된다는 점을 확인했다. Tooling은 agent를 구조적으로 먼저 그쪽으로 route한다. 이에 대해서는 아래에서 더 다룬다. CI는 이를 우회하는 변경이 review에서 실패하게 한다. Mandate는 downstream team이 governed layer 위에 build하거나, 그렇지 않은 이유를 설명하게 한다. 강제 없는 governance는 빠르게 여러 후보 문제로 되돌아간다.

- Artifact를 colocate한다: 계속 바뀌는 data model과 business logic에 대한 Anthropic의 주된 방어는 colocation이다. 거의 모든 data code, 즉 modeling, semantic layer, reference doc, canonical dashboard definition이 하나의 repo에 있으며, CI check가 cross-layer integrity를 보호한다. Modeling change가 downstream dashboard를 깨뜨리거나 documented metric을 무효화한다면 CI가 이를 표시하고, 수정은 같은 PR에 포함되어 ship된다. 이 mechanics는 아래 Skill 섹션에서 다시 다룬다.

- Metadata를 first-class product로 다룬다: coding agent가 잘 작동하는 이유 중 하나는 codebase가 legible하기 때문이다. README, type signature, docstring 등이 있다. Warehouse도 마찬가지로 legible할 수 있지만, column과 table description, canonical metric definition, grain documentation, valid value range, lineage, ownership, model tiering이 transformation 자체와 같은 엄격함으로 유지될 때만 그렇다. 새로운 통찰은 아니지만, 좋은 governance는 agent가 올바른 dataset을 고르는 데 필요한 핵심 context를 제공한다.

### Sources of truth

Data foundation이 data warehouse 자체라면, source of truth는 agent가 그것을 탐색하기 위해 참조하는 표면이다. 이 layer는 concept <> entity ambiguity를 줄이고, stakeholder 질문 속 “weekly active users”를 데이터 모델 안의 특정 governed entity로 바꾼다. 대략 신뢰도 내림차순으로 보면 다음과 같다.

- Semantic layer: compile된 metric과 dimension definition이다. 질문이 정의된 metric에 clean하게 매핑되면 agent는 function을 호출하고 하나의 숫자를 얻는다. 회사의 다른 모든 surface가 생산하는 것과 같은 숫자다. Anthropic의 agent는 skill instruction에 의해 semantic layer를 먼저 활용하도록 구조적으로 요구된다. Appendix를 보라. Anthropic이 시도했지만 작동하지 않았던 아이디어 하나는 LLM이 raw table과 query log에서 metric definition을 자동 생성하게 해 semantic layer를 bootstrap하는 것이었다. 결과는 그럴듯해 보였지만, Anthropic이 제거하려던 바로 그 ambiguity를 encoding한 definition이었다. Eval에서는 더 작고 사람이 curate한 layer보다 net-negative였다. 따라서 Anthropic은 documentation은 Claude로 생성하되, definition은 사람이 소유하도록 권장한다.

- Lineage와 transformation graph: semantic layer가 질문을 cover하지 않을 때, lineage와 table ranking, 즉 reference 수에 기반한 ranking은 agent가 어떤 upstream model이 concept에 공급되는지, 무엇이 deprecated되었는지, 무엇이 grain을 공유하는지 추론하게 한다. 이는 “metric을 모른다”를 “어떤 governed model에서 aggregate해야 하는지 안다”로 바꾼다. 또한 아래 online validation에서 surface하는 freshness와 provenance signal의 backbone이기도 하다.

- Query corpus: dashboard, notebook, 과거 analysis의 historical SQL이다. 직관적으로는 매우 가치 있어야 한다. 이미 올바르게 답한 모든 질문의 기록이기 때문이다. 실제로는 agent에게 과거 query 수천 개에 대한 raw retrieval access를 주어도 정확도는 1%p 미만으로만 움직였다. 이 ablation은 아래 later section에서 설명한다. 비정형 retrieval은 새 질문을 올바른 precedent에 매핑하지 못했다. 작동하는 것은 그 corpus를 structured per-domain reference doc과 skill에 설명된 reusable analysis pattern으로 distill하는 것이다. Query history를 agent가 직접 읽는 source of truth가 아니라 curation을 위한 raw material로 다루어야 한다.

- Business context: 대부분의 팀이 건너뛰는 layer이며, Anthropic도 가장 오래 과소평가한 layer다. 비즈니스를 이해하지 못하는 agent는 사용자가 물은 것에는 답하지만, 사용자가 의도한 것에는 답하지 못한다. “the Q2 launch”가 특정 product를 가리킨다는 사실, 두 팀이 같은 term을 다르게 정의한다는 사실, 어떤 질문이 목요일 board meeting 때문에 나온 것이라는 사실을 알지 못한다. Anthropic은 indexed docs, roadmap, decision log, organizational structure로 구성된 company knowledge graph를 주입해 agent가 ambient reference를 resolve하고 더 나은 clarification question을 묻게 한다.

이 네 가지 모두에서 공통 failure pattern은 data foundation layer에서 본 것과 같다. poor or stale documentation이다. Claude는 이 간극을 메우는 데 매우 유용하다. Column description을 draft하고, query pattern에서 metric doc을 제안하며, CI에서 undocumented model을 flag할 수 있다. 하지만 curation과 ownership은 사람이 관리한다.

다음 두 섹션에서는 그 ownership이 실제로 일어날 만큼 충분히 저렴해지게 하는 방법을 다룬다.

### Skills

Source of truth가 agent의 declarative knowledge, 즉 metric이 무엇을 의미하는지라면, skill은 procedural knowledge다. 어떤 source를 어떤 순서로 참조할지, ambiguous data를 어떻게 탐색할지, 완성된 analysis가 어떤 모습이어야 하는지를 담는다.

Claude Code에서 [skill](https://code.claude.com/docs/en/skills)은 agent가 필요할 때 읽는 markdown folder다. Anthropic에서 개발한 skill은 큰 부가가치를 만든다. Skill이 없을 때 Claude가 analytics question에 정확하게 답하는 능력은 eval에서 21%를 넘지 못했다. Skill을 추가하면 이 수치가 집계 기준 95%를 꾸준히 넘고, 특정 domain에서는 정기적으로 99% 수준에 도달한다. Anthropic이 대부분의 skill을 만들 때 사용하는 skeleton은 appendix를 보라.

몇 가지 best practice는 다음과 같다.

Create pairwise skills: knowledge skill은 추가 domain detail을 on demand로 load할 수 있게 하는 얇은 top-level router 역할을 한다. 이 skill은 “먼저 semantic layer를 시도하라. coverage가 없으면, 이 domain의 관련 table, column, join, gotcha를 설명하는 약 30개의 reference file이 있다”고 말한다. 이 router는 사실상 retrieval failure에 대한 Anthropic의 답이다. Agent가 백만 field warehouse를 search하게 두는 대신, query가 작성되기도 전에 공간을 몇십 개 curated file로 좁힌다. unbook skill은 senior analyst가 따를 process를 encoding한다. 질문을 clarify하고, knowledge skill을 통해 source를 찾고, query를 실행한 뒤, adversarial review sub-agent를 통해 결과를 반복 검토한다. 또한 retention curve, rate decomposition, funnel analysis 같은 12개 정도의 reusable analysis pattern을 bundle해 흔한 요청이 매번 새로 발명되지 않게 한다.

Create proper reference docs: reference doc은 LLM retrieval을 위해 작성되어야 한다. Anthropic의 reference doc은 table, 즉 grain, scope, exclusion을 설명하고, gotcha의 mechanics, 예컨대 “known free-email domain은 제외하되 anthropic.com 같은 custom domain은 유지하라”를 설명하며, “질문이 experiment lift에 관한 것이면... raw event count에는 사용하지 말라” 같은 explicit routing trigger를 담는다. 반대로 금세 낡는 prescriptive recipe는 피한다. 아래는 Anthropic이 reference doc을 만들 때 사용하는 skeleton이다.

```text
# [Domain] Tables

## Quick Reference
### Business Context — [what this domain means in plain words]
### Entity Grain — [what one row represents]
### Standard Hygiene Filter — [the filter every query in this domain applies]

## Dimensions
- [How the key dimensions are encoded, and how the same concept is named
  differently across tables]

## Key Tables
### [table_name]
- Grain: [...] · Scope/exclusions: [...]
- Usage: [when to use it, when NOT to, join keys, required filters]
[... one short section per governed table ...]

## Gotchas
- [The wrong-answer modes a senior analyst would warn you about]

## Best Practices / Common Query Patterns
- [Default choices, standard cuts, worked patterns where the exact query
  form is the hard part]

## Cross-References
- [Neighboring domain docs that own adjacent questions]
```

Treat skill maintenance as a first-class citizen: skill doc은 매일 바뀌는 data model을 설명하므로, 적극적으로 유지하지 않으면 몇 주 안에 틀린다. Anthropic은 이것을 engineering problem으로 다루기 전까지 offline accuracy가 launch 시점 약 95%에서 한 달 뒤 약 65%로 drift하는 것을 보았다. 이는 skill markdown file을 transformation model과 같은 repo에 colocate한다는 뜻이었다. Model을 바꾸는 PR이 그것을 설명하는 doc도 업데이트하는 같은 PR이 되도록 했다. Code-review hook은 reporting-model change가 skill file을 건드리지 않으면 flag한다. 이제 Anthropic data-model PR의 약 90%는 같은 diff 안에 skill change를 포함한다. 또한 모델이 개선되고 이전 failure mode가 더 이상 적용되지 않으면 skill scaffolding을 정기적으로 prune한다.

Create a consistent and seamless experience across all surfaces: 같은 skill은 Slack, IDE, dashboard tool, standalone agent session에서 같은 질문에 같은 답을 제공해야 한다. Anthropic은 하나의 canonical source, 즉 data repo를 보장하고 skill change가 자동 sync되도록 하여 이를 수행했다. Merge되면 skill은 IDE 사용자를 위한 plugin marketplace, single file을 읽는 hosted app용 cloud-storage blob, MCP를 통해 직접 제공되는 resource로 sync된다. 또한 hardcoded repo path와 surface-specific namespace를 피함으로써 처음부터 portability를 고려했다.

### Validation

마지막으로 validation은 세 failure mode 중 무엇이 아직 새고 있는지를 알아내는 방법이다.

#### Offline evaluations

흔히 보는 pattern은 데이터 팀이 정교한 analytic environment를 구축하면서, analytics agent의 정확도를 이해하는 process는 전혀 두지 않는 것이다.

이 간극을 다루는 한 방법은 offline eval이다. Offline eval은 단순한 question / answer pair다. 이것은 ML model의 offline testing과 비슷하게 생각할 수 있다. Online agent의 performance를 직접 알려 주지는 않지만, critical gap이 있는지에 대해서는 좋은 감각을 준다.

Anthropic은 두 종류의 offline eval을 배포한다. Dashboard-based eval은 Claude가 자동 생성한 뒤 사람이 validate하며, 가장 흔한 stakeholder question을 cover한다. Long tail eval은 Claude에게 business context, roadmap, table doc을 제공하고 나머지 domain 전반에서 그럴듯한 질문을 생성하게 한다. 또한 stakeholder가 thread에서 agent를 수정할 때마다 그 correction을 candidate eval로 계속 harvest한다.

다른 best practice는 다음과 같다.

- Ground truth가 drift하지 않게 anchor한다: live data에 대해 작성한 eval은 underlying number가 움직이는 순간 낡는다. 모든 eval을 snapshot date에 pin하거나, stable fact table에 대해 작성하거나, grader가 agent의 number가 아니라 query를 judge하게 한다. Suite를 CI에 연결해 dependency를 건드리는 PR이 affected eval을 다시 실행하게 한다.

- Result를 test log가 아니라 telemetry처럼 저장한다: 모든 run은 skill version, git SHA, model ID, assertion별 pass/fail, token count, wall-clock을 가진 warehouse table에 들어간다. “그 change가 도움이 되었나?”는 query가 되고, 단일 CI run이 잡지 못하는 느린 regression을 포착할 time-series를 얻는다.

- Launch를 domain별로 gate한다: domain owner는 자신의 eval set slice가 어떤 threshold, Anthropic 초기에는 약 90%, 를 넘기 전에는 stakeholder에게 agent를 announce할 수 없다. 이것은 사용자가 failure를 보기 전에 reference-doc fix를 강제한다.

- 적절한 eval 수를 만든다: 필요한 eval 수는 business area의 복잡성과 underlying data model의 복잡성에 따라 달라진다. Offline accuracy가 online accuracy를 얼마나 잘 예측하는지 추적해 calibrate한다. Anthropic은 topic, 예컨대 “growth” 하나당 몇십 개를 넘어서면 diminishing return이 있고, 그 ceiling은 새 model generation마다 낮아진다는 점을 확인했다.

- Offline eval accuracy는 약 100%여야 한다. 올바른 답은 모두 semantic layer, 그런 layer가 있다면, 를 hit해야 한다. 다시 말하지만 이 수준의 accuracy가 시스템이 틀린 답을 만들지 않을 것이라는 뜻은 아니다. 적절한 eval coverage가 있다는 가정하에 명백한 gap이 없다는 뜻이다.

#### Ablation techniques

Skill에 대한 모든 구조적 결정, 예컨대 어떤 source를 expose할지, sub-agent가 latency를 감수할 가치가 있는지, 두 skill을 하나로 merge할지 여부는 offline eval set을 고정해 두고 내린다.

Anthropic은 정확히 하나의 component만 바꾸고 pass rate를 비교한다. 각 run은 한 시간밖에 걸리지 않으며 많은 논쟁을 대체한다. Methodology가 어떤 단일 결과보다 중요하다.

- Null result를 고려해 설계한다: Anthropic의 가장 유용한 ablation은 negative result였다. Agent에게 dashboard, transformation, analyst-notebook SQL 전체, 즉 수천 개 file에 direct grep access를 주었다. 그런 다음 transcript에서 agent가 매 answer 전에 실제로 그것들을 읽었다는 점을 검증했다. 정확도는 어느 방향으로도 1%p 미만만 움직였다. 그 다음 obvious confound를 확인했다. 틀린 질문에 대한 답이 실제로 corpus 안에 있었는가? 약 80%의 경우 그렇다. “답이 존재한다”는 것이 “이제 맞춘다”를 예측했는가? 아니다. flip rate는 flat했다. 정보는 있었고, agent는 그것을 보았지만, 여전히 사용하지 않았다. 이 단일 실험은 bottleneck이 prior work에 대한 access가 아니라 structure, 즉 질문을 올바른 entity에 매핑하는 것임을 알려 주었다. 이 insight는 수개월의 roadmap을 재지정했다.

- PR granularity로 ablate한다: 의미 있는 모든 skill edit은 관련 eval slice에서 before / after run을 거치고, PR description에 delta를 적는다. 이는 “doc을 개선했다”는 말을 정직하게 만들며, 선의의 추가가 오히려 상황을 악화시키는 놀라울 정도로 흔한 사례를 잡는다.

- 작동하지 않은 것의 짧은 목록을 유지한다: Anthropic의 예 두 가지는, 어느 지점 이후 추가 doc refinement round를 쌓는 것, 세 번 연속 net-negative iteration을 겪었고 doc은 더 길어졌지 더 좋아지지 않았다, 그리고 latency를 줄이려고 adversarial reviewer를 더 싼 model로 바꾸는 것이다. 후자는 정확도 이득 대부분을 잃었고 실제 speedup도 없었다. Negative result는 기록 비용이 낮고, 다음 사람이 같은 실험을 반복하는 것을 막는다.

#### Online validation

마지막 단계는 실제 online system performance를 가능한 한 정확하게 만드는 것이다. Anthropic이 수행하는 일부 단계는 다음과 같다.

- Adversarial review: 잠재적 final answer의 모든 underlying assumption에 공격적으로 도전하는 Claude skill을 쓰면 eval set에서 정확도가 6% 증가했다. 하지만 token은 32% 더 들고 latency는 72% 높아졌다.

- Provenance footer: 모든 response는 source tier, 즉 semantic layer › curated reference › raw table, underlying data의 freshness, model owner를 담은 footer를 가진다. 이것이 답을 더 정확하게 만들지는 않지만, 소비자가 response를 얼마나 신뢰할 수 있는지 판단하는 데 도움이 된다. “raw table, freshness unknown” footer는 상위에 전달하기 전에 검증하라는 신호이며, silent failure에 대해 Anthropic이 가진 몇 안 되는 mitigation 중 하나다.

- Data quality checks: agent가 올바른 field를 적절한 방식으로 쓰고 있어도, data 자체가 틀릴 수 있다. 참조된 field가 최신이고, complete하며, anomaly가 없는지 확인하는 기본 data quality check를 추가하는 것은 일반적으로 좋은 hygiene이다.

- Passive monitoring: Anthropic이 지속적으로 추적하는 production signal 두 가지는 agent query 중 semantic layer를 통해 resolve되는 비율과, response가 correction language, 예컨대 “that’s the wrong table”, “you’re missing the fraud filter”를 사용하는 비율이다. 둘 다 offline pass rate와 함께 매주 review되는 dashboard로 들어간다.

- Active correction harvesting: 이것이 loop를 닫는 부분이다. Scheduled agent가 몇 시간마다 stakeholder channel에서 비슷한 correction language를 scan하고, 관련 reference doc에 대한 한 줄 fix를 draft하며, domain owner에게 tag된 PR을 연다. Fix path는 의도적으로 지루하게 설계되어 있다. markdown file을 edit하고, merge하고, 모든 곳에 auto-sync한다. 그래야 domain owner가 이 작업에 너무 많은 시간을 쓰지 않는다. 같은 correction은 offline eval set으로도 다시 들어간다.

이 모든 것이 완전히 잡아내지 못하는 failure mode는 silent failure다. 답은 틀렸지만 그럴듯해 보이고, 아무 이의 없이 사용된다. Anthropic의 mitigation은 provenance footer, leadership-bound output에 대한 명시적 human sign-off, 그리고 각 domain의 top KPI를 blessed dashboard와 매일 sanity-check하는 standing eval이다. 하지만 아직 robust solution은 없다.

## 시작하기

처음부터 시작한다면, 몇 개의 canonical dataset, 몇십 개의 offline eval, 얇은 knowledge skill만으로도 대부분의 upside를 얻을 수 있다. 이 글의 나머지는 그것들이 만들어진 뒤 Anthropic이 추가한 것이다.

Anthropic은 많은 best practice를 공유했지만, 그 모두가 모든 데이터 팀에 적절하지는 않다. 다음 질문을 통해 접근에 영향을 줄 몇 가지 원칙에 대해 조직과 alignment를 맞추어야 한다.

- 오늘의 올바른 답과 미래의 올바른 답 중 무엇이 얼마나 중요한가? AI model은 빠르게 발전하고 있다. Anthropic은 회사들이 현재 model shortfall을 보완하려고 상당한 infrastructure를 만들지만, model이 개선되면 그것이 무의미해지는 경우를 자주 본다. Model이 어디에서 부족한지 알고, 그 gap을 model improvement가 채우기를 기다리는 것은 overhead가 훨씬 적다. 다만 회사의 risk tolerance에 맞지 않을 수 있다.

- 시간이 지나면서 비즈니스 복잡성이 어떻게 변할 것으로 예상하는가? 예를 들어 많은 data를 만들지 않거나, output consumer가 몇 명뿐이거나, data model이 단순하게 유지될 가능성이 높다면, 논의한 process 중 일부는 과할 수 있다.

- Output의 intended audience는 얼마나 기술적인가? 다르게 말하면, underlying data model을 모르더라도 답이 틀렸을 때 알아차릴 수 있는 data scientist를 위해 이 analytics system을 만든다면, underlying data model에 익숙하지 않은 audience를 위한 경우보다 error에 더 관대할 수 있다.

- 정확도 향상을 위해 얼마를 지불할 의향이 있는가? Anthropic은 adversarial validation 같은 process가 정확도를 상당히 높일 수 있지만, 대개 더 높은 cost와 latency를 수반한다는 점을 확인했다.

- Access control과 internal data privacy에 대해 어느 정도 편안한가? Agent는 context가 많을수록 성능이 크게 좋아지는 경우가 많다. 그러나 broad data access는 대부분 회사의 governance posture와 충돌한다. 이것은 하나의 agent를 만들지, scope가 나뉜 여러 agent를 만들지를 결정한다.

어떤 경로를 택하든, Anthropic의 가장 큰 이득은 세 failure mode 각각을 다룬 데서 나왔다. Ambiguity를 하나의 governed answer로 collapse하고, 그 answer를 쉽게 discoverable하게 만들며, 둘 중 하나가 stale해졌을 때 flag하는 것이다.

이 글은 Data Science and Data Engineering 팀의 Chen Chang, Clement Peng, Justin Leder, Johanne Jiao, Josh Cherry가 작성했다. 저자들은 Michael Segner의 기여에 감사한다.

## Appendix

#### Skill File Skeleton

아래는 Anthropic의 main warehouse skill skeleton이다. 실제 file의 구조를 보여 주되, 내부 세부사항은 `[bracketed placeholders]`로 대체했다. 그대로 복사하라는 뜻이 아니라, 어떤 section들을 적어 둘 가치가 있었는지 보여 주기 위한 것이다.

```yaml
---
name: [warehouse-skill]
version: [x.y.z]
description: "IF the user asks to query [the company]'s data warehouse for any
  [list of business domains] question — THEN invoke this skill. DO NOT invoke
  for [adjacent engineering tasks] or questions with no data-warehouse component."
---
```

```markdown
# [Warehouse] Skill Instructions

## Description
The single source of truth for safe and effective [warehouse] querying.
Referenced by other skills [listed] for query execution guidance.

Act as a Data Analyst, providing strategic insights and data-driven
recommendations but seek guidance along the way.

Out-of-scope decisions: [product areas, etc.] → surface data only,
state "decision is [owning team]'s call", do NOT take a position or author
code fixes.

## Executing queries
Priority:
1. [Managed connection] (if available): [query tool] / [schema tool]
2. [CLI fallback] (if installed): [default project, fallback project]
3. Neither — ask the user to authenticate, then stop

---

# Semantic Layer (REQUIRED first step)

The governed semantic layer is the mandatory default path for every data
question — same numbers as [the BI tool], joins/grain/filters baked in. Raw SQL
via the reference docs below is the fallback, used only after the
semantic-layer path is shown not to cover the ask.

## Required workflow
1. Load — [how to load the semantic layer in each runtime, with fallbacks]
2. Discover — search measures/dimensions by keyword; always check
   segments (the named canonical population filters — hand-rolled WHERE
   clauses for these are the dominant wrong-answer mode)
3. Compile + run — build the spec → compile to SQL → execute
4. Fallback — only if discovery finds no relevant metric or compile fails
   → raw SQL via `references/*.md` (PART 3 below)

> Don't bail early. Do NOT fall back to raw SQL on these grounds:
> - "[custom date filtering / cohorts]" → [covered by time-dimension specs]
> - "[needs a join]" → [the metric layer already encapsulates its joins]
> - [3–4 more pre-rebutted excuses agents use to skip the semantic layer]

### Date windows & timezone — decide before you query
- As-of date vs trailing-N days: [convention for each]
- "Last week/month" → the last complete calendar week/month, not trailing-7/30
- Timezone default: [TZ]; [exception for certain reporting rollups]
- Freshness lag: [some] tables settle late — anchor on MAX(date), not "yesterday"

---

# PART 1: MUST KNOW (Read First for Every Request)

## 🚀 Quick Start Workflow
1. Check for red flags first: [restricted/PII requests, gated domains,
   high-stakes asks that need extra validation]
2. Out of scope — escalate, don't guess: [access requests, pipeline
   troubleshooting, stale dashboards, root-cause assertions, product/pricing
   recommendations] → redirect to [the owning team], don't answer
3. Clarify the request: time period, segment, the business decision it informs
4. Check for existing dashboards: [per-domain dashboard catalogs]
5. Identify the data source: [navigation map below; prefer governed/aggregated tables]
6. Execute the analysis: [required filters + adversarial review]
7. Deliver insights: show methodology, differentiate observations from interpretations

## 🏢 Business Context

### Entity Disambiguation (MUST CLARIFY)
- "[Term A]" can mean: [entity 1] or [entity 2] — always clarify which
- "[Term B]" can mean: [entity 1] → [entity 2] → [entity 3] (one-to-many chain)
- "Users": [which identifier gives accurate counts, and which ones inflate them]

### Business Terminology
- [Current product names vs deprecated aliases that still appear as frozen
  values in the data layer — write with the new names, filter with the old]
- [Key internal acronyms]
- [Headline metric] calculations: [monthly / default window / leading indicator]
- Unfamiliar terms — search [internal docs], don't guess

### Data Integrity Requirements ⚠️
- NEVER: make up data/columns; make speculative assertions beyond what data shows
- ALWAYS: use safe division; differentiate observations ("data shows X")
  from interpretations ("this suggests Y"); flag limitations

---

# PART 2: HOW TO DO (Follow During Execution)

## 🔧 Technical Execution Guide
- [Managed-connection tools and CLI invocation details]
- PII protection: for restricted data, return the SQL for the user to run
  themselves — do not return results

## 📊 Analysis Best Practices Guide
1. Clarify the ask before querying
2. Show your work (filters, inclusions/exclusions, freshness)
3. Clarify denominators
4. Consider sample bias
5. Connect to business impact
6. Adversarial SQL review (MANDATORY) — spawn the [sql-reviewer] sub-agent
   for every query before the final answer; blocking findings must be fixed
   and re-reviewed; do not self-certify
7. Report with provenance — every answer ends with a footer:
   > Source: [semantic layer | governed table | raw exploration] ·
   > Confidence: [tier] · Reviewed: [reviewer ✓, round N] ·
   > Freshness: [max date in the data] · Owner: [owning team]

---

# PART 3: DATA REFERENCES & RESOURCES

## 📚 Knowledge Base Navigation
### [Domain A] → `references/[domain_a].md`
- Use for: [kinds of questions]
- Key tables: [...]
- Dashboards: `references/[domain_a]_dashboards.json`

### [Domain B] → `references/[domain_b].md`
- Use for: [...]

[... one entry per business domain — a few dozen in total ...]

## ⚠️ Troubleshooting Guide

### When Information Is Missing
- [missing tables / access denied / outdated docs / unknown enum values → what to do]

### Field Naming Gotchas
- Use `[field_x_v2]` NOT `[field_x]`
- [Two similarly-named tables report the same metric at different grains — which to use]
- [Which of two plausible sources is canonical for the headline metric]
- [… a dozen more hard-won one-liners …]
```
