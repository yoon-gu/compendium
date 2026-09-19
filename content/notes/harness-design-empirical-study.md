---
title: "코딩 에이전트 harness 설계에 대한 실증 연구: 계획, 액션 공간, 컨텍스트 관리를 따로 떼어 보기"
date: 2026-09-19
draft: false
math: true
source_url: "https://arxiv.org/abs/2609.20804"
author: "Run-Ze Fan, Zihao Zhang, Simin Ma, Yebowen Hu, Shouju Wang, Kaiqiang Song, Fei Liu, Hamed Zamani, Xiaoyang Wang (UMass Amherst, Emory, UNC Charlotte, Zoom)"
tags: ["AI", "Agent", "평가", "Harness", "코딩 에이전트", "컨텍스트 관리", "SWE-bench", "Terminal-Bench", "논문"]
summary: "harness를 통째로 비교하는 대신 실행 루프를 고정하고 계획·액션 공간·컨텍스트 관리 세 부품만 갈아끼워 176개 설정을 돌렸다. 컨텍스트 관리의 가치는 대부분 '창 넘침으로 인한 조기 종료'를 막는 데서 나오고, 계획은 약한 모델에겐 정확도 보조재·강한 모델에겐 비용 절감재로 역할이 바뀐다."
---

> **원문:** [An Empirical Study of Harness Design for Coding Agents](https://arxiv.org/abs/2609.20804) — Run-Ze Fan 외 8인 (UMass Amherst, Emory University, UNC Charlotte, Zoom Video Communications), arXiv:2609.20804v1, 2026-09-17
>
> 아래는 원문을 읽고 한국어로 정리한 노트다. 수치와 표현은 원문 기준이며, 자세한 내용은 원 논문을 참고.

## 왜 이 논문인가

어제 정리한 [HarnessTax 노트](/compendium/notes/harnesstax/)는 Claude Code·Codex CLI·Pi라는 **완성된 harness들**을 통째로 비교했다. 이 논문은 정확히 그 접근의 한계에서 출발한다. 완성품끼리 비교하면 성능 차이가 계획 때문인지, 도구 설계 때문인지, 컨텍스트 관리 때문인지, 아니면 모델과의 상호작용 때문인지 구분되지 않는다.

그래서 저자들은 실행 루프(ReAct)를 고정한 가벼운 harness를 직접 만들고 세 부품만 독립적으로 갈아끼운다 — 계획(planning), 액션 공간(action space), 컨텍스트 관리(context management). 나머지(워크스페이스 접근 제어, 편집 후 진단, 정체 감지)는 모든 실험에서 고정.

## 실험 구성

- 모델 4종: Nemotron-3 30B / 120B / 550B와, 다른 계열인 Mistral-Medium-3.5-128B. SGLang으로 로컬 서빙, temperature 0.
- 벤치마크 2종: SWE-Bench Verified(500개 실제 GitHub 이슈)와 Terminal-Bench 2.1(89개 커맨드라인 과제). 지표는 성공률과 과제당 평균 비용(OpenRouter 가격 기준).
- 설정 176개: 컨텍스트 관리 5단계(T0-T4) × 컨텍스트 창 예산 4종(32k/64k/96k/128k) = 모델-벤치마크 쌍당 20개, 여기에 계획 on/off와 액션 공간 ablation 2개를 더해 22개 × 4모델 × 2벤치마크.
- 통계: 과제 단위로 짝지은 결과에 양측 정확 McNemar 검정, Benjamini-Hochberg로 FDR 0.05 통제.

컨텍스트 관리는 세 가지 조합 가능한 메커니즘으로 분해된다.

- M1 생략(elision) — 오래된 도구 관찰값의 본문을 짧은 stub으로 대체
- M2 회수(recall) — 생략한 내용을 파일 시스템에 저장하고 `recall_event` 도구로 원문을 다시 꺼내 볼 수 있게 함 (생략을 되돌릴 수 있게 만드는 무손실 장치)
- M3 요약(summarization) — 너무 오래된 메시지를 누적 요약문으로 접음

T0은 아무것도 안 함, T1=M1, T2=M1+M2, T3=M3, T4=셋 다. T4는 두 개의 임계값을 쓴다. 히스토리가 soft 임계($B_1$, 사용 가능 창의 0.6)를 넘으면 중간 영역의 덩치 큰 관찰값을 생략하고, hard 임계($B_2$, 0.85)를 넘으면 가장 오래된 중간 이벤트를 요약한다. 시스템 프롬프트와 최초 과제 설명, 그리고 최소 2턴 이상의 최근 창은 원문 그대로 유지.

## 발견 1 — 컨텍스트 관리의 가치는 창이 좁을수록 커진다

관리 티어(T1-T4)와 무관리(T0)의 성공률 격차를 모델 평균으로 보면, 창이 넓어질수록 꾸준히 줄어든다.

| 컨텍스트 창 | SWE-Bench 격차 | Terminal-Bench 격차 |
|---|---|---|
| 32k | 35.7%p | 9.5%p |
| 64k | 15.9%p | 7.5%p |
| 96k | 5.5%p | 4.8%p |
| 128k | 2.7%p | 2.8%p |

이 격차의 정체는 명확하다. T0의 창 넘침(overflow) 실패율이 SWE-Bench에서 78.7% → 8.7%, Terminal-Bench에서 61.0% → 12.1%로 떨어지는 곡선과 격차 곡선이 나란히 간다. 반면 **관리 티어는 모든 예산에서 넘침 실패가 0건**이다.

즉 컨텍스트 관리는 에이전트를 똑똑하게 만드는 게 아니라, 창이 빡빡할 때 궤적이 조기에 잘려 나가는 것을 막아 준다. 궤적 분석도 같은 말을 한다 — 32k에서 관리를 켜면 중앙값 궤적 길이가 20-30턴에서 50-180턴으로 늘어나고, 단계(localize → fix → verify) 구성 비율은 거의 그대로다. 행동을 바꾸는 게 아니라 **실행을 연장**하는 것.

## 발견 2 — T4(생략 먼저, 요약은 나중)가 비용 대비 가장 낫다

T1-T4의 성공률은 서로 비슷한데, T4가 8개 모델-벤치마크 패널 중 7개에서 가장 싸다. 네 가지 창 예산 모두에서 평균 비용도 T4가 최저.

이유는 최대 컨텍스트 점유율과 메커니즘 호출 횟수에서 드러난다. 32k에서 T1·T2는 여전히 창을 거의 꽉 채우는 반면 T3·T4는 눈에 띄게 낮게 유지한다. 그리고 T4는 T3보다 M3(LLM 요약 호출)를 모든 예산에서 덜 부른다. 싼 생략으로 먼저 처리하니 비싼 요약 호출까지 갈 일이 줄어드는 것이다.

## 발견 3 — 무손실 회수(M2)는 만들어 놔도 안 쓴다

T1과 T2는 M2 유무만 다르므로 깔끔한 대조군이다. 32개 비교에서 T2가 T1보다 나은 경우 15, 나쁜 경우 14, 동률 3이고 평균 차이는 **-0.36%p**다.

실제 사용량을 보면 더 분명하다. T2·T4 설정 64개 중 36개(56.3%)는 `recall_event`를 **한 번도 부르지 않는다**. 과제당 호출 수 평균은 32k에서 0.540이다가 64k·96k·128k에서 0.069, 0.011, 0.007로 떨어지고, T4/128k의 계획·액션 공간 ablation 16개 설정에서는 회수 호출이 아예 0이다. 그나마 쓰는 것도 거의 Nemotron-3 30B이고, 가장 많이 쓴 조합(30B, Terminal-Bench, 32k, T2)조차 T1보다 3.37% 낮은 점수를 받았다.

되돌릴 수 있게 만드는 장치는 기계 장치만 늘리고, 모델은 그 문을 열지 않는다.

## 발견 4 — 계획은 약한 모델에겐 정확도, 강한 모델에겐 비용

T4/128k에 전체 도구를 켠 상태에서 계획만 on/off로 비교한다.

- Nemotron-3 30B: SWE-Bench +11.6%p, Terminal-Bench +4.5%p. 단, 비용은 양쪽 다 증가(Terminal-Bench 기준 약 75%).
- Nemotron-3 120B: 일관된 성공률 이득 없음. SWE-Bench는 비용 증가, Terminal-Bench는 감소(약 26%).
- Nemotron-3 550B / Mistral: 양쪽 벤치마크에서 비용 감소. SWE-Bench 기준 각각 약 30%, 32% 절감에 성공률은 2.0%p, 0.4%p 하락.

궤적을 보면 같은 "계획"이 모델에 따라 정반대로 작동하는 이유가 보인다. 30B는 계획을 끄면 SWE-Bench 중앙값 궤적이 40턴에서 **5턴**으로 쪼그라들고, 68.6%의 실행이 파일을 한 번도 고치지 못한 채 끝나며 58.4%가 탐색(localize) 단계에서 멈춘다. 계획을 켜면 각각 27.8%, 10.4%. 계획이 이 모델에게 해 주는 일은 추론의 질 향상이 아니라 **첫 편집 시도까지 버티게 해 주는 것**이다.

반대로 550B는 계획을 켜면 중앙값이 108턴 → 74턴, Mistral은 68턴 → 53턴으로 줄어든다. 줄어든 구간은 대부분 탐색이나 수정이 아니라 **편집 후 검증(verification)**이다. 강한 모델에게 계획은 "언제 멈춰도 되는지"를 알려 주는 장치에 가깝다.

## 발견 5 — 미리 정의된 도구 vs bash 하나

전체 도구 세트(read_file, write_file, edit_file, list_files, glob_files, grep_text, web_fetch, bash)와 bash만 남긴 인터페이스를 비교한다.

- Nemotron-3 30B: 도구 세트가 SWE-Bench +15.0%, Terminal-Bench +10.1%. bash-only에서는 학습 때 익힌 도구 호출 패턴을 그대로 뱉는데 등록된 도구가 없어 실행으로 이어지지 못한다. Terminal-Bench에서 bash-only 궤적의 66%가 이런 인터페이스 밖 호출 뒤 종료되고, 평균 궤적이 71턴에서 15턴으로 줄어든다.
- Nemotron-3 120B: 이득이 SWE-Bench 1.6%, Terminal-Bench 4.5%로 축소. 대신 실행이 효율적이 된다(SWE-Bench 101턴 → 77턴).
- Nemotron-3 550B: **bash-only가 더 낫다.** 성공률 SWE-Bench +3.6%, Terminal-Bench +5.6%에 비용은 각각 53%, 30% 감소. 호출 수도 32%, 24% 적다. 여러 단계를 하나로 묶은 조밀한 셸 명령을 쓰기 때문이다.
- Mistral: 과제 유형이 경계선을 만든다. SWE-Bench에서는 전체 도구가 +23.2%인데 Terminal-Bench에서는 bash-only가 +6.7%. 실제로 이 모델은 Terminal-Bench 작업 액션의 71.9%를 bash로 처리하는 반면 SWE-Bench에서는 40.4%다. 셸 중심 과제일수록 경쟁하는 도구를 치우는 쪽이 맞아떨어진다.

편집 단위도 달라진다. bash-only에서는 이미 고친 파일을 다시 손보는 re-patch가 줄고(550B 기준 4.6 → 1.5), 한 번에 쓰는 편집 줄 수가 커진다(550B 18줄 → 54줄). 파일을 통째로 새로 쓰는 비중도 올라간다.

다만 대가도 있다. Mistral의 bash-only SWE-Bench 실행 중 32.8%가 파일을 한 번도 편집하지 못하고 끝난다(전체 도구에서는 1.2%).

## 정리하면

세 부품 모두 "좋다/나쁘다"로 답할 수 있는 게 아니라 **조건부**라는 것이 이 논문의 핵심 주장이다.

- 컨텍스트 관리 → 컨텍스트 예산이 결정한다. 창이 넉넉하면 한계 이득이 작다.
- 계획 → 모델 능력이 결정한다. 약하면 정확도, 강하면 비용.
- 액션 공간 → 모델의 bash 숙련도와 과제 유형이 결정한다.
- 무손실 회수 → 대체로 안 쓴다.

harness 설계는 기능을 더 넣는 문제가 아니라 모델과 예산에 맞춰 부품을 고르는 문제다. HarnessTax가 "복잡한 harness에 돈을 더 내고 있을지 모른다"고 바깥에서 관찰했다면, 이 논문은 그 복잡도의 어느 부품이 언제 값을 하는지를 안에서 뜯어본 셈이다.

## 인용

```
@misc{fan2026harnessdesign,
  title  = {An Empirical Study of Harness Design for Coding Agents},
  author = {Fan, Run-Ze and Zhang, Zihao and Ma, Simin and Hu, Yebowen and Wang, Shouju
            and Song, Kaiqiang and Liu, Fei and Zamani, Hamed and Wang, Xiaoyang},
  year   = {2026},
  eprint = {2609.20804},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url    = {https://arxiv.org/abs/2609.20804},
}
```
