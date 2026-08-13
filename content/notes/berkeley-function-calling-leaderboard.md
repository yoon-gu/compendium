---
title: "Berkeley Function Calling Leaderboard(BFCL): Tool Use에서 Agentic LLM 평가로"
date: 2026-08-13
draft: false
source_url: "https://openreview.net/forum?id=2GmDdhBdDk"
author: "Shishir G. Patil, Huanzhi Mao, Fanjia Yan, Charlie Cheng-Jie Ji, Vishnu Suresh, Ion Stoica, Joseph E. Gonzalez"
tags: ["AI", "LLM", "Function Calling", "Tool Use", "Benchmark"]
summary: "BFCL은 LLM의 function calling 능력을 single-turn tool call을 넘어 crowd-sourced query, multi-turn state, memory, SQL, agentic task까지 확장해 평가하는 benchmark다. 최신 model은 단순 tool call에는 강하지만 memory와 long-horizon decision-making에서는 여전히 취약하다."
---

> **원문:** [The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models](https://openreview.net/forum?id=2GmDdhBdDk) — Shishir G. Patil, Huanzhi Mao, Fanjia Yan, Charlie Cheng-Jie Ji, Vishnu Suresh, Ion Stoica, Joseph E. Gonzalez, ICML 2025 / PMLR 267
>
> OpenReview 직접 PDF/API는 이 환경에서 challenge/403으로 막혀, 공개 PMLR 페이지와 PDF를 기준으로 Compendium용 한국어 재구성본을 만들었다.

전문은 [한국어 번역본](/compendium/papers/berkeley-function-calling-leaderboard/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 재구성 번역본 PDF](/compendium/papers/berkeley-function-calling-leaderboard.pdf)
- [원문 PDF](/compendium/papers/berkeley-function-calling-leaderboard-original.pdf)

## 핵심 요약

BFCL은 function calling, 즉 LLM이 외부 function/API/tool을 호출하는 능력을 평가하기 위한 benchmark다. 기존 benchmark는 실제 user interaction을 충분히 반영하지 못하거나 LLM-based evaluator에 의존하는 경우가 많았다. BFCL은 AST substring matching, execution response matching, state-based/response-based evaluation, exact-match answer evaluation을 결합해 더 deterministic하고 scalable한 평가를 지향한다.

가장 중요한 차이는 평가 범위다. BFCL은 단순히 한 번의 prompt에서 올바른 function call을 만드는지만 보지 않는다. single-turn, crowd-sourced, multi-turn, agentic dataset을 포함해 missing parameter, missing function, long context, memory management, SQL, live relevance 같은 실제 deployment 문제를 다룬다.

논문의 결과는 실무적으로 유용하다. 최신 LLM은 simple/multiple/parallel single-turn call에서는 높은 성능을 보이지만, conversation이 길어지고 state가 바뀌며 memory snapshot을 사용해야 하는 setting에서는 성능이 크게 흔들린다. 즉 function calling을 “JSON schema를 맞히는 능력”으로만 보면 agentic application의 병목을 놓치게 된다.

## 왜 중요한가

Foundation model이나 agent framework를 평가할 때, tool use는 이제 부가 기능이 아니라 core capability다. 하지만 실제 제품에서는 tool call의 format correctness보다 더 까다로운 문제가 많다. 필요한 parameter가 없으면 질문해야 하고, tool이 irrelevant하면 호출하지 않아야 하며, read-only task에서는 결과를 추측하지 않고 올바른 tool path를 거쳐야 한다. BFCL은 이런 차이를 benchmark design 안에 명시적으로 넣었다.

## 읽을 때 볼 포인트

- AST matching이 execution 없이 function call correctness를 얼마나 잘 근사하는가
- crowd-sourced query가 synthetic single-turn query와 어떻게 다른가
- state-based evaluation과 response-based evaluation이 각각 어떤 failure를 잡는가
- memory management와 live relevance가 단순 tool calling benchmark를 어떻게 agentic evaluation으로 확장하는가
- 공개 leaderboard가 data contamination과 overfitting 문제를 어떻게 다뤄야 하는가
