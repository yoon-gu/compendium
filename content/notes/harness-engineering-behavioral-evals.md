---
title: "Harness Engineering의 해부: coding agent를 behavioral eval로 붙잡아 두기"
date: 2026-09-14
draft: false
source_url: "https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/"
author: "Taylor Mullen, Christian Gunderman (Google)"
tags: ["AI", "Agent", "평가", "Harness", "Google", "Antigravity", "코딩 에이전트"]
summary: "Terminal-Bench 같은 end-to-end benchmark는 점수가 왜 움직였는지 알려주지 않는다. Google의 Antigravity 팀은 그 자리를 behavioral evaluation으로 메운다 — 최종 결과 대신 '모호한 요청에 되물었는가', 'build validator를 돌렸는가' 같은 관찰 가능한 개별 행동을 unit test처럼 단정하는 방식이다."
---

> **원문:** [The Anatomy of Harness Engineering: How to Evaluate, Iterate, and Guard AI Coding Agents](https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/) — Taylor Mullen(Principal Engineer), Christian Gunderman(Staff Software Engineer), Google Developers Blog, 2026-09-09
>
> 아래는 원문을 한국어로 정리한 노트다.

## 한 줄 요약

Agent harness를 black box 시험 성적표로 평가하지 말고, 일반 소프트웨어처럼 unit test와 integration test로 다루라는 이야기다. 저자들은 그 integration test 자리에 행동 평가(behavioral evaluation)를 놓는다.

## 문제: 점수는 움직이는데 이유를 모른다

Agentic coding system의 harness engineering을 처음 붙잡는 팀은 대개 같은 함정에 빠진다. Terminal-Bench나 DeepSWE 같은 end-to-end benchmark를 돌리고, 종합 점수가 몇 퍼센트 움직이는 것을 지켜보고, 왜 움직였는지는 모른 채 끝난다.

점수가 떨어졌을 때 실제로 묻고 싶은 질문은 이런 것들이다.

- 모호한 prompt에서 model이 과신했는가
- 제출 전에 test suite 검증을 빼먹었는가
- 존재하지 않는 CLI flag를 환각했는가

End-to-end benchmark는 이 질문에 답하지 않는다. 답을 찾으려면 조사를 시작해야 하고, 그 조사 비용이 비싸다는 것이 핵심 불만이다.

## 성적표 대신 행동 지표

Behavioral eval은 multi-file refactor 전체를 풀었는지가 아니라, 관찰 가능한 개별 행동(discrete, observable action)을 본다. 원문이 드는 예시는 셋이다.

- 명세가 부족한 prompt를 받았을 때, 추측하지 않고 명확화 질문(clarifying question)을 하는가
- Build file을 수정했을 때, 완료 선언 전에 local validator를 돌리는가
- 문서를 생성할 때, 정규 repository 링크를 넣는가

이 정도 해상도의 eval set이 충분히 쌓이면 "이 agent에게 기대하는 행동"의 baseline이 생기고, 거기에 맞춰 prompt를 반복 개선할 수 있게 된다는 것이다.

## 언제 평가를 시작하나: dogfooding이 먼저

흥미로운 대목은 "첫날부터 eval harness를 세우지 말라"는 조언이다. 저자들은 개발을 두 단계로 나눈다.

첫 단계는 개발자의 감과 dogfooding이다. Agent가 자기 codebase를 다루고, boilerplate를 처리하고, 자기 markdown renderer를 짜고, 일상적인 개발 작업을 해내기 전까지는 평가를 돌리는 의미가 없다. 이 시기에는 직감을 따라 실험하라고 말한다.

Eval은 두 번째 단계, 즉 전진을 확인하고 회귀(regression)를 막는 단계의 물건이다. 그래서 eval suite의 목적은 agent가 2% 좋아진 것을 자축하는 데 있지 않다. **새 prompt 수정, tool schema 변경, model 업그레이드가 agent를 전체적으로 나쁘게 만들지 않았다는 확신**을 주는 데 있다.

