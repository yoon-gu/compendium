# NotebookLM Podcast Brief — Intelligent AI Delegation

## Paper identity

- Title: Intelligent AI Delegation
- Authors: Nenad Tomašev, Matija Franklin, Simon Osindero
- arXiv: https://arxiv.org/abs/2602.11865
- Compendium: https://yoon-gu.github.io/compendium/papers/intelligent-ai-delegation/

## 한 문단 thesis

이 논문은 AI agent가 복잡한 목표를 수행하기 위해 task를 나누고 다른 AI 또는 인간에게 넘기는 과정을 단순 task decomposition이 아니라 authority, responsibility, accountability, trust, monitoring, permission, verification이 결합된 protocol 문제로 재정의한다. agentic web과 virtual agent economy가 커질수록 delegation은 orchestration convenience가 아니라 safety-critical coordination layer가 된다.

## 추천 episode 흐름

1. 왜 delegation이 단순 parallelization이 아닌가
2. 인간 조직 이론에서 가져온 개념: principal-agent problem, span of control, authority gradient, trust calibration
3. Intelligent Delegation Framework의 다섯 축
4. Monitoring, verifiable completion, permission handling, security가 production agent system에서 왜 필요한가
5. MCP/A2A/A2P 같은 protocol 생태계와의 연결
6. 실무자가 agent workflow를 설계할 때 적용할 checklist

## 영어로 남길 용어

AI agent, delegation, delegator, delegatee, task decomposition, task assignment, monitoring, trust, reputation, permission handling, verifiable completion, protocol, agentic web, MCP, A2A, A2P, workflow, accountability, authority gradient, span of control.

## Caveats

논문은 구체적인 benchmark나 implementation 결과보다 conceptual framework에 가깝다. 따라서 실무 적용 시에는 각 domain의 verification cost, permission boundary, rollback 가능성, monitoring granularity를 별도로 operationalize해야 한다.

## Closing takeaway

좋은 agent system은 일을 나눠 맡기는 API만 있는 시스템이 아니다. 누가 어떤 권한으로 무엇을 맡고, 실패를 어떻게 감지하며, 결과를 어떻게 검증하고, 책임을 어디에 귀속할지를 protocol 수준에서 설계해야 한다.
