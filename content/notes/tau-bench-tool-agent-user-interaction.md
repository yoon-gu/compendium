---
title: "τ-bench: Tool-Agent-User 상호작용을 위한 고객지원 benchmark"
date: 2026-08-12
draft: false
math: true
source_url: "https://arxiv.org/abs/2406.12045"
author: "Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan"
tags: ["AI", "LLM", "에이전트", "벤치마크", "도구 사용", "대화형 에이전트", "고객지원", "시뮬레이션"]
summary: "τ-bench는 customer service형 대화에서 agent가 user와 tool/API를 함께 다루고, domain-specific policy를 얼마나 일관되게 따르는지 평가하는 benchmark다. retail와 airline 두 domain을 통해 단순 function calling 정확도가 아니라 장기 대화, policy 준수, database state consistency, pass^k 기반 신뢰성을 함께 측정한다."
---

전문은 [한국어 번역본](/compendium/papers/tau-bench-tool-agent-user-interaction/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/tau-bench-tool-agent-user-interaction.pdf)
- [arXiv 원문 PDF](/compendium/papers/tau-bench-tool-agent-user-interaction-original.pdf)

$\tau$-bench는 tool을 호출하는 LLM agent를 평가할 때, 단순히 “올바른 function call을 만들었는가”만 보는 방식이 충분하지 않다는 문제의식에서 출발한다. 실제 고객지원 환경에서는 agent가 user와 여러 차례 대화하면서 identity를 확인하고, 누락된 정보를 수집하고, policy를 해석하고, database/API를 조작한 뒤, 다시 user에게 필요한 설명과 확인을 제공해야 한다. 논문은 이 end-to-end 상호작용을 Tool-Agent-User benchmark라는 형태로 정식화한다.

핵심 설계는 세 층이다. 첫째, agent는 숨겨진 database에 직접 접근하지 못하고 API tool을 통해서만 상태를 읽고 쓴다. 둘째, user는 고정된 canned response가 아니라 LM-simulated user로 구현되어, 같은 underlying task라도 발화가 매번 조금씩 달라질 수 있다. 셋째, agent는 domain-specific policy 문서를 system prompt 수준에서 참조하며, 단순 사실 조회가 아니라 규칙 준수까지 평가받는다. 이 구조 덕분에 benchmark는 함수 호출 정확도, 정책 해석, 대화 기억, 정보 수집, 최종 database state consistency를 함께 본다.

도메인은 `\tau-retail`과 `\tau-airline` 두 가지다. retail에서는 pending order 수정, delivered order return/exchange, 주소 변경, 정보 제공 같은 task를 다룬다. airline에서는 reservation booking/change/cancel, baggage allowance, refund, certificate 처리처럼 더 ad-hoc한 rule이 많이 등장한다. 논문의 관찰대로 airline이 더 어렵고, policy 제거 ablation에서도 성능 저하가 더 크게 나타난다. 이는 agent가 실제로 긴 규칙 문서를 읽고 적용해야 하는 난도가 retail보다 더 높다는 뜻이다.

평가 방식도 실무적으로 의미가 있다. 각 task는 가능한 최종 database outcome이 하나만 되도록 설계되고, episode 종료 후 최종 database state와 user-facing output을 ground truth와 비교해 성공 여부를 정한다. 여기에 논문은 `pass^k`를 도입한다. 이는 여러 번의 독립 trial 가운데 하나만 성공하면 되는 `pass@k`와 달리, 같은 task를 $k$번 다시 실행했을 때 전부 성공할 확률을 본다. 고객지원 자동화처럼 “평균적으로 가끔 잘함”보다 “같은 의미의 요청에 반복 가능하게 잘함”이 중요한 환경에서는 이 지표가 더 직접적이다.

결과는 보수적이다. `gpt-4o` function calling baseline도 retail에서 약 61\%, airline에서 약 35\% 수준에 머무르며, `pass^8`은 retail에서 25\% 미만으로 떨어진다. 즉 현재 상용 최고급 모델조차 긴 대화, policy 준수, compound request 처리, 복잡한 database reasoning을 안정적으로 해결하지 못한다. failure breakdown에서는 잘못된 argument 선택, 잘못된 정보 제공, policy를 놓친 의사결정, 여러 요청 중 일부만 해결하는 문제가 반복적으로 나타난다.

이 논문이 주는 메시지는 분명하다. production agent를 평가할 때는 평균 1회 성공률만 보아서는 안 되고, 같은 task semantics 아래에서 conversation variation이 생겨도 규칙을 지키며 일관되게 끝까지 해결하는지 봐야 한다. $\tau$-bench는 그 문제를 간단한 offline QA나 single-turn function calling benchmark보다 훨씬 현실적으로 드러내는 평가 장치다.
