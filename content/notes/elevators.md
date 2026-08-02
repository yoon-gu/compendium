---
title: "엘리베이터: 버튼을 눌렀는데 왜 오지 않을까"
date: 2026-08-02
draft: false
source_url: "https://john.fun/elevators"
author: "John Herrick"
tags: ["Engineering", "Simulation", "Algorithms", "Statistics"]
summary: "엘리베이터 dispatch는 단순히 가장 가까운 차를 보내는 문제가 아니라, traffic pattern, wait-time distribution, p90 tail, re-optimization, destination dispatch의 flexibility tradeoff가 얽힌 scheduling 문제다. 이 글은 원문의 interactive simulation을 텍스트 중심으로 옮기며 SCAN/LOOK, Otis RSR, destination dispatch가 어떤 조건에서 달라지는지 정리한다."
---

> **원문:** [Elevators](https://john.fun/elevators) — John Herrick, 게시일 미표기
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 원문은 interactive simulation과 inline SVG demo가 핵심이므로, 상단에 원문 simulation을 iframe으로 함께 넣었다. 본문 번역에는 거대한 inline image data나 generated SVG를 그대로 덤프하지 않았다.

## Interactive simulation

원문의 핵심은 글 중간중간 삽입된 elevator simulation이다. 아래 embed에서 원문 simulation을 직접 조작할 수 있다. `flow`, `floors`, `cars`, traffic pattern, LOOK/RSR/Destination Dispatch 선택을 바꾸며 wait-time metric과 histogram이 어떻게 변하는지 확인해 보자.

<div class="compendium-iframe-wrap" style="position:relative; width:100%; height:min(86vh, 920px); min-height:680px; margin:1.25rem 0; border:1px solid var(--border); border-radius:12px; overflow:hidden; background:var(--entry);">
  <iframe src="/compendium/simulations/elevators/" title="Elevators interactive simulation by John Herrick" loading="eager" allow="fullscreen" style="position:absolute; inset:0; width:100%; height:100%; border:0;"></iframe>
</div>

작은 화면이나 embed가 제대로 뜨지 않는 환경에서는 [원문 simulation을 새 창에서 열기](https://john.fun/elevators)를 권한다.

![Elevators social preview](https://john.fun/metadata/elevator/twitter-card.png)

누구나 도무지 오지 않는 엘리베이터를 기다리며 답답해한 적이 있다. “버튼을 눌렀는데 왜 안 오는 거지?”라고 묻게 된다. 엘리베이터는 너무 흔한 물건이라 단순해 보이지만, 실제로는 겉보기보다 훨씬 복잡하다.

이 글에서는 엘리베이터의 수수께끼를 풀어 본다. 우리가 버튼을 누르는 방식, 그리고 엘리베이터가 우리의 버튼을 누르는 방식까지.

## One Car

가장 단순한 엘리베이터 algorithm은 SCAN이라고 부르며, 1961년에 특허가 등록되었다. 엘리베이터는 lobby에서 시작해 맨 위층까지 올라간 뒤 방향을 바꿔 다시 내려온다. 이동 경로 위에 있는 사람은 태우고 내려준다.

대부분의 경우 실제로 꼭 **최상층**까지 갈 필요는 없다. 엘리베이터가 요청된 가장 높은 층까지만 올라간 뒤 방향을 바꾼다면, 이 algorithm은 LOOK algorithm이라고 부른다. 사람들이 대체로 알고 있고 기대하는 방식이 바로 이것이다.

원문 demo에서는 “add five calls” 버튼으로 여러 호출을 추가하면서 LOOK이 요청된 최상층까지만 움직이고 되돌아오는 모습을 보여 준다.

## Multiple Cars

여기서부터 수수께끼가 시작된다. 엘리베이터가 여러 대라면, 각 car는 누가 누구를 태울지 어떻게 조율할까?

가장 기본적인 system에는 중앙 scheduler가 있고, 각 엘리베이터에 어느 층에 멈출지 알려 준다. 새 요청이 들어오면 가장 가까운 엘리베이터에 배정한다. 하지만 곧 보겠지만, 이보다 더 잘할 수 있다.

## Long Waits

엘리베이터 algorithm이 얼마나 좋은지는 어떻게 측정할까? 가장 obvious한 metric은 엘리베이터가 도착할 때까지 기다리는 시간이다.

아주 단순한 측정 기준은 “엘리베이터가 30초 안에 도착하는 비율은 얼마나 되는가?” 또는 “90초 안에 도착하는 비율은 얼마나 되는가?”다.

원문 simulation은 passenger flow를 분당 14명 수준으로 바꿔 가며 `wait < 30s`, `wait < 90s` 같은 지표가 어떻게 움직이는지 보여 준다.

## Applied Stats

더 엄밀하게는 wait time의 **distribution**을 봐야 한다. 수천 번의 ride에 대해 wait time을 plot하면 histogram을 얻는다.

p90이 2분이라는 것은 90%의 경우 rider가 엘리베이터를 2분 이하로 기다린다는 뜻이다. p50이 1분이라는 것은 절반의 경우 엘리베이터가 1분 안에 도착한다는 뜻이다.

사람들은 보통 자신이 평균적으로 얼마나 기다렸는지를 기억하지 않는다. 엘리베이터가 **영원히** 안 오는 것 같았던 순간, 즉 p90 case에 집착한다.

## Morning Rush

모든 passenger traffic이 같은 것은 아니다. 큰 corporate office building을 상상해 보자. 아침에는 거의 모든 traffic이 lobby에서 upper level로 올라가는 trip에 지배된다.

저녁에는 모두가 건물을 떠나면서 이 흐름이 반대로 뒤집힌다. 점심 rush는 양쪽이 조금씩 섞이고, 나머지 traffic은 대체로 floor-to-floor 이동이다.

원문은 Morning, Lunch, Evening, Interfloor pattern을 바꿔 가며 wait-time distribution이 크게 달라지는 것을 보여 준다. 엘리베이터가 마주하는 time-of-day traffic pattern에 따라 wait statistics는 극적으로 바뀐다. Morning rush는 악명 높게도 가장 나쁜 wait statistics를 만든다.

## Smarter Elevators

LOOK elevator algorithm을 분석할 때, rider를 car에 어떻게 배정하는지 살펴보았다. 지금까지는 각 요청을 가장 가까운 car에 순진하게 배정했지만, 더 잘할 수 있다고 말했다.

가장 가까운 car가 이미 가득 차 있다면 어떨까? Otis의 RSR(Relative System Response) algorithm을 쓰면 더 똑똑해질 수 있다. RSR은 각 car가 passenger를 태우기에 얼마나 적합한지 점수화한다. 점수는 낮을수록 좋다.

RSR pickup score는 다음 항목들을 합성한다.

```text
Score
= ETA to pickup
+ onboard load penalty
+ same-direction anti-bunching penalty
- direction-match bonus
- idle-nearby bonus
- low-load bonus
```

Anti-Bunching은 다른 car가 이미 같은 방향으로 같은 층을 향하고 있다면 해당 car에 penalty를 준다. Idle Nearby는 caller와 두 층 이내에 있는 idle car에 reward를 준다.

RSR은 5초마다 다시 최적화한다. elevator A가 태우기로 되어 있던 passenger도 elevator A가 지연되면 elevator B로 reroute될 수 있다. 이 re-optimization이 traffic flow를 매끄럽게 만드는 핵심으로 드러난다.

원문 graphic에서는 3층에서 버튼이 바로 그 순간 눌렸다면 어떤 엘리베이터가 가장 좋은 선택인지 각 elevator가 빛나며 보여 준다. elevator가 움직이면서 최적 선택이 계속 바뀌고, optimizer가 실제로 움직이는 모습을 볼 수 있다.

## LOOK vs RSR

엘리베이터 분석 toolkit을 갖췄으니, LOOK과 RSR의 performance를 benchmark해서 더 똑똑한 elevator algorithm이 wait time을 얼마나 개선하는지 볼 수 있다.

흥미롭게도 flow rate가 높아질수록 LOOK이 오히려 RSR을 앞서기 시작한다. 엘리베이터가 항상 가득 차 있고 거의 모든 층에 멈추는 상황에서는 추가 rule의 효과가 그만큼 줄어든다.

LOOK은 elevator bank당 car 수가 적은 작은 building에서도 RSR보다 나은 경향이 있다. 때로는 단순하게 유지하는 편이 더 낫다.

추적할 수 있는 또 다른 metric은 journey time, 즉 엘리베이터 안에서 실제 목적지에 도착할 때까지 기다리는 시간이다. RSR과 LOOK은 이 지점에서도 서로 다른 특성을 갖지만, 그것은 이 글의 범위를 벗어난다.

## Destination Dispatch

모든 엘리베이터 안에 버튼이 있는 것은 아니다. 일부 최신 엘리베이터에는 각 층에 kiosk가 있어서 엘리베이터가 도착하기 전부터 어느 층으로 갈지 지정할 수 있다. 그러면 kiosk가 어느 elevator 앞에서 기다려야 하는지 알려 준다.

이를 Destination Dispatch라고 부른다. 언뜻 보면 훌륭해 보인다. elevator optimizer가 이제 누가 어디로 가는지에 대한 완전한 지식을 갖게 되었으니, wait time을 줄이는 데 쓸 수 있지 않을까?

하지만 이런 멋진 kiosk는 일반적으로 전통적인 up/down button보다 wait time이 더 나쁜 것으로 나타난다. 물론 kiosk가 이기는 edge case도 있다. 예컨대 elevator bank당 car가 8대 이상인 매우 높은 building에서는 유리할 수 있다. 그러나 대부분의 경우에는 단순한 up/down button이 우세하다.

이 counterintuitive한 결과는 모두 5초마다 system이 각 elevator의 path를 다시 최적화하는 rebalancing step 덕분이다. kiosk는 rigidity를 강제한다. 사용자는 **배정된** elevator에 반드시 타야 한다.

엘리베이터를 호출한 지 30초 뒤의 world state는 처음과 매우 달라졌을 수 있지만, system은 그 변화에 적응하지 못한다. 결국 optimizer가 추가 정보를 얻는 이점보다 flexibility를 잃는 손실이 더 크다.

## Full Sim

원문 끝에는 모든 button과 knob를 조작할 수 있는 simulation이 있다. Morning, Lunch, Evening, Interfloor traffic pattern을 바꾸고, floors, cars, flow를 조정하며, LOOK, RSR, Destination Dispatch를 비교할 수 있다. histogram도 함께 볼 수 있다.

상단 iframe에서도 simulation을 스크롤하며 조작할 수 있고, 더 넓은 화면으로 parameter를 움직여 보려면 [원문 Full Sim](https://john.fun/elevators)을 직접 여는 것이 좋다.

## Conclusion

이 글은 elevator algorithm의 표면만 살짝 긁은 것이다. 다음에 엘리베이터를 기다리다 답답해지더라도 너무 개인적으로 받아들이지는 말자. 엘리베이터는 당신의 요청을 들었다. 다만 생각해야 할 것이 많을 뿐이다.

## Practitioner notes

- 이 글은 elevator dispatch를 scheduling/optimization 문제로 보여 준다. “가장 가까운 car”라는 greedy heuristic은 이해하기 쉽지만, load, direction, bunching, idle position, re-optimization이 들어오면 성능이 달라진다.
- 평균 wait time보다 p90 같은 tail metric이 사용자 경험을 더 잘 설명한다. 사람은 평균 대기시간보다 “정말 오래 기다린 경험”을 더 강하게 기억한다.
- Destination Dispatch는 정보량을 늘리지만 flexibility를 줄인다. optimizer에 정보를 더 주는 것이 항상 좋은 것은 아니며, re-optimization이 중요한 system에서는 binding decision이 오히려 손실이 될 수 있다.
- Traffic regime이 바뀌면 optimal policy도 바뀐다. Morning rush, evening down-peak, lunch mixed traffic, interfloor traffic을 같은 distribution으로 보면 dispatch algorithm의 실제 성능을 오판하기 쉽다.
- 원문의 interactive simulation은 시스템 설계에서 “algorithm intuition → metric 정의 → distribution 확인 → edge case 비교”로 이어지는 설명 방식의 좋은 예다.
