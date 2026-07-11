---
title: "DeepEval로 Vibe Coding하기"
date: 2026-07-11
draft: false
source_url: "https://deepeval.com/docs/vibe-coding"
author: "DeepEval / Confident AI"
tags: ["AI", "LLM Evaluation", "Agent", "Vibe Coding", "DeepEval"]
summary: "DeepEval의 eval suite를 coding agent 개발 loop 안에 넣어, 실패 metric과 trace를 읽고 작은 수정 단위로 agent·RAG·chatbot을 개선하는 방법을 설명한다. 핵심은 dataset, eval suite, `deepeval test run`, span-level localization, 그리고 반복적인 patch-and-verify loop다."
---

> **원문:** [Vibe Coding with DeepEval](https://deepeval.com/docs/vibe-coding) — DeepEval / Confident AI
>
> 아래 글은 원문 문서의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 코드 identifier, CLI command, metric 이름, tool·agent workflow 용어는 실무자가 그대로 쓰는 English form을 우선 유지했다.

DeepEval은 AI quality validation suite로도 훌륭하다. 예를 들면 pytest assertion, regression gate, CI/CD failure tracking 같은 용도로 쓸 수 있다. 하지만 이것은 use case의 절반일 뿐이다.

나머지 절반은 같은 eval을 개발 중에 사용하는 것이다. coding agent가 eval을 실행하고, 실패한 metric과 trace를 읽고, 그 결과를 바탕으로 agent, RAG pipeline, chatbot에서 다음에 무엇을 바꿔야 하는지 결정한다. 그런 다음 다시 실행해 수정이 맞았는지 확인한다.

짧게 말하면, **DeepEval은 agent를 vibe coding하지 않으면서 agent를 vibe code할 수 있게 해준다.**

> 빠르게 skill을 설치하고 Cursor / Claude Code / Codex에 starter prompt를 붙여 넣고 싶다면 원문의 [5-min Vibe Coder Quickstart](https://deepeval.com/docs/vibe-coder-quickstart)로 바로 가면 된다. 이 문서는 그 loop 자체, 즉 실제로 무엇이 실행되고 왜 작동하며 어떻게 drive하는지를 설명한다.

## The Loop

DeepEval을 이용한 vibe coding은 eval suite와 coding agent 사이의 feedback loop다.

1. dataset을 정의하거나, DeepEval이 문서, trace, 기존 example에서 dataset을 생성하게 한다.
2. 해당 dataset으로 agent를 호출하고 관심 있는 metric으로 output을 score하는 eval suite를 추가한다.
3. coding agent가 suite를 실행하고, failure를 읽고, 관련 prompt, retrieval logic, tool, application code를 targeted하게 바꾸도록 한다.
4. score와 metric reason이 behavior 개선을 보여줄 때까지 같은 eval을 다시 실행한다.

`deepeval test run`의 trace는 coding agent에게 단순한 pass/fail 이상의 정보를 준다. 여기에는 score, span-level context, metric reason이 포함되어 있으므로, failure를 해당 system의 어느 부분이 만들었는지까지 거슬러 올라갈 수 있다.

예를 들어 run이 `faithfulness 0.64`를 보고하면, agent는 off-source claim을 만든 retriever span을 열고, retrieval을 active refund policy로 좁힌 뒤, eval을 다시 실행해 수정이 통했는지 확인할 수 있다. 이 workflow는 tight unit-test cycle과 비슷하다. 다만 assertion은 score가 매겨진 model output이고 runner는 coding agent라는 점이 다르다.

## Under the Hood

[Agent Skill](https://deepeval.com/docs/vibe-coder-quickstart#install-the-agent-skill)이 설치된 상태에서 사용자가 “add evals to this repo and fix the failing ones”라고 말하면, coding agent는 evaluation framework를 새로 꾸며내지 않는다. 대신 DeepEval CLI를 shell out한다. 구체적으로 매 iteration round는 [CLI reference](https://deepeval.com/docs/command-line-interface)에 문서화된 단일 CLI command에 기대어 다음 stage들을 지난다.

### 1. Dataset load 또는 generate

agent는 먼저 `tests/evals/`, Confident AI, 또는 Hugging Face dataset에 기존 dataset이 있는지 찾는다.

아무것도 없으면 [`deepeval generate`](https://deepeval.com/docs/command-line-interface#generate)로 dataset을 만든다. 이 single command는 custom Python 없이 docs, context, scratch, 기존 golden에서 single-turn 또는 multi-turn golden을 합성한다.

```bash
deepeval generate \
  --method docs \
  --variation single-turn \
  --documents ./docs \
  --output-dir ./tests/evals \
  --file-name .dataset
```

생성된 `.dataset.json`은 repo에 commit된다. 이후 run은 이를 재사용하고, 새로운 edge case는 여기에 append된다.

### 2. Eval suite build

skill은 네 가지 흔한 shape에 대한 [pytest template](https://github.com/confident-ai/deepeval/tree/main/skills/deepeval/templates)을 제공한다. single-turn end-to-end, multi-turn end-to-end, single-turn component-level, 그리고 shared `conftest.py`다. agent는 가장 가까운 template을 고르고 placeholder(dataset path, app entrypoint, metric, threshold)를 채운 뒤 `tests/evals/test_<app>.py` 같은 committed file을 작성한다. throwaway script도, 숨겨진 golden도 없다. 이 suite는 agent 없이도 다시 실행된다.

agent가 고르는 metric도 임의로 invent되는 것이 아니다. [50+ metrics catalog](https://deepeval.com/docs/metrics-introduction)의 `GEval`, `AnswerRelevancyMetric`, `FaithfulnessMetric`, `ToolCorrectnessMetric`, `ConversationalGEval` 등에서 가져오며, 각 metric에는 default threshold와 agent가 읽을 수 있는 `reason` field가 있다.

### 3. Suite 실행

이제 loop의 heartbeat는 [`deepeval test run`](https://deepeval.com/docs/command-line-interface#test-run)이다. 매 round마다 같은 command를 사용하므로 UI rerun에서 생기는 flake가 없다.

```bash
deepeval test run tests/evals/test_<app>.py \
  --identifier "iterating-on-retrieval-round-1" \
  --num-processes 5 \
  --ignore-errors \
  --skip-on-missing-params
```

CLI는 test별, metric별 score와 metric `reason` string을 출력한다. 이것이 agent가 다음 변경을 선택하기 위해 parse하는 structured output이다.

### 4. Failure localize

`@observe`가 켜져 있으면 모든 span(`retriever`, `lookup_order`, `classify_intent`, `draft_response`)이 자체 scored metric을 가진다. 실패한 Faithfulness score는 “app이 나쁘다”가 아니다. “`retrieve_policy_docs` span이 deprecated policy를 인용했기 때문에 0.64를 받았다”에 가깝다. agent는 전체 app이 아니라 그 span을 소유한 file을 연다.

이것이 loop를 actionable하게 만드는 핵심이다. 자세한 동작은 DeepEval의 [component-level evals](https://deepeval.com/docs/evaluation-component-level-llm-evals)에서 볼 수 있다.

### 5. Patch and verify

agent는 실패한 metric을 고칠 수 있을 법한 가장 작은 것부터 edit한다. prompt, retriever filter, tool argument schema, parser 등이 될 수 있다. 그런 다음 같은 `deepeval test run` command를 다시 실행한다. 실패 metric이 green으로 바뀌고 다른 metric이 regress하지 않으면 그 round는 닫힌다. 그렇지 않으면 다음으로 작은 변경을 고른다.

skill의 [iteration-loop reference](https://github.com/confident-ai/deepeval/blob/main/skills/deepeval/references/iteration-loop.md)는 agent가 자동으로 따라야 할 guardrail을 포함한다. failure를 없애기 위해 threshold를 낮추지 말 것, 어려운 golden을 삭제하지 말 것, 묻지 않고 model이나 framework를 바꾸지 말 것 같은 규칙이다.

## Why This Works

DeepEval에는 coding agent에게 특히 좋은 signal source가 되는 세 가지 속성이 있다. 이것들이 “eval을 한 번 돌렸다”를 “agent가 무엇을 바꿔야 하는지 알았다”로 바꾼다.

- Structured output. 모든 metric은 numeric score, threshold 대비 pass/fail, natural-language `reason`을 반환한다. agent가 log scraping 없이 parse할 수 있다.
- Span-level localization. `@observe(metrics=[...])`를 사용하면 failure가 전체 app이 아니라 failing span을 소유한 file을 가리킨다.
- Reproducible CLI 하나. 같은 `deepeval test run` command, 같은 dataset, 같은 metric을 쓴다. agent는 fix가 score를 실제로 움직였는지 확인하는 command를 하나만 알면 된다.

## How to Prompt Your Coding Agent

가장 큰 mindset shift는 coding agent에게 “DeepEval을 추가하고 끝내라”고 말하지 않는 것이다. 대신 **loop를 drive하라**고 요청해야 한다.

build phase에 좋은 prompt 예시는 다음과 같다.

- “Run `deepeval test run tests/evals/` and fix the lowest-scoring metric. Don't change thresholds. Re-run to confirm.”
- “The Faithfulness metric is failing on cases 3, 7, and 12. Open the retriever span for each, find the common pattern, and patch the retriever — not the metric.”
- “Run 5 rounds of the iteration loop. Each round: run evals, pick one failing metric, edit the smallest thing that could fix it, re-run, summarize what changed.”

마지막 prompt는 skill이 enforce하는 iteration loop에 직접 대응한다. skill이 설치되어 있다면 “Use DeepEval to fix the refund agent — run 5 rounds”만으로 충분하다.

## Connect to Confident AI

DeepEval은 local-first이며 위 loop는 완전히 offline에서도 동작한다. [Confident AI](https://www.confident-ai.com)에 연결하면 이 loop를 team 전체로 확장할 수 있다.

```bash
deepeval login
```

coding agent가 실행하는 모든 `deepeval test run`은 reviewer가 `deepeval view`로 열 수 있는 testing report를 push한다. production monitoring은 새로운 failure case를 dataset으로 다시 보내므로, 다음 iteration round가 실제 regression을 자동으로 포함하게 된다.

## Next Steps

이제 자신의 repo에서 loop를 drive하면 된다. coding agent가 각 stage에서 정확히 어떤 command를 실행하는지 알고 싶다면 CLI reference에서 전체 surface를 확인할 수 있다.

- [5-min Vibe Coder Quickstart](https://deepeval.com/docs/vibe-coder-quickstart): skill을 설치하고 starter prompt를 붙여 넣어 loop를 coding agent에게 넘긴다.
- [CLI Reference](https://deepeval.com/docs/command-line-interface): loop가 사용하는 모든 flag, 즉 `deepeval generate`, `deepeval test run`, `deepeval view`를 확인한다.
