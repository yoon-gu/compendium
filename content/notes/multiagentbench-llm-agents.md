---
title: "MultiAgentBench: LLM 에이전트 협업·경쟁 벤치마크"
date: 2026-06-04
draft: false
math: true
source_url: "https://arxiv.org/abs/2503.01935v1"
author: "Kunlun Zhu et al. (UIUC)"
tags: ["AI", "LLM", "에이전트", "멀티 에이전트", "벤치마크", "MARBLE"]
summary: "MultiAgentBench는 LLM 기반 멀티 에이전트 시스템을 다양한 협업·경쟁 환경에서 평가하고, 단순 task success뿐 아니라 계획, 커뮤니케이션, milestone 기반 KPI를 함께 측정한다."
---

전문은 [한국어 번역본](/compendium/papers/multiagentbench-llm-agents/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/multiagentbench-llm-agents.pdf)
- [arXiv 원문 PDF](/compendium/papers/multiagentbench-llm-agents-original.pdf)

MultiAgentBench는 LLM 기반 멀티 에이전트 시스템을 연구 공동 저술, Minecraft 건축, 데이터베이스 이상 진단, 코딩 협업, Werewolf, bargaining 같은 다양한 상호작용 환경에서 평가하기 위한 벤치마크다. 결론의 핵심은 MARBLE 프레임워크와 평가 지표가 단순 task success를 넘어 계획, 커뮤니케이션, 경쟁 상황에서의 조정 품질을 함께 측정한다는 점이다. 저자들은 실험을 통해 LLM 에이전트에서 신뢰, 정보 공개, 반복적 협력 실패 같은 창발적 사회 행동을 관찰했다고 정리한다.

한계는 네 가지다. 첫째, 시나리오와 모델 범위가 제한적이다. 현재는 특정 도메인과 일부 경쟁 환경에 집중하며, 오픈 월드, 풍부한 사회적 인지, task-oriented dialogue, DeepSeek 계열 같은 최신 모델을 더 포함할 필요가 있다. 둘째, 절제 연구가 충분히 세분화되지 않았다. 장기·단기·공유 메모리, 다른 멀티 에이전트 워크플로의 영향을 더 분석해야 한다. 셋째, 경쟁 메커니즘은 다자 협상, 반복 게임, 확률적 요소를 충분히 포착하지 못한다. 넷째, 대부분의 과제가 명확한 목표를 갖기 때문에 개방형·모호한 실제 과제를 다루는 확장이 필요하다.

부록은 프레임워크와 환경별 평가 설계를 상세히 설명한다. MARBLE은 configuration, environment, memory, communication, action 모듈로 구성된다. 설정 모듈은 에이전트 프로필과 관계를 초기화하고, 환경 모듈은 함수 호출 기반 상호작용을 제공하며, 메모리 모듈은 공유·개별 메모리와 RAG 기반 검색을 관리한다. 커뮤니케이션 모듈은 역할 협상과 정보 공유를 지원하고, 행동 모듈은 계획 실행 결과를 메모리에 다시 반영한다.

환경별로는 Research Scenario가 100개 ML/AI 논문과 저자 프로필을 기반으로 5Q 형식의 연구 아이디어를 생성하게 하며, 혁신성·안전성·실행 가능성을 평가한다. Werewolf는 숨겨진 역할과 비대칭 정보가 있는 사회적 추론 게임으로, 주민 진영의 협력 품질을 중심으로 평가한다. Partial-Day에서는 예언자 보호, 늑대인간 추방, 주민 구출, 늑대인간 독살 같은 단기 과제를 보고, Full-Game에서는 net score, result score, 주민 승률을 본다. Llama3.3-70B가 Werewolf에서 가장 좋은 결과를 보였고, GPT-4o baseline보다 높은 주민 승률을 기록했다. 실패 사례는 고성능 모델도 정보 공개와 상호 신뢰가 부족하면 패배할 수 있음을 보여 준다.

Database Environment는 PostgreSQL 성능 이상 원인(Fetch/Insert Large Data, Lock Contention, Redundant Index, Vacuum)을 진단한다. 에이전트는 pg_locks, pg_stat_statements 같은 시스템 뷰를 질의하고, 50개 샘플에서 두 개 후보 중 하나가 정답이면 correct로 계산한다. Coding Scenario는 SRDD 기반 과제에서 코드 작성, 실행, 디버깅, 테스트, 리뷰 도구를 사용하며 지시 준수·실행 가능성·일관성·품질을 본다. Bargaining Scenario는 Amazon 제품 100개와 Big Five 성격 프로필을 사용해 두 판매자와 두 구매자의 협상을 평가한다. Minecraft Scenario는 VillagerAgent/Mineflayer 기반으로 블록 구조물 건축을 수행하며, 올바른 유형·위치·방향의 블록 hit rate를 점수화한다. 특히 함수 호출 실행 가능률이 낮으면 task score가 크게 하락한다.

평가 프롬프트는 실무적으로 중요하다. 커뮤니케이션 프롬프트는 결정의 효과성, 명확성, 사회적 관계·프로필 정렬, 과제 진척 기여도를 1-5점으로 평가한다. 계획 프롬프트는 역할 정의, task assignment, workload distribution, 전략적 조정을 평가한다. KPI 프롬프트는 연구 과제에서 `form 5q` 또는 `improve 5q` milestone 달성 여부와 핵심 기여 에이전트를 기록한다. 5Q task score 프롬프트는 혁신성·안전성·실행 가능성을 JSON 점수로 출력한다.

Foundation model/BERT 실무자 관점에서 핵심 메시지는 개별 모델 성능과 시스템 성능이 다르다는 것이다. BERT류 모델이 검색, 분류, 이상탐지, 코드 검증 등 하위 모듈로 강해도, 멀티 에이전트 시스템에서는 메모리 설계, 함수 호출 실행 가능성, 역할 분배, 정보 공유 타이밍, 반복 커뮤니케이션 억제가 성능을 좌우한다. 따라서 평가 시 최종 점수만 보지 말고 로그 기반으로 커뮤니케이션 반복, 도구 호출 실패, milestone 달성, 신뢰 형성과 정보 공개 전략을 함께 분석해야 한다.
