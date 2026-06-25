---
title: "Rubrics 소개: 자기 작업을 평가하고 고치는 에이전트 만들기"
date: 2026-06-26
draft: false
source_url: "https://www.langchain.com/blog/introducing-rubrics-for-deepagents"
author: "Shrikar Seshadri, Sydney Runkle (LangChain)"
tags: ["AI", "Agents", "LangChain", "Deep Agents", "Evaluation"]
summary: "LangChain의 Deep Agents에 추가된 RubricMiddleware는 개발자가 성공 기준을 rubric으로 정의하면 별도 grader sub-agent가 실행 결과를 평가하고, 기준을 만족할 때까지 에이전트가 수정 루프를 돌도록 한다. 테스트 통과, 금지 패턴 회피, 필수 섹션 포함처럼 검증 가능한 기준이 있는 작업에서 에이전트 출력의 분산을 줄이는 패턴이다."
---

> **원문:** [Introducing Rubrics: Build Agents that Evaluate and Correct Their Work](https://www.langchain.com/blog/introducing-rubrics-for-deepagents) — Shrikar Seshadri, Sydney Runkle, 2026년 6월 2일
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다.

## 핵심 요점

- 에이전트는 종종 방향은 맞지만 첫 시도에서 완전히 요구사항을 충족하지는 못하는 출력을 만든다.
- `RubricMiddleware`는 에이전트에게 “완료(done)”가 무엇인지 알려 주고, 그 지점에 도달할 때까지 계속 진행하게 만드는 방법이다.
- 테스트 통과, 금지된 패턴 회피, 필수 섹션 포함처럼 명확하고 검증 가능한 성공 기준이 있는 작업에서 가장 효과적이다.

에이전트는 어느 때보다 복잡한 작업을 맡고 있다. 하지만 꽤 자주 결승선에 도달하지 못한다. LangChain은 이 문제를 고치기 위해 [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview)에 [`RubricMiddleware`](https://docs.langchain.com/oss/python/deepagents/rubric)를 추가했다. 개발자가 rubric을 정의하면, 에이전트는 모든 기준을 만족하거나 설정된 상한에 도달할 때까지 자기 평가와 반복 수정을 수행한다.

Claude Code나 Codex의 [`/goal`](https://code.claude.com/docs/en/goal)에 익숙하다면, 이것은 비슷한 패턴이다. 다만 이 구현은 평가를 전담 grader [sub-agent](https://docs.langchain.com/oss/deepagents/subagents)가 처리하기 때문에 조금 더 유연하다. 이 grader는 도구를 호출할 수 있고, 전체 transcript를 바탕으로 추론할 수 있으며, 기준별 피드백을 반환할 수 있다.

## 문제

일부 에이전트 작업에는 “완료”의 정의가 명확하다. 코드 리팩터링은 테스트 스위트가 통과하면 끝난다. 보고서는 필요한 모든 섹션이 포함되면 완성된다.

하지만 에이전트가 항상 첫 시도에서 거기에 도달하는 것은 아니다. context가 커질수록 모호한 지시, 도구 오사용, 비결정적 오류가 누적된다. 그 결과 출력 품질이 떨어지고, 개발자는 문제를 진단한 뒤 작업을 수동으로 다시 실행해야 한다.

## 작동 방식

에이전트 실행이 끝나기 전에 별도의 grader sub-agent가 rubric에 비추어 실행 결과를 검토한다. 모든 기준을 통과하면 실행은 종료된다. 부족한 점이 있으면 grader의 기준별 피드백이 대화에 다시 주입되고, 에이전트가 다시 실행된다. 이 루프는 rubric이 만족되거나 설정된 반복 한도에 도달하면 끝난다.

![RubricMiddleware flow](https://cdn.prod.website-files.com/65c81e88c254bb0f97633a71/6a1f13e4883e8acba1e4792c_rubric_middleware_flow%20(2).svg)

루프는 `satisfied`, `max_iterations_reached`, `failed`, `grader_error` 중 하나의 상태로 종료된다.

## 연결하기

아래는 최소 설정을 단계별로 나눈 것이다. 핵심 아이디어는 `RubricMiddleware`를 한 번 정의하고, deep agent에 붙인 다음, invoke 시점에 `rubric` 문자열을 넘기는 것이다. `rubric`이 없으면 middleware는 아무 동작도 하지 않는다.

### 1) `RubricMiddleware` 정의

이 [middleware](https://docs.langchain.com/oss/python/deepagents/rubric#configure-the-middleware)는 기본 에이전트 위에 grader loop를 추가한다. grader는 다음 항목으로 설정된다.

- `model`: 채점에 사용할 LLM. 보통 main agent model보다 작거나 저렴한 모델을 쓴다.
- `system_prompt`: grader의 역할과 “좋은 결과”의 기준을 정의하는 지시문.
- [`tools`](https://docs.langchain.com/oss/deepagents/tools): grader가 근거를 수집하기 위해 호출할 수 있는 선택적 도구. 예를 들어 테스트 실행, lint, 출력 검증 도구가 여기에 들어간다.
- `max_iterations`: fix → re-grade 루프를 몇 번까지 반복할지 정하는 최대 횟수.

```python
from deepagents import RubricMiddleware

rubric_middleware = RubricMiddleware(
    model="anthropic:claude-haiku-4-5",
    system_prompt="You are a code reviewer grading generated code against a rubric.",
    tools=[run_test_suite],
    max_iterations=5,
)
```

### 2) deep agent에 전달하기

[deep agent](https://docs.langchain.com/oss/deepagents/quickstart)에도 자체 “운영 지침”이 있어야 한다. 에이전트의 `system_prompt`는 작업을 어떻게 수행할지를 알려 주고, rubric은 grader가 그 작업을 어떻게 판단할지를 알려 준다.

아래 코드에서 각 항목은 다음을 의미한다.

- `model`: 해결책을 생성하는 데 사용할 LLM.
- `system_prompt`: 에이전트가 따라야 할 코딩 관례와 제약.
- [`middleware`](https://docs.langchain.com/oss/langchain/middleware/overview): `rubric_middleware`를 붙여서 에이전트가 반복적으로 교정될 수 있게 한다.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=(
        "You are a careful Python engineer. Write correct, readable code. "
        "Follow the user’s instructions exactly."
    ),
    middleware=[rubric_middleware],
)
```

### 3) human message와 rubric으로 invoke하기

invoke 시점에는 다음을 제공한다.

- `messages`: 사람의 요청. 필요하면 이전 대화도 포함한다.
- `rubric`: grader가 만족 여부를 표시해야 하는 줄바꿈 구분 checklist.

```python
from langchain.messages import HumanMessage

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "Write a Python function `find_duplicates(lst)` that returns a list of "
                    "all elements that appear more than once in the input list, in the order "
                    "they first appear."
                )
            )
        ],
        "rubric": (
            "- All tests pass in run_test_suite\n"
            "- The function is named `find_duplicates` and accepts a single list argument\n"
        ),
    },
    config={"configurable": {"thread_id": "code-generation-session"}},
)
print(result["messages"][-1].text)
```

여기서는 grader에게 정확성을 추상적으로 추론하라고만 요구하지 않는다. 대신 `run_test_suite` 도구를 제공해 실제 동작을 직접 검증하게 한다. grader는 판정을 내리기 전에 도구를 호출해 강한 근거를 수집할 수 있다. 도구가 제공되지 않은 경우에는 transcript를 바탕으로 추론하는 방식으로 fallback한다.

## 실제 동작 보기

위 코드 생성 예시에서 에이전트의 첫 번째 시도는 겉으로는 맞아 보였지만 테스트 하나를 실패했다. grader는 다음과 같이 반환했다.

> “하나의 테스트가 실패합니다: `test_unhashable`. 이 함수는 입력 리스트 안에 list 같은 unhashable type이 들어오면 `TypeError`로 crash합니다.”

에이전트는 구현을 수정했고, 두 번째 반복에서 모든 테스트를 통과했다. 이 피드백은 일반적인 “다시 시도하라”가 아니다. 각 기준에는 자체 verdict가 있으므로, 에이전트는 정확히 무엇을 고쳐야 하는지 알 수 있다.

전체 예시는 [이 trace](https://smith.langchain.com/public/791de20a-83ba-4228-a5b8-e4e4f2d00719/r)에서 볼 수 있다.

## 왜 중요한가

에이전트 출력은 확률적이다. 같은 prompt가 어떤 실행에서는 성공하고, 다음 실행에서는 부족할 수 있다. `RubricMiddleware`는 이런 분산을 잡아내는 부담을 개발자에게서 시스템으로 옮긴다.

출력을 수동으로 검사하고 실패한 작업을 다시 실행하는 대신, “완료”가 무엇인지 한 번 정의하면 루프가 나머지를 처리한다. 각 retry는 정보가 있는 retry다. grader가 정확히 무엇이 잘못되었는지 식별하고, 기준별로 목표가 분명한 피드백을 생성하기 때문이다.

결과적으로 correctness가 중요한 작업에서 더 신뢰할 수 있는 에이전트를 만들 수 있다.

## 더 알아보기

`RubricMiddleware`는 beta 상태이며 API가 변경될 수 있다. configuration, observability, rubric persistence를 포함한 전체 walkthrough는 [문서](https://docs.langchain.com/oss/python/deepagents/rubric)를 참고하면 된다.