## 어떻게 쓰나: 산출물이 아니라 행동을 단정한다

구조적으로는 behavioral assertion을 로컬에서 도는 빠르고 결정적인 unit 스타일 검사로 분리한다. 핵심 원칙은 한 문장으로 압축된다 — 결과 문장(output prose)이 아니라 행동을 단정하라.

즉 최종 문자열 일치가 아니라 중간 실행 단계, 특히 어떤 tool을 호출했는지와 어떤 파일을 고쳤는지를 본다. 원문의 Python 예제는 Antigravity SDK로 agent에게 마운틴뷰 날씨를 물은 뒤, 응답의 tool call 목록에 web search builtin이 들어 있는지를 `assert`한다. 기억으로 지어내지 않고 ground truth를 조회했는지를 확인하는 것이다.

여기서 한 걸음 더 나가면 prompt engineering 자체를 자동화할 수 있다. LLM이 자기 system prompt를 고쳐 가며 실패하는 test 하나를 통과할 때까지 반복하고, 나머지 test suite가 CI/CD guardrail처럼 기존 기능이 깨지지 않았음을 보장하는 loop다.

## 시작하는 법: 세 단계 loop

원문은 작게 시작하라며 세 단계를 제시한다.

1. 실패 모드 하나를 고른다. Agent가 최근에 저지른 실수 — 예컨대 task를 완료 처리하기 전에 unit test 돌리기를 잊은 것 — 에서 명백하게 빠진 동작 하나를 target으로 잡는다.

2. 과제 복잡도에 맞춰 단정의 강도를 조절한다. 최적해가 하나뿐인 단순한 과제라면 특정 milestone을 짚는 엄격한 단일 턴 단정이면 된다(test runner를 호출했는가). 복잡한 과제에서는 model이 예상 밖이지만 완전히 옳은 경로를 택할 수 있으므로, 경직된 tool 호출 순서를 강요하지 말고 LLM-as-a-judge 같은 결과 기반의 느슨한 검사를 쓴다.

3. Batch 평가를 자동화해 안정성을 본다. AI model의 비결정성 때문에 단일 eval 실행은 noisy하므로 PR을 거기에 걸지 않는다. 대신 더 큰 표본을 모아 시간에 따른 합격률 추세를 본다. 이 방향성 신호에 기대면 예상 범위의 변동 때문에 개발을 멈추지 않고도 prompt를 고치고 model을 올릴 수 있다.

로컬 suite는 `pytest evals/behavioral/ -v` 한 줄로 5초 안에 도는 정도를 기준으로 든다. 이 속도가 곧 "안전망"의 조건이다 — system prompt를 만지거나 model을 갈아 끼워도 핵심 행동이 깨졌는지 즉시 알 수 있어야 한다.

## 맺음: 둘은 대체재가 아니다

마지막 문단의 정리가 이 글의 온도를 잘 보여준다. Behavioral eval은 end-to-end suite를 대체하지 않고 보완한다. **거시(macro) benchmark는 최종 목적지를 검증하고, 미시(micro) behavioral eval은 안전하고 빠른 반복을 가능하게 하는 동반자** 역할을 한다.

시작하는 데 더 높은 benchmark 점수가 필요한 게 아니라, agent를 정직하게 붙잡아 둘 evaluation harness가 필요하다는 것이다.

## 함께 읽기

- [Loop Engineering: 에이전트를 돌리는 시스템을 설계한다](/compendium/notes/loop-engineering-anthropic-playbook/) — generator-evaluator를 분리해 loop 자체를 설계하는 관점
- [Deep Agents의 RubricMiddleware](/compendium/notes/deepagents-rubrics/) — 성공 기준을 rubric으로 정의하고 grader sub-agent가 평가하는, LLM-as-a-judge의 구현 사례
- [DeepEval로 하는 vibe coding](/compendium/notes/deepeval-vibe-coding/) — eval suite를 개발 loop 안에 넣고 span 단위로 실패를 좁히는 방법
