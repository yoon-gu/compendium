---
title: "Berkeley Function Calling Leaderboard(BFCL): Tool Use에서 Agentic LLM 평가로"
date: 2026-08-13
draft: false
math: true
source_url: "https://openreview.net/forum?id=2GmDdhBdDk"
author: "Shishir G. Patil, Huanzhi Mao, Fanjia Yan, Charlie Cheng-Jie Ji, Vishnu Suresh, Ion Stoica, Joseph E. Gonzalez"
tags: ["AI", "LLM", "Function Calling", "Tool Use", "Benchmark", "Agent"]
summary: "BFCL은 function calling benchmark를 single-turn tool use에서 crowd-sourced, multi-turn, memory, SQL, agentic evaluation으로 확장한다."
---

짧은 요약은 [/notes/berkeley-function-calling-leaderboard/](/compendium/notes/berkeley-function-calling-leaderboard/)에서 볼 수 있다.

> **원문:** [The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models](https://openreview.net/forum?id=2GmDdhBdDk) — Shishir G. Patil, Huanzhi Mao, Fanjia Yan, Charlie Cheng-Jie Ji, Vishnu Suresh, Ion Stoica, Joseph E. Gonzalez, ICML 2025 / PMLR 267
>
> 아래 글은 원문 논문의 구조를 따라가며 한국어로 재구성한 것이다. OpenReview 직접 PDF/API는 이 환경에서 challenge/403으로 막혔고, PMLR 공개 PDF는 접근 가능했으나 확인한 공개 경로에서 원저자 TeX/source archive는 발견되지 않았다. 따라서 한국어 PDF/TeX는 원저자 source가 아니라 public PDF text extraction 기반의 **PDF-only reconstruction**이다.

**PDF 다운로드**

- [한국어 재구성 번역본 PDF](/compendium/papers/berkeley-function-calling-leaderboard.pdf) — 공개 PDF에서 재구성한 한국어판
- [원문 PDF](/compendium/papers/berkeley-function-calling-leaderboard-original.pdf)

**관련 링크**

- [PMLR proceedings page](https://proceedings.mlr.press/v267/patil25a.html)
- [BFCL leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [Software repository](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard)

## 한국어 재구성 번역본

이 페이지의 canonical full translation은 위의 [한국어 PDF](/compendium/papers/berkeley-function-calling-leaderboard.pdf)다. PDF에는 abstract, introduction, related work, BFCL dataset 구성, evaluation methodology, result analysis, conclusion, impact statement, appendix A-J를 포함해 원문 PDF의 주요 구조를 순서대로 재구성했다.

## 논문의 중심 주장

BFCL은 function calling을 단순한 schema-following 문제가 아니라 agentic evaluation 문제로 다룬다. Single-turn function invocation에서는 최신 LLM이 이미 강한 성능을 보이지만, real deployment에서는 missing parameter, irrelevant tool, multi-turn state update, memory retrieval/update, SQL operation, live relevance 같은 조건이 함께 등장한다. BFCL은 이런 조건을 deterministic metric과 실제 user-contributed query로 평가한다.

## Benchmark 구성

1. Single-turn dataset: simple, multiple, parallel, parallel multiple, irrelevance/relevance function call을 평가한다.
2. Crowd-sourced dataset: 실제 user query에서 출발해 더 복잡한 function 수와 parameter 수를 포함한다.
3. Multi-turn dataset: Base, Missing Parameters, Missing Functions, Long Context를 통해 stateful conversation을 평가한다.
4. Agentic dataset: live relevance, memory management, SQL category를 통해 answer format, persistence, state, structured operation을 평가한다.

## 평가 방법

BFCL의 핵심은 AST substring matching이다. Model output을 Python-callable 형태로 제한한 뒤 AST로 parse하고, function name과 parameter value가 ground truth set에 맞는지 확인한다. 실제 execution 없이도 scalable하게 평가할 수 있고, 저자들은 subset에서 execution-based metric과 높은 correlation을 확인했다. Multi-turn에서는 final state가 ground truth와 맞는지 보는 state-based evaluation과, read-only task에서 올바른 function trajectory를 따랐는지 보는 response-based evaluation을 함께 사용한다.

## 실무적 시사점

BFCL 결과는 function calling model을 평가할 때 단순 JSON validity나 single-turn score만 봐서는 부족하다는 점을 보여준다. Agent product에서 중요한 것은 tool을 “부르는” 능력뿐 아니라, 언제 부르지 않아야 하는지, 어떤 정보를 더 물어야 하는지, state를 어떻게 갱신해야 하는지, memory를 어떻게 읽고 지워야 하는지다. BFCL은 이 차이를 benchmark category로 분해해 보여준다.
