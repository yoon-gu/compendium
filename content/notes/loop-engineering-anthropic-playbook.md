---
title: "Loop Engineering: 에이전트를 프롬프트하는 시스템 설계"
date: 2026-07-05
draft: false
source_url: "https://huasheng.ai/orange-books"
author: "HuaShu / 공개 PDF 재구성"
tags: ["AI", "에이전트", "코딩 에이전트", "자동화", "Loop Engineering"]
summary: "Loop Engineering은 사람이 에이전트에게 한 줄씩 지시하는 자리에서 물러나, 에이전트를 프롬프트하고 검증하며 반복 실행하는 시스템 자체를 설계하는 일이다. 이 글은 loop의 다섯 move, generator-evaluator split, 실제 운영 사례와 비용을 정리한다."
---

전문은 [한국어 번역본](/compendium/papers/loop-engineering-anthropic-playbook/)에서 볼 수 있다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/loop-engineering-anthropic-playbook.pdf) — 공개 PDF 기반 재구성·번역본
- [원문 PDF](/compendium/papers/loop-engineering-anthropic-playbook-original.pdf)

> **원문:** *Loop Engineering: The Anthropic Playbook for Designing Systems That Prompt Your Agents* — 공개 공유 PDF 기반
>
> 원본 TeX 소스는 공개적으로 확인되지 않았다. Compendium에는 원문 PDF와, 원문 Figure를 PDF에서 직접 크롭해 반영한 한국어 재구성 번역 PDF를 함께 올렸다.

## 핵심 요약

Loop Engineering은 에이전트에게 매번 사람이 직접 지시하는 대신, 에이전트에게 지시를 보내고 결과를 검증하며 다음 run으로 이어 주는 시스템 자체를 설계하는 일이다. Prompt Engineering이 “무슨 말을 할까”를 다룬다면, Context Engineering은 “지금 context window에 무엇을 넣을까”를 다루고, Harness Engineering은 “한 번의 run에 어떤 tool과 stop condition을 줄까”를 다룬다. Loop Engineering은 그 위에서 “어떻게 스스로 다시 돌게 할까”를 다룬다.

원문은 한 turn의 loop를 다섯 move로 나눈다. Discovery는 이번 turn의 일을 스스로 찾는 과정이고, handoff는 작업을 격리된 환경으로 넘기는 과정이다. Verification은 생성한 에이전트가 아닌 별도 evaluator가 “아니오”라고 말할 수 있게 하는 부분이며, persistence는 대화 밖에 state를 남기는 일이다. 마지막으로 scheduling이 한 번의 run을 반복되는 loop로 바꾼다.

가장 중요한 설계 원칙은 generator와 evaluator의 분리다. 코드를 쓴 에이전트가 자기 코드를 평가하면 자기 숙제 채점이 된다. 원문은 evaluator를 다른 지시, 때로는 다른 모델로 구성하고, 단순히 코드를 읽는 데 그치지 않고 test를 실행하거나 browser를 조작하는 식으로 행동하게 해야 한다고 주장한다. Loop의 바닥은 evaluator다. Generator의 수준은 무엇을 만들 수 있는지를 정하지만, evaluator의 수준은 무엇을 만들지 않을지를 정한다.

위험도 분명하다. 검증 부채, 이해 부식, 인지적 항복, 토큰 폭증은 조용히 쌓인다. 루프가 많은 PR과 수정안을 만들수록, 사람이 읽고 판단하지 않으면 코드베이스에 대한 이해는 뒤처지고 자동화에 항복하기 쉬워진다. 그래서 좋은 루프는 사람을 없애는 장치가 아니라, 사람이 정말 판단해야 할 위치를 더 분명하게 만드는 장치다.
