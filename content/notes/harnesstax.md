---
title: "HarnessTax: coding agent에서 harness는 얼마나 중요한가"
date: 2026-09-18
draft: false
source_url: "https://harnesstax.github.io/"
author: "Melissa Z. Pan, Shuo Yang, Negar Arabzadeh, Wei-Lin Chiang, Ion Stoica, Matei Zaharia (UC Berkeley, Arena)"
tags: ["AI", "Agent", "평가", "Harness", "벤치마크", "코딩 에이전트", "SWE-bench", "Terminal-Bench"]
summary: "7개 모델 × 3개 harness(Claude Code, Codex CLI, Pi) 21쌍을 SWE-bench Lite와 Terminal-Bench 2.0에서 비교했다. harness를 바꿔도 성공률은 거의 그대로인데 비용은 최대 5배까지 벌어진다 — 눈에 띄지 않게 새어 나가는 이 차액이 'harness tax'다."
---

> **원문:** [HarnessTax: How Much Does the Harness Matter for Coding Agents?](https://harnesstax.github.io/) — Melissa Z. Pan, Shuo Yang, Negar Arabzadeh, Wei-Lin Chiang, Ion Stoica, Matei Zaharia (UC Berkeley Sky Lab, Arena), 2026-09-16
>
> 아래는 원문을 한국어로 정리한 노트다.

## 한 줄 요약

코딩 에이전트(coding agent)를 고른다는 것은 모델과 harness를 함께 고르는 일인데, 벤치마크 두 개에서 재어 보니 harness는 성공률을 거의 바꾸지 못하고 **비용만 바꿨다**. 같은 품질에 더 내고 있다면 그것이 harness tax다.

## 무엇을 어떻게 쟀나

- 대상: 7개 모델 × 3개 harness = 21개 모델-harness 쌍. harness는 Claude Code, Codex CLI, 그리고 최소 구성 오픈소스 harness인 Pi.
- 벤치마크: SWE-bench Lite와 Terminal-Bench 2.0에서 각각 무작위 추출한 30개 과제. 과제당 3회 반복 시도.
- 설정: 각 harness의 기본 설정에서 출발해 high effort 옵션을 켜고, 한 시도당 100 agent turn으로 상한을 둠. 성공 판정은 각 벤치마크의 공식 평가기.
- 비용: 2026년 9월 1일자 direct API 가격표를 고정해 토큰 비용을 계산 — 같은 모델이면 harness가 달라도 동일 단가. 신뢰구간은 부트스트랩(bootstrap) 10,000회.
- 통제: SWE-bench Lite에서는 컨테이너 외부 네트워크를 차단하고 Claude Code/Codex의 기본 웹 도구를 껐다.

## 발견 1 — harness는 정확도보다 비용을 바꾼다

Claude Fable 5의 SWE-bench Lite 성공률은 Claude Code 97.8%, Codex 96.7%, Pi 96.7%로 사실상 동률인데, 비용은 Claude Code $1.33 대 Pi $0.67로 약 두 배다.

공유 모델 전체를 비용비의 기하평균으로 보면 SWE-bench Lite에서 Claude Code는 Pi의 약 2.0배, Codex의 약 1.6배이고, Terminal-Bench 2.0에서는 Pi의 약 1.5배다. 반면 harness가 성공률에 주는 평균 효과는 SWE-bench Lite에서 ±2% 이내, Terminal-Bench 2.0에서 약 ±5% 이내에 머문다.

저자들의 처방은 단순하다. 모델 평가는 성공률만이 아니라 **널리 쓰이는 여러 harness에서의 비용과 성공률을 함께** 비교해야 한다.

## 발견 2 — 단순한 harness도 충분히 경쟁력이 있다

Pi가 제공하는 도구는 read, write, edit, bash 네 개뿐인데도 두 벤치마크 모두에서 파레토 프론티어(Pareto frontier)에 닿는다.

비용 차이가 어디서 오는지 보면, 턴 수가 아니라 턴당 지출이다. SWE-bench Lite의 Fable 5는 시도당 평균 턴이 Pi 15.4, Claude Code 15.3으로 거의 같은데 비용은 Claude Code가 약 두 배고 그 대가는 성공률 1.1%p다.

더 앞쪽, 첫 모델 호출에서 이미 차이가 시작된다. 7개 모델 전부에서 Claude Code의 초기 컨텍스트 평균은 Pi의 **10배가 넘는다** — 더 긴 지시문과 더 큰 도구 스키마(tool schema) 때문이다. 물론 총지출은 캐싱과 생성 토큰, 이후 호출에도 좌우된다.

여기서 나오는 함의는 두 갈래다. 독점 harness에 접근하지 않고도, 모델과 함께 co-training하지 않고도 오픈소스 harness 연구가 SOTA 수준에서 가능하다는 것. 그리고 풍부한 harness 기능이 다른 모델·워크로드·상호작용 환경에서는 여전히 이득일 수 있으니, harness 복잡도는 신념이 아니라 **경험적 트레이드오프**로 다뤄야 한다는 것.

## 발견 3 — 모델은 자기 harness 밖에서도 잘한다

제공사가 자사 환경에 맞춰 최적화했다고 해서 그 조합이 최선이라는 보장이 없었다. Anthropic·OpenAI 모델 6개와 벤치마크 2개, 총 12개 비교 중 **9개에서 최고 성공률은 다른 회사의 harness에서 나왔다**.

- Sonnet 4.6, SWE-bench Lite: Codex 68.9% 대 Claude Code 66.7% (비용은 비슷)
- GPT-5.6 Sol, Terminal-Bench 2.0: Pi 83.3% 대 Codex 78.9%, 비용은 $0.42 대 $0.76으로 절반 수준

모델의 능력이 특정 harness에 묶여 있지 않고 이전 가능하다는 이야기다. 남는 질문은 "어느 harness가 최고인가"가 아니라, 주어진 모델과 워크로드에서 비용과 성공률의 균형이 가장 좋은 조합이 무엇이냐다.

## 한계와 다음 단계

결과는 모델이 학습 중 접했을 수 있는 오픈소스 벤치마크 두 개에 한정된다. 다른 벤치마크와 실제 워크로드에서는 달라질 수 있다.

저자들이 보는 다음 단계는 실제 개발 워크플로에서 harness를 평가하고 그 선택을 자동화하는 것이다. 요구사항이 바뀌고, 개발자가 피드백을 주고, 과제가 세션을 넘어 이어지는 환경 말이다.

마지막 관점이 흥미롭다. 일상적인 작업에서 코딩 에이전트는 결국 모델 지능에 접근하는 인터페이스이고, 모델이 강해질수록 오늘의 scaffolding은 덜 필요해질 수 있다. 그러니 범용 코딩 에이전트는 화려한 부가 기능보다 **비용 효율과 신뢰성**을 우선해야 한다. 반대로 모델 능력의 경계에 있는 어려운 문제 — 과학적 발견 같은 — 에서는 아이디어 탐색과 후보 평가, 피드백 학습을 구조화해 주는 harness가 여전히 값을 한다. 다만 이런 설정을 사용자가 직접 고르게 해서는 안 되고, 과제가 전개되는 대로 적응하면서도 범용성을 유지하는 harness를 지향해야 한다는 것이 저자들의 결론이다.

## 인용

```
@misc{pan2026harnesstax,
  title  = {{HarnessTax: How Much Does Harness Matter for Coding Agents?}},
  author = {Pan, Melissa Z. and Yang, Shuo and Arabzadeh, Negar and Chiang, Wei-Lin and Stoica, Ion and Zaharia, Matei},
  year   = {2026},
  url    = {https://harnesstax.github.io/},
}
```

원문에는 파레토 프론티어 그래프, 누적 비용-성공 곡선, 초기 컨텍스트 비교 등 인터랙티브 차트가 함께 있으니 수치를 직접 보려면 [원문 사이트](https://harnesstax.github.io/)를 참고하는 편이 좋다. 프로파일링 트레이스도 공개 예정이라고 밝히고 있다.
