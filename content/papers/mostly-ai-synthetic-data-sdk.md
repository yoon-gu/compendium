---
title: "오픈소스 합성 데이터 SDK를 통한 테이블형 데이터 접근의 민주화"
date: 2026-06-24
draft: false
math: true
source_url: "https://arxiv.org/abs/2508.00718"
author: "Ivona Krchova, Mariana Vargas Vieyra, Mario Scriminaci, Andrey Sidorenko (MOSTLY AI)"
tags: ["AI", "Synthetic Data", "Tabular Data", "Privacy", "Open Source"]
summary: "MOSTLY AI Synthetic Data SDK는 테이블형 데이터 합성을 위한 오픈소스 Python SDK로, TabularARGN 기반 생성, 차등 개인정보 보호, 공정성 제약, 자동 품질 보증을 하나의 실무형 인터페이스로 묶는다."
---

짧은 요약은 [/notes/mostly-ai-synthetic-data-sdk/](/compendium/notes/mostly-ai-synthetic-data-sdk/)에서 볼 수 있다.

> **원문:** [Democratizing Tabular Data Access with an Open-Source Synthetic-Data SDK](https://arxiv.org/abs/2508.00718) — Ivona Krchova, Mariana Vargas Vieyra, Mario Scriminaci, Andrey Sidorenko, MOSTLY AI, arXiv 2508.00718
>
> 아래 글은 원문 논문의 순서와 서술을 최대한 따라가며 한국어로 옮긴 것이다. 이 Markdown 페이지는 논문의 진입점이며, 원문 레이아웃·그림·표·코드 목록을 보존한 전체 구조 보존 번역은 한국어 PDF를 기준으로 제공한다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/mostly-ai-synthetic-data-sdk.pdf) — 원문 레이아웃을 보존한 한국어판
- [arXiv 원문 PDF](/compendium/papers/mostly-ai-synthetic-data-sdk-original.pdf)

## 전문 번역 안내

이 논문은 IEEE 양식의 TeX 원문을 한국어 TeX로 옮겨 XeLaTeX로 다시 빌드했다. 본문 섹션, 그림, 표, 코드 목록, 라벨, 참조, 인용, 참고문헌 구조를 보존했으며, Markdown 본문에는 PDF를 대체해 모든 표와 코드 목록을 다시 펼치지 않는다.

전체 번역은 위의 한국어 PDF에서 확인할 수 있다. PDF에는 다음 흐름이 원문 순서대로 포함된다.

1. Introduction — 데이터 접근 병목, 합성 데이터의 역할, SDK의 기여
2. Architecture Overview and Workflow — SDK 구성 요소와 기본 사용 흐름
3. Data Ingestion and Processing — 데이터 준비, 컬럼 인코딩, 개인정보 보호 전략, 다중 테이블 관계 관리
4. Generative Model Training — TabularARGN 개요, LLM 파인튜닝 지원, 조기 중지·드롭아웃·차등 개인정보 보호
5. Synthetic Data Generation — 유연한 생성, 재조정, 스마트 대치, 공정성 제약
6. Empirical Performance and Community Adoption — 품질·확장성 비교와 GitHub/community adoption 지표
7. Conclusion and Acknowledgment

## NotebookLM 활용 메모

`papers-tex/mostly-ai-synthetic-data-sdk/notebooklm-podcast-brief.md`에 한국어 팟캐스트 브리프를 함께 추가했다. NotebookLM에 원문 PDF와 한국어 PDF를 넣을 때 이 브리프를 진행 구성과 발음·용어 지침으로 사용할 수 있다.
