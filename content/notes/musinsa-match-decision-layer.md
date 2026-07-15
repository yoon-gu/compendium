---
title: "MATCH란 무엇인가: 팀무신사의 의사결정 레이어"
date: 2026-07-14
draft: false
source_url: "https://techblog.musinsa.com/match%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80-5776910908af"
author: "김경민, 무신사 Core Product Platform PM"
tags: ["AI", "Personalization", "Recommendation", "MarTech", "Musinsa"]
summary: "무신사의 MATCH는 고객 데이터를 단순히 모으는 CDP가 아니라, 오디언스 선정·캠페인 실행·피드백 학습을 연결하는 비즈니스 의사결정 레이어다. 이 글은 MATCH가 rule-based 타겟팅에서 소재 반응 예측과 feedback loop 기반 개인화로 전환한 배경과 조직적 의미를 정리한다."
---

> **원문:** [MATCH란 무엇인가](https://techblog.musinsa.com/match%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80-5776910908af) — 김경민, 무신사 Core Product Platform PM, 2026-07-14
>
> 아래 글은 원문의 구조와 서술을 따라가며, Compendium 독자를 위해 기술·제품 관점의 맥락을 조금 더 또렷하게 정리한 한국어 note다.

## 핵심 요약

무신사의 MATCH(Musinsa Audience Targeting & Customer Hub)는 고객 행동 데이터를 쌓아두는 저장소가 아니라, 데이터를 실제 매출과 고객 경험으로 전환하기 위한 의사결정 레이어다. 핵심 문제의식은 “데이터를 가지고 어떻게 매출을 만들어낼 것인가”에 있다. 데이터가 충분히 모여 있고 파이프라인도 안정적으로 구축되어 있더라도, 적절한 시점에 적절한 고객 접점으로 연결되지 않으면 비즈니스 가치를 만들 수 없기 때문이다.

MATCH는 기존의 rule-based audience 추출을 넘어, 캠페인 소재와 유저 행동 데이터를 함께 학습해 “이 소재에 가장 잘 반응할 유저”를 모델이 직접 찾아내는 방향으로 전환했다. 앱 push 채널에서 시작해 타겟팅과 detargeting, 발송 실행, 반응 signal 학습을 하나의 feedback loop로 묶었고, 그 결과 마케터는 반복적인 타겟 추출 대신 전략과 기획에 더 집중할 수 있게 되었다.

## 데이터를 쌓기만 해서는 매출로 연결되지 않는다

데이터는 축적 자체만으로 자산이 되지 않는다. 고객 행동 데이터가 많고, 로그 체계와 data pipeline이 안정적으로 갖춰져 있어도, 그 데이터가 적절한 timing에 고객에게 닿지 못하면 한 건의 매출도 만들 수 없다. 따라서 데이터는 축적과 분석을 넘어 실행(engagement)으로 이어져야 한다.

문제는 수많은 변수와 접점을 사람이 모두 수기로 판단하기 어렵다는 데 있다. 데이터가 비즈니스 자산이 되려면, 많은 signal 가운데 최적의 action을 고르는 의사결정 엔진이 필요하다. MATCH는 바로 이 지점에서 출발한다. 단순한 정보 hub가 아니라, Musinsa와 29CM의 고객 데이터를 비즈니스 의사결정으로 연결하는 레이어를 만들기 위한 시도다.

![MATCH 개념 이미지](https://miro.medium.com/v2/resize:fit:1000/1*FOwDp5hrOAqF8deQitZgNw.jpeg)

## 최적화의 역설: 각자의 최선이 전체의 최선은 아니다

MATCH의 출발점은 처음부터 거대한 AI personalization system이 아니었다. 처음의 질문은 비교적 단순했다. “CDP(Customer Data Platform)가 필요한가, 필요하다면 어떤 형태여야 하는가?”

초기에는 여러 곳에 흩어진 고객 데이터를 한곳에 모으고, 이를 바로 활용할 수 있게 serving하는 것만으로 많은 문제가 풀릴 것이라고 기대했다. 프로젝트가 marketing need에서 시작되었기 때문에, CRM(Customer Relationship Management) marketing workflow와 발송 도구를 따라가며 실제 업무 흐름을 파악했다.

하지만 현장에서 드러난 본질적 질문은 달랐다.

> “그래서 이 데이터를 가지고 어떻게 매출을 만들어낼 것인가?”

무신사와 29CM의 규모가 커질수록 이 질문은 더 중요해졌다. 온라인과 오프라인, 무신사와 29CM, 플랫폼 안의 메시지·배너·상품·혜택까지 고객 접점이 늘어나면서, 단순히 데이터를 보유하는 것보다 수많은 맥락과 접점을 어떻게 최적화해 business impact를 극대화할지가 더 본질적인 문제가 되었다.

각 조직은 이미 자기 영역에서 최적화를 잘 수행하고 있었다. CRM은 CRM대로, banner는 banner대로, recommendation system은 recommendation system대로 지표를 개선하기 위해 가설을 세우고 실험하며 모델을 다듬었다. 그러나 개별 최적화가 정교해질수록 전체 고객 경험에는 두 가지 gap이 남았다.

- 일관성의 gap: 개별 campaign이 독립적으로 잘 설계되어도, 한 사용자가 특정 시점에 강한 할인 메시지를 받은 직후 곧바로 감도 높은 brand content를 제안받는 식의 단절이 발생할 수 있다. 사용자에게는 맥락 있는 흐름이 아니라 파편화된 노출의 연속으로 느껴진다.
- 학습의 gap: marketing experiment에서 얻은 insight가 recommendation system으로 흐르지 않고, 반대 방향도 마찬가지다. 동일한 사용자를 다루면서도 각 system의 learning data가 서로 다른 silo 안에 갇히는 구조다.

따라서 domain을 가로질러 decision과 feedback을 연결하는 별도 layer가 필요했다. 예를 들어 한 유저가 ‘나이키 기획전’과 ‘신규 브랜드 소개’ campaign target에 동시에 포함될 때 어느 쪽에 배정해야 전환율을 극대화할 수 있는지, 상품 상세 조회·찜하기·구매 이력 중 어떤 signal에 어느 정도 weight를 둘지 같은 질문이다.

기존에는 데이터 속성은 있었지만 이를 고르는 판단이 부족했고, signal은 많았지만 이를 결합할 기준이 부족했다. 기존 CDP가 해결하지 못한 본질은 데이터 수집의 부재가 아니라 결정의 영역이었다.

## 그래서 MATCH는 “결정”을 다룬다

MATCH는 이 결정을 system으로 풀기 위해 설계되었다. 이름 그대로 Musinsa Audience Targeting and Customer Hub이며, 단순히 데이터를 모아두는 창고가 아니라 적합한 audience를 발굴해 각 고객 접점에서 최적의 business decision으로 연결하는 layer를 지향한다.

![MATCH 구축 과정 이미지](https://miro.medium.com/v2/resize:fit:700/1*gIThbH-nXxob-imgaOul9g.png)

### Audience: 결정의 최소 단위이자 핵심

개인화된 message, 매력적인 creative, 완벽한 exposure timing 등 marketing 성과를 높이는 요소는 많다. 하지만 그 모든 결정을 적용할 최종 대상인 audience가 모호하다면 어떤 노력도 성과로 이어지기 어렵다. 정교한 AI model과 강력한 serving infra가 있어도 target이 부정확하면 기술은 힘을 잃는다. MATCH가 audience를 정교하게 다듬는 작업에 먼저 집중한 이유가 여기에 있다.

기존 audience는 대체로 rule의 집합이었다. “최근 30일 내 나이키 상품을 조회한 유저”, “지난 시즌 세일 기간에 구매한 유저”처럼 marketer가 조건을 직접 정의하고 유저를 추출하는 구조다. 이 방식은 직관적이고 설명하기 쉽지만, 조건 조합에 따라 결과가 크게 달라진다. 어떤 signal이 실제 purchase conversion과 연결될지 사전에 rule만으로 정의하기는 어렵다.

Rule-based 방식에서는 특정 user가 같은 시간대에 여러 creative audience에 동시에 매칭되기도 한다. 이 경우 어떤 creative에 배정해야 marketing effect가 커질지 판단하기 어렵고, 기존에는 marketer의 경험과 직관에 의존해야 했다.

### Rule 중심에서 소재 반응 여부 중심으로

MATCH는 audience 정의를 바꿨다. Personalization팀은 유저의 과거 행동 데이터와 campaign creative의 meta information, 예를 들어 brand, category, price range 등을 함께 학습하는 model을 설계했다.

이제 targeting은 “나이키를 6회 조회한 유저”를 찾는 방식에서 “이 나이키 기획전 creative에 가장 잘 반응할 유저”를 AI가 직접 발굴하는 방식으로 바뀐다. Creative 정보가 입력되면 model이 각 user와 creative 사이의 fit을 산출하고, response probability가 높은 user를 추려낸다. Marketer는 복잡한 rule을 일일이 정의하거나 creative conflict를 직접 해결하는 부담을 줄일 수 있다.

이 접근을 통해 MATCH는 단순한 audience classification을 넘어, 각 service domain의 특성에 맞춘 실제 personalization decision을 만들어낸다.

- CRM 등 marketing channel에서는 creative 정보를 기반으로 system이 가장 적합한 수신자를 선별해 자동 발송한다.
- Web/App 내 domain service에서는 user가 어떤 audience group에 속하는지 real-time으로 판별하고, domain 담당자가 data 기반으로 growth goal을 최적화할 수 있도록 serving layer 역할을 한다.

Personalization팀은 data collection, analysis, modeling, serving, user experience까지 end-to-end로 책임진다. 데이터 학습, modeling, serving이 하나의 cycle로 연결되어 있다는 점이 MATCH의 구조적 강점이다.

## 성과를 넘어 조직의 의사결정 방식을 재정의한다

MATCH의 가능성을 검증한 첫 실전 무대는 활용도가 높고 복잡도도 큰 app push channel이었다. 당시 marketing 현장은 하루에도 수십 건씩 들어오는 campaign 요청으로 과부하 상태였다. Target 중복과 creative conflict라는 복잡한 문제를 marketer가 매번 수동으로 막아내고 있었기 때문이다.

하지만 더 중요한 문제는 단순한 운영 비효율이 아니었다. Campaign을 실행할 때마다 click과 purchase data가 쌓이지만, 그 결과가 system에 누적되지 않는 구조적 한계가 있었다. 담당자가 바뀌면 marketing asset은 reset되고, 수백 번의 campaign을 집행해도 다음 campaign의 targeting accuracy는 크게 개선되지 않았다. 실행은 쌓이지만 system intelligence는 진화하지 않는 구조였던 셈이다.

### Audience optimization과 feedback loop

MATCH는 처음부터 거창한 personalization을 내세우기보다, data가 스스로 순환하는 feedback loop의 최소 기반을 첫 milestone으로 삼았다. Marketer가 campaign creative와 기본 조건을 등록하면 AI/ML model이 creative에 맞는 targeting과 detargeting을 처리하고, 발송 후 얻은 user response signal로 다음 campaign의 정확도를 높이는 선순환 구조를 설계했다.

이 과정에서 중요한 질문은 사람과 system의 decision responsibility를 어디에 둘 것인가였다. MATCH는 “creative 기획과 최종 검토는 marketer가, target 선별과 발송 실행은 system이 담당한다”는 기준을 세웠다. 그리고 현업 조직이 수년간 쌓아온 판단 기준을 system이 이해할 수 있는 언어로 번역하는 데 많은 노력을 들였다.

그 결과, 기존에 외부 solution에 의존해 수동으로 운영하던 promotion push 전반을 MATCH pipeline으로 전환했다. 현재 상당한 규모의 app push message가 MATCH의 personalization ML model 위에서 자동 최적화되어 발송되고 있으며, targeting이 정교해지면서 click-through rate와 기여 거래액 모두 꾸준히 개선되는 성과를 얻고 있다.

그러나 MATCH의 가장 큰 의미는 숫자 개선 자체보다 조직의 일하는 방식 변화에 있다. 반복적인 target extraction을 system에 맡기면서 marketer는 더 큰 business 그림을 그리는 전략 수립과 기획에 집중할 수 있게 되었다. MATCH는 tech와 business의 접점에서 구성원에게는 역량을 펼칠 무대를, 고객에게는 매끄러운 shopping experience를 제공하는 방향으로 commerce operation의 패러다임을 바꾸고 있다.

## 다음 과제와 MATCH의 정체성

MATCH는 이제 본격적인 궤도에 오른 system이고, 아직 풀어야 할 질문이 많다. 데이터가 충분한 대형 brand는 AI model이 비교적 잘 다룰 수 있다. 그러나 전략적으로 키워야 할 신생 category나 신생 brand는 signal이 부족하다. 눈앞의 conversion rate만 기계적으로 따르는 최적화는 강자만 더 강해지는 winner-takes-all 구조를 만들 수 있다. Business input과 optimal output 사이에서 철학적 균형점을 설계하는 것이 model algorithm을 넘어선 첫 번째 과제다.

![Inbox Optimizer와 CRM 최적화 방향성](https://miro.medium.com/v2/resize:fit:700/1*5bTPH8auPUbHnktKw2WRSA.png)

하루에도 수십 개의 campaign이 쏟아지는 상황에서 user의 message fatigue를 제어하는 것도 핵심 과제다. 해법은 campaign 수를 억지로 줄이는 것이 아니라, 많은 campaign 가운데 각 user에게 가장 적합한 message combination을 system이 정교하게 골라내는 Inbox Optimizer를 구축하는 것이다. 이는 발송 효율을 넘어 user가 brand를 경험하는 방식 자체를 다시 설계하는 문제다.

결국 MATCH는 사람의 개입이 전혀 없는 완전 자동화 black box가 아니다. Model, business policy, operation, verification이 유기적으로 맞물려 돌아가는 decision framework에 가깝다. 누가 어떤 decision authority를 가질지, 그 결과를 어떻게 측정하고 다음 decision에 어떻게 반영할지 고민하며 사람과 system이 조화롭게 협업하는 방식을 설계하는 일이다.

이 여정은 “왜 이 제품을 직접 만들어야 하는가”를 조직 안에서 계속 증명하는 과정이기도 했다. Databricks나 Braze 같은 글로벌 solution이 존재하는 상황에서 자체 구축이 왜 더 나은 대안인지 설명하고 설득해야 했기 때문이다. Business의 갈증을 system requirement로 번역하고, marketer·engineer·data scientist가 함께 system boundary를 조율하며, 실험 결과를 다음 decision에 곧바로 반영하는 cycle 자체가 팀의 중요한 자산이 되었다.

MATCH가 아직 모든 답을 갖고 있지 않다는 것은, 반대로 이 system 위에서 다음 질문을 함께 던지고 답을 만들어갈 동료가 필요하다는 뜻이기도 하다. 원문은 이번 MATCH series가 총 7부작으로 이어질 예정이라고 소개한다. 이어지는 주제는 MATCH console과 AI assistant MAI, CRM domain 적용기, Audience API 구축 과정, personalization model 설계와 검증 등이다.

## Practitioner 관점에서 읽을 포인트

이 글의 핵심은 “CDP를 만들었다”가 아니라, data product가 실제 business decision을 바꾸려면 어떤 layer가 필요한가에 있다. 특히 foundation-model이나 recommendation system 관점에서 보면 다음 지점이 중요하다.

1. Audience를 static segment가 아니라 user-creative fit을 예측하는 decision unit으로 재정의했다.
2. Campaign execution과 response signal을 feedback loop로 연결해, 실행이 다음 model quality로 되돌아오게 했다.
3. Marketer와 system 사이의 decision boundary를 명확히 했다. 사람은 creative와 business policy를, system은 targeting과 execution optimization을 맡는다.
4. 개별 domain optimization이 전체 customer journey와 충돌할 수 있음을 product architecture 차원에서 다뤘다.
5. 단기 conversion optimization이 신생 brand/category 노출 기회를 줄일 수 있다는 fairness와 exploration 문제를 명시적으로 인식했다.

MATCH는 recommender, CRM automation, campaign orchestration, real-time audience serving, organizational workflow가 한 시스템 안에서 만나는 사례다. 단순히 모델을 잘 만드는 문제보다, 모델이 실제 의사결정 권한을 어디까지 가져야 하고 그 결과를 어떻게 다시 학습으로 연결할지에 대한 product-system design 문제로 읽는 것이 더 적절하다.

## TEAM MUSINSA CAREER

원문 말미에서 무신사는 Personalization팀을 소개한다. 이 팀은 무신사, 29CM, 글로벌 등 팀무신사의 다양한 서비스에서 개인화 경험을 책임진다. 추천 모델 개발과 serving을 넘어 고객 행동 데이터 정의·수집·집계, persona와 segment 개발, 대규모 embedding 기반 modeling, real-time targeting API, automated campaign generation까지 end-to-end로 설계하고 운영한다.

관련 채용 링크는 다음과 같다.

- [Backend Engineer (Personalization)](https://www.musinsacareers.com/ko/o/219869)
- [Backend Engineer (Core Ads Platform)](https://www.musinsacareers.com/ko/o/221224)
- [Machine Learning Engineer (AdTech/MarTech)](https://www.musinsacareers.com/ko/o/220840)
