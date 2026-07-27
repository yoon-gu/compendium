---
title: "지능형 AI Delegation"
date: 2026-07-27
draft: false
math: true
source_url: "https://arxiv.org/abs/2602.11865"
author: "Nenad Tomašev, Matija Franklin, Simon Osindero"
tags: ["AI", "Agents", "Delegation", "Multi-Agent", "Safety"]
summary: "AI agent 간, 그리고 AI-human 간 task delegation을 안전하고 adaptive하게 수행하기 위한 intelligent delegation 프레임워크를 제안한다."
---

짧은 요약은 [/notes/intelligent-ai-delegation/](/compendium/notes/intelligent-ai-delegation/)에서 볼 수 있다.

> **원문:** [Intelligent AI Delegation](https://arxiv.org/abs/2602.11865) — Nenad Tomašev, Matija Franklin, Simon Osindero, arXiv 2602.11865
>
> 아래 글은 원문 논문의 순서와 서술을 최대한 따라가며 한국어로 옮긴 것이다. 원문의 figure, table, citation, section 구조를 보존한 canonical full translation은 PDF로 제공한다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/intelligent-ai-delegation.pdf) — 원문 레이아웃을 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/intelligent-ai-delegation-original.pdf)

## 전문 번역 안내

이 항목의 전체 번역은 TeX source를 기반으로 재빌드한 [한국어 PDF](/compendium/papers/intelligent-ai-delegation.pdf)를 canonical version으로 삼는다. Markdown page는 검색과 웹 열람을 위한 간단한 entry point이며, 원문의 모든 table, figure, citation, bibliography 구조는 PDF에 보존되어 있다.

## Abstract 번역

AI agent는 점점 더 복잡한 task를 처리할 수 있게 되었다. 더 야심찬 goal을 달성하려면 AI agent는 문제를 관리 가능한 sub-component로 의미 있게 분해하고, 그 completion을 다른 AI agent 또는 인간에게 안전하게 delegate할 수 있어야 한다. 그러나 기존 task decomposition과 delegation 방법은 단순 heuristic에 의존하며, environmental change에 동적으로 적응하거나 unexpected failure를 robust하게 처리하지 못한다.

이 논문은 **intelligent AI delegation**을 위한 adaptive framework를 제안한다. 여기서 delegation은 task allocation과 관련된 일련의 decision일 뿐 아니라 transfer of authority, responsibility, accountability, roles and boundaries의 명확한 specification, intent clarity, 그리고 둘 이상의 party 사이에 trust를 수립하기 위한 mechanism을 포함한다. 제안 프레임워크는 복잡한 delegation network에서 human 및 AI delegator/delegatee 모두에 적용될 수 있으며, emergent agentic web에서 protocol development를 안내하는 것을 목표로 한다.
