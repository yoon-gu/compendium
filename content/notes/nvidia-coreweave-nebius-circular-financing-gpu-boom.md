---
title: "Nvidia, CoreWeave, Nebius와 GPU 붐의 순환 금융"
date: 2026-07-13
draft: false
source_url: "https://io-fund.com/ai-stocks/nvidia-coreweave-nebius-circular-financing-gpu-boom"
author: "Beth Kindig, I/O Fund"
tags: ["AI", "GPU", "Nvidia", "CoreWeave", "Nebius", "AI Infrastructure"]
summary: "I/O Fund는 CoreWeave와 Nebius 같은 neocloud가 hyperscaler의 AI compute 수요를 흡수하며 급성장하고 있지만, capex와 operating cash flow의 mismatch를 debt, Nvidia equity, GPU-backed financing으로 메우고 있다고 분석한다. 특히 Nvidia가 투자자, GPU 공급자, 잔여 capacity backstop 역할을 동시에 하는 구조가 GPU boom의 circular financing risk를 만든다는 점을 짚는다."
---

> **원문:** [Nvidia, CoreWeave, and Nebius: Inside the Circular Financing of the GPU Boom](https://io-fund.com/ai-stocks/nvidia-coreweave-nebius-circular-financing-gpu-boom) — Beth Kindig, I/O Fund, 2026-06-12
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 투자 조언이 아니라 원문 분석의 한국어 번역·정리이며, 원문의 재무 수치와 risk framing을 그대로 보존했다.

## 핵심 요약

- Neocloud는 hyperscaler들이 AI infrastructure를 빠르게 scale하려는 과정에서 막대한 demand를 받고 있으며, 그 결과 revenue와 backlog가 빠르게 늘고 있다.
- CoreWeave와 Nebius 같은 leader는 최신 Nvidia GPU에 빠르게 접근하고 compute utilization을 optimize하는 능력을 통해 이 demand를 가능하게 한다.
- 그러나 hyperscaler demand 뒤의 bearish argument는 hyperscaler가 capex spending을 밖으로 밀어내고 cost를 operating expense line으로 옮기려 한다는 점이다.
- CoreWeave와 Nebius의 growth는 아직 profitable하지 않다. 두 회사는 limited cash flow와 soaring debt load, 점점 어려워지는 macro backdrop 속에서 AI demand를 잡으려 한다.
- Nvidia의 investment와 financial backstop으로 드러나는 circular financing은 면밀히 monitor해야 할 또 하나의 핵심 risk다.

Neocloud는 AI business model 중 가장 논쟁적인 영역 중 하나이며, CoreWeave와 Nebius가 가장 널리 알려진 두 이름이다. 이 회사들은 sales, backlog, share price가 급등했다. 차별화의 핵심은 최신 GPU compute에 빠르게 접근하고, hyperscaler가 efficient compute capacity를 빠르게 추가할 수 있도록 GPU utilization advantage를 제공한다는 점이다.

CoreWeave와 Nebius는 각각 3.5GW의 contracted power capacity를 확보했다. Data center expansion에서 power가 병목이라는 점을 고려하면 이 power footprint는 중요하다. 다만 대부분의 contracted power capacity는 아직 online 상태가 아니다. CoreWeave는 2026년 말까지 1.7GW의 active power를 목표로 하고, Nebius는 800MW-1GW의 connected power를 목표로 한다.

따라서 두 회사는 contracted power를 active power로 전환하고, 큰 backlog를 revenue로 전환하기 위해 빠르게 움직이고 있다. 문제는 이 과정이 극도로 비싸며, neocloud가 Big Tech와 같은 cash나 operating cash flow profile을 갖고 있지 않다는 점이다. 그 결과 neocloud는 독특하고 circular한 financing structure를 사용하고 있으며, 이는 red flag를 만든다.

이 분석은 Nvidia equity, hyperscaler contract, GPU-backed debt를 타고 buildout을 fund하는 두 public neocloud를 다루며, 이 surge의 durability에 무엇을 의미하는지 살핀다.

## Microsoft와 Meta의 120B 달러 이상 neocloud 베팅

Hyperscaler-neocloud partnership의 규모는 이들의 현재 revenue와 비교하면 매우 크다. Microsoft는 CoreWeave, Nebius, Nscale 같은 private player를 포함해 약 [60B 달러의 commitment](https://www.datacenterdynamics.com/en/news/microsofts-neocloud-spending-surpasses-60bn/)를 맺으며 가장 많은 neocloud deal을 체결했다. Meta는 최근 [21B 달러 expansion](https://coreweave.com/news/coreweave-and-meta-announce-21-billion-expanded-ai-infrastructure-agreement) 이후 CoreWeave에 총 35.2B 달러를 commit했고, Nebius와는 최대 [27B 달러 deal](https://nebius.com/newsroom/nebius-signs-new-ai-infrastructure-agreement-with-meta)을 맺어 총 commitment가 최대 62.2B 달러에 달한다. Meta와 함께 OpenAI도 CoreWeave의 두 largest customer 중 하나이며, CoreWeave는 Anthropic과도 [multi-year compute agreement](https://www.coreweave.com/news/coreweave-announces-multi-year-agreement-with-anthropic)를 보유한다.

Microsoft와 Meta만 합쳐도 total commitment는 최대 122.2B 달러다. 비교를 위해 말하면, 이는 AWS의 TTM revenue의 약 90%에 해당하는 금액이 long-term capacity deal 형태로 neocloud에 배정된 것이다. OpenAI와 Anthropic의 hyperscaler-backed deal까지 고려하면, 정확한 deal value가 알려지지 않았더라도 total potential commitment는 145B 달러를 넘어선다.

CoreWeave의 FY2026 estimated revenue는 12.6B 달러이고 Nebius의 FY2026 revenue는 3.4B 달러로 예상된다. 따라서 이 partnership은 current sales보다 한 자릿수 이상 큰 order of magnitude의 commitment를 만들고 있다.

Hyperscaler가 상대적으로 새로운 neocloud business model에 이렇게 많은 capital을 배정하는 이유는 세 가지다. Leading GPU generation에 대한 빠른 access, optimized compute utilization, 그리고 balance sheet에 capex를 인식하지 않아도 되는 benefit이다. 원문은 이를 차례로 살핀다.

## Neocloud advantage: GPU에 빠르게 접근하기

Neocloud demand의 근본은 hyperscaler의 compute capacity에 대한 끝없는 수요다. 그러나 neocloud는 hyperscaler의 internal build보다 훨씬 빠르게 compute capacity를 추가할 수 있어 Big Tech에 중요한 value proposition을 제공한다. Hyperscaler가 AI compute에 매년 수천억 달러를 쓰는 상황에서, data center expense와 revenue generation 사이의 lag를 줄이는 것은 return on investment를 극대화하는 데 중요하다.

Commercial real estate giant JLL도 time-to-deployment 측면의 neocloud advantage를 뒷받침한다. JLL은 “[Neocloud는 hyperscale data center의 multi-year build와 달리 몇 달 안에 high-density GPU infrastructure를 deploy할 수 있어](https://www.jll.com/en-us/insights/the-rise-of-neocloud-in-the-ai-landscape), rapid AI development가 필요한 business에 중요한 time-to-market advantage를 제공한다”고 설명한다.

CoreWeave의 S-1 Registration filing은 고객에게 제공하는 주요 benefit 중 하나로 “최신 AI infrastructure advancement에 더 빠르게 접근”할 수 있다는 점을 든다. CoreWeave는 “NVIDIA H100, H200, GH200 cluster를 AI scale production에 처음 deliver한 곳 중 하나였고, NVIDIA GB200 NVL72-based instance를 generally available로 만든 첫 cloud provider였으며, receipt 후 빠르면 2주 안에 최신 chip을 infrastructure에 deploy하고 compute capacity를 고객에게 제공할 수 있다”고 말한다.

Nebius도 [Annual Report](https://ir-api.eqs.com/feeds/sec-filing/b7ee389e-7a01-47d8-a96b-790dfe6cdfb8/detail/c349334a-1ff2-4f6f-9fa7-14a67d08cb34/convpdf?disposition=inline)에서 “최신 세대 NVIDIA GPU chip을 가장 먼저 deploy해 온 consistent track record”를 언급한다.

CoreWeave와 Nebius가 최신 GPU를 남보다 먼저 확보할 수 있는 데에는 Nvidia와의 관계가 중요하다. Nvidia는 최근 [CoreWeave](https://nvidianews.nvidia.com/news/nvidia-and-coreweave-strengthen-collaboration-to-accelerate-buildout-of-ai-factories)와 [Nebius](https://nvidianews.nvidia.com/news/nvidia-and-nebius-partner-to-scale-full-stack-ai-cloud)에 각각 2B 달러를 투자했다. 이 partnership 아래에서 CoreWeave와 Nebius는 2030년까지 각각 5GW 이상의 data center capacity deploy를 목표로 한다.

CoreWeave는 6월 초 [Nvidia Vera Rubin NVL72 system을 가장 먼저 가동](https://www.datacenterdynamics.com/en/news/coreweave-claims-to-have-first-nvidia-vera-rubin-nvl72-up-and-running/)했다고 밝히며 최신 chip과 architecture에 빠르게 접근하는 능력을 다시 보여주었다. 이는 CoreWeave와 Nebius와의 partnership이 hyperscaler가 가능한 한 많은 최신 GPU compute에 단기간 접근하도록 도울 수 있다는 evidence다.

## Hardware를 넘어: neocloud platform의 더 높은 GPU utilization

Raw compute access 외에도 CoreWeave와 다른 neocloud는 GPU utilization을 개선하는 software와 capability를 추가한다. 이는 hyperscaler에게 중요한 value add다.

예를 들어 CoreWeave Kubernetes Service(CKS)는 수천 개 GPU에 걸친 workload allocation을 coordinate한다. SUNK service는 training workload와 inference workload가 같은 cluster에서 실행되도록 하여 GPU utilization을 optimize한다. CoreWeave Tensorizer는 high-speed model loading을 가능하게 해 GPU idle time을 줄인다.

CoreWeave는 이런 software 및 optimization capability와 rapid fault detection/remediation service를 결합하면 hyperscaler보다 더 높은 GPU utilization rate를 제공할 수 있다고 본다. 기준 metric은 model FLOPs utilization(MFU)이다. “MFU gap”은 compute capacity와 실제 usage 사이의 gap을 설명하는 metric으로, 오늘날 30%-40% 범위인 경우가 많다.

MFU gap은 GPU performance를 더 현실적으로 측정하는 방식이기 때문에 비용이 커질 수 있다. GPU가 idle인지 아닌지만 보는 것이 아니라, 실제 workload가 GPU의 maximum capability에 얼마나 가깝게 parallelize되는지를 보기 때문이다. [Trainy AI](https://www.trainy.ai/blog/gpu-utilization-misleading)는 “GPU Utilization은 특정 시점에 kernel이 실행 중인지 여부만 측정한다. 그 kernel이 사용 가능한 모든 core를 쓰는지, workload를 GPU maximum capability까지 parallelize하는지는 알려주지 않는다”고 설명한다.

![AI model FLOPS utilization gap](https://images.prismic.io/bethtechnology/aitn7alQnVZVEPHK_AIEfficiencyGap%E2%80%93ModelFLOPSUtilizationvsTheoreticalMaximum-100%25vs35%E2%80%9345%25-.png?auto=compress,format&q=90&max-w=1000?w=3840)

*Chart: theoretical model FLOPS utilization 100%와 observed performance 35%-45%를 비교해 AI workload의 efficiency gap을 보여준다. Source: [CoreWeave](https://coreweave.com/blog/coreweave-leads-the-charge-in-ai-infrastructure-efficiency-with-up-to-20-higher-gpu-cluster-performance-than-alternative-solutions).*

상장 당시 CoreWeave는 MFU rate가 35%-45%이며 competitor보다 20% 높다고 밝혔다. 이는 다른 AI data center의 MFU rate가 30%대에 가깝다는 뜻이다. 그러나 2025년 3월 blog post에서 CoreWeave는 Hopper GPU에서 [50% 초과 MFU](https://coreweave.com/blog/coreweave-leads-the-charge-in-ai-infrastructure-efficiency-with-up-to-20-higher-gpu-cluster-performance-than-alternative-solutions)를 달성했다고 언급했다. Next-generation GPU hardware를 짧은 시간에 세우는 능력과 utilization rate 개선을 결합한 지점이 neocloud advantage의 핵심이다.

## Balance sheet 뒤편: hyperscaler가 neocloud capacity를 lease하는 이유

Hyperscaler가 neocloud에서 compute capacity를 lease하면 cost timeline이 큰 upfront capex outflow에서 long-term contract에 걸친 operating expense outflow로 이동한다. Hyperscaler의 막대한 spending을 고려하면 cost를 분산할 필요성은 점점 분명해지고 있다.

이는 hyperscaler가 neocloud와 협력하는 이유에 대한 “bear” case다. GPU access와 utilization 측면의 rationale과 대비해 이해해야 한다. Hyperscaler 역시 software optimization과 GPU utilization을 스스로 잘할 수 있기 때문이다. 실제로 이들은 cloud operation과 workload optimization에서 오랜 incumbent이며 깊은 expertise를 갖고 있다.

Meta를 예로 들면, analyst는 현재 Meta가 2026년에 operating cash flow 136B 달러를 생성할 것으로 예상한다. Meta의 stated capex guidance가 125B-145B 달러라는 점을 고려하면, 회사는 그해 free cash flow negative가 될 수 있다. 그런데 Meta는 최대 62.2B 달러의 neocloud agreement도 갖고 있다. Meta가 같은 value의 capacity를 직접 build했다면 그 spend는 balance sheet capex로 인식되어 이미 압박받는 free cash flow를 더 짓눌렀을 것이다.

반면 neocloud agreement는 Meta의 capex에는 아무것도 추가하지 않는다. 비용이 contract life 동안 operating expense로 인식되기 때문이다. Meta의 CoreWeave 및 Nebius contract는 2031-2032년까지 이어지므로, opex payment는 연평균 10B 달러 미만일 수 있다.

Microsoft도 비슷하다. Calendar year 2026에 Microsoft는 capex 190B 달러를 guide하고 있으며, analyst는 같은 기간 operating cash flow 200B 달러를 예상한다. 이 수치가 실현되면 Microsoft는 OCF의 95%를 capex에 쓰게 된다. 여러 해에 걸쳐 operating expense로 인식되는 60B 달러의 neocloud agreement는 capacity를 늘리면서도 해당 spend를 cash flow statement의 capex에서 벗어나게 한다.

Hyperscaler가 capex를 offload하면, 그 capex를 떠안는 쪽은 neocloud다. 이것이 neocloud의 막대한 funding need로 이어진다.

## Circular financing: investor, supplier, demand backstop으로서 Nvidia의 역할

Nebius와 CoreWeave가 가진 advantage의 일부는 Nvidia에서 나온다. GPU leader와의 partnership 덕분에 두 회사는 Blackwell Ultra, 그리고 이제 Rubin 같은 next-gen platform을 가장 먼저 stand up하고 deploy하는 provider가 될 수 있다.

Nvidia가 partner라는 사실은 CoreWeave와 Nebius가 훨씬 좋은 조건으로 funding을 확보하는 데에도 역할을 할 수 있다. Hyperscaler를 넘어 strong balance sheet와 cash flow를 가진 또 다른 investment-grade firm의 presence와 support가 있기 때문이다. Nvidia의 LTM free cash flow는 119B 달러로, Apple에 이어 세계에서 두 번째로 높다. 그러나 downside는 Nvidia와 두 회사의 관계가 circular financing의 가장 식별 가능한 사례 중 하나라는 점이다.

이는 Nvidia가 CoreWeave와 Nebius에 해 온 multi-billion-dollar investment에서 비롯된다. 특히 Nvidia가 최근 각 회사에 2B 달러를 투자한 것이 처음도 아니다. Nvidia의 Q1 2025 13F filing은 당시 [896.7M 달러 규모의 CoreWeave stake](https://13f.info/manager/0001045810/cusip/21873S108)를 보여주었고, Q4 2025 13F는 [Nebius 33M 달러 stake](https://13f.info/13f/000104581025000013-nvidia-corp-q4-2024)를 보여주었다. Nvidia와 이들 회사의 investment relationship은 1년을 훨씬 넘는다.

CoreWeave의 경우 Nvidia는 unsold GPU capacity에 대해 상당한 [financial backstop](https://www.sec.gov/Archives/edgar/data/1769628/000176962825000047/crwv-20250909.htm)도 제공했다. Initial value가 6.3B 달러인 agreement에 따르면, “[CoreWeave의] datacenter capacity가 자체 customer에 의해 완전히 사용되지 않는 경우 NVIDIA는 2032년 4월 13일까지 잔여 unsold capacity를 purchase할 obligation이 있다.” 다시 말해 CoreWeave가 다른 buyer를 찾지 못하면 Nvidia가 unsold GPU capacity를 구매하기로 commit한 것이다. Initial value가 6.3B 달러라는 점에서, arrangement가 시간이 지나며 더 커질 가능성도 있다.

Nvidia가 이런 investment를 하면, CoreWeave와 Nebius는 다시 Nvidia로 돌아가 대량의 GPU를 구매한다. 이는 circular financing의 명확한 표현이다. Nvidia는 비교적 작은 equity funding을 제공함으로써 수십B 달러 규모의 GPU를 구매하려는 neocloud와의 relationship을 확보한다.

Nvidia는 cash flow가 깊게 negative인 ramp-up phase에서 CoreWeave와 Nebius를 지원함으로써 long-term benefit을 얻을 수 있다. 두 회사가 결국 self-sustainable해진다면 Nvidia는 최신 system을 앞으로도 수년간 판매할 large-scale customer 두 곳을 확보한다. 그러나 neocloud 입장에서는 revenue가 capex를 2:1로 lag하는 상황에서, new infrastructure를 build하기 위해 계속 cash를 raise해야 하는지, 그리고 그 필요가 언제 level out될지가 concern이다.

## Neocloud가 AI expansion을 fund하는 방식: debt, equity, circular financing

CoreWeave와 Nebius는 active power를 빠르게 ramp하려 한다. CoreWeave는 현재 3.5GW contracted power pipeline 중 1GW가 active지만, 2027년 말까지 그 majority를 active capacity로 전환하려 한다. Nebius도 3.5GW contracted power를 갖고 있으며, 2026년 말까지 최대 1GW의 connected power(active이거나 GPU installation 후 activate 가능)를 목표로 한다.

하지만 현재 모든 AI buildout에서 keyword는 “active power”다. Energy constraint가 전반적으로 심화되고 있기 때문이다.

## CoreWeave: 압박받는 balance sheet와 빠르게 증가하는 debt

CoreWeave의 balance sheet는 어려운 위치에 있다. 회사는 cash balance와 operating cash flow가 뒷받침하지 못하는 속도로 active power footprint를 빠르게 확장하려 한다.

최근 분기 revenue는 2.08B 달러로 YoY 112% 증가했다. 그러나 operating cash flow(OCF)는 2.98B 달러였고 capex는 7.7B 달러에 달해 free cash flow는 -4.71B 달러가 되었다. 이 mismatch로 cash balance는 QoQ 890M 달러, 즉 28.3% 감소해 2.27B 달러가 되었다. 반면 debt는 거의 3.5B 달러, 즉 QoQ 16.1% 증가해 24.86B 달러가 되었다. Q2에는 CoreWeave가 6월 11일 3.5B 달러 senior note raise를 발표했기 때문에 debt가 더 늘어날 예정이다.

![CoreWeave capex vs revenue growth](https://images.prismic.io/bethtechnology/aitoNalQnVZVEPHR_CoreWeaveCapexvsRevenueGrowth%E2%80%93RisingAIInfrastructureSpendingOutpacesRevenue.png?auto=compress,format&q=90&max-w=1000?w=3840)

*Chart: CoreWeave의 quarterly capex가 약 7.7B 달러까지 급증하는 반면 revenue는 같은 기간 약 2.07B 달러에 도달했음을 보여준다. Source: [YCharts](https://go.ycharts.com/io-fund).*

Full year 기준으로 CoreWeave는 capex 31B-35B 달러, midpoint 33B 달러를 예상한다. 이는 올해 남은 기간 capex spend가 25.3B 달러라는 뜻이다. Analyst는 CoreWeave가 2026년에 operating cash flow 8.68B 달러, 즉 올해 남은 기간 5.7B 달러를 생성할 것으로 추정한다. CoreWeave의 2.27B 달러 cash balance를 고려하면 17.33B 달러의 큰 funding gap이 생긴다. 실제로는 이미 얇아진 cash cushion을 더 줄이지 않기 위해 이보다 더 많이 raise할 가능성이 높다.

CoreWeave는 과거 equity issuance도 funding source로 사용했지만 debt issuance가 훨씬 크다. 상장 후 첫 다섯 번의 earnings report를 보면 total equity issuance는 3.5B 달러에 불과한 반면 debt issuance는 18.81B 달러로 5배 이상 높다. 따라서 CoreWeave가 이미 -22.6B 달러의 net cash position을 가진 상태에서 capex plan을 fund하기 위해 debt를 더 늘릴 가능성이 높다. Unique funding structure를 들여다보면 debt가 계속 핵심 lever가 될 것임을 알 수 있다.

## Nebius: 더 강한 balance sheet지만 계속되는 funding need

Nebius는 상대적으로 훨씬 나은 위치에 있다. Cash 9.37B 달러, debt 8.45B 달러로 net cash balance는 920M 달러다. 최근 분기 revenue는 YoY 684% 증가한 339M 달러였고, operating cash flow는 customer prepayment 증가 덕분에 QoQ 170.7% 증가한 2.26B 달러였다. Capex는 2.47B 달러였고 FCF는 -214.9M 달러였다.

하지만 Nebius도 active power footprint를 빠르게 확장하려 한다. Full year capex guidance의 midpoint는 22.5B 달러다. 이는 올해 남은 기간 20B 달러의 spending을 의미한다. 회사의 cash와 약 6.9B 달러의 contractual commitment를 포함해도 Nebius는 capex forecast midpoint를 뒷받침하기 위해 6.3B 달러의 추가 funding을 draw해야 한다.

CoreWeave와 마찬가지로 Nebius도 debt를 equity issuance보다 더 많이 사용해 funding했다. 다만 정도는 덜하다. Q4 2024 이후 Nebius의 total equity issuance는 Nvidia가 최근 구매한 2B 달러의 pre-funded warrant를 포함해 약 3.92B 달러였다. 같은 기간 debt issuance는 8.32B 달러였다. 최신 earnings call에서 Nebius는 capital raising option으로 asset-backed financing, corporate debt, equity issuance를 언급했다.

Nebius의 미사용 25M share at-the-market equity program은 2026 funding gap을 메우는 데 꽤 도움이 될 수 있다. Share price 200달러, 즉 현재 stock level보다 약 10% 낮은 가격을 가정하면 program을 전부 활용해 gross proceeds 5B 달러를 만들 수 있고 shareholder dilution은 약 8%다. 그러나 과거 trend를 고려하면 asset-backed debt와 corporate debt가 주요 경로가 될 가능성이 높다.

전체적으로 CoreWeave와 Nebius의 2026 funding requirement breakdown은 contracted power를 active power로 전환하려는 훨씬 큰 push의 한 단계일 뿐이다. 이 spending 이후에도 CoreWeave는 contracted power의 50% 미만, 즉 1.7GW만 active로 만들 계획이다. Nebius가 connected power target의 upper bound에 도달해도 contracted power의 30% 미만에 해당한다. 여기서 connected power는 active이거나 GPU가 install되면 activate 가능한 power를 포함한다.

따라서 두 회사는 CFO가 capex에 수렴할 때까지 scale을 위해 점점 더 많은 funding을 찾아야 한다. 두 수치 사이의 spread가 아직 매우 넓기 때문에, 결과적으로 여러 해 동안 debt load 증가나 shareholder dilution이 이어질 가능성이 높다.

## GPU-backed debt: CoreWeave의 AI infrastructure funding engine

CoreWeave는 GPU-backed delayed draw term loan(DDTL)에 크게 의존하며, 여섯 개 separate facility를 닫았다. DDTL 아래에서 CoreWeave는 data center buildout의 여러 stage를 pay하기 위해 필요할 때마다 fund를 draw down한다.

특히 3월에 closed된 8.5B 달러 DDTL 4.0은 [investment-grade credit rating](https://s205.q4cdn.com/133937190/files/doc_presentations/2026/Mar/2026-03-DDTL-4-Overview.pdf)을 받은 첫 사례다. 2026년 Q1 기준 CoreWeave는 DDTL 4.0 중 1.26B 달러만 draw했다. 현재 CoreWeave의 total debt에 표시되는 것은 이 1.26B 달러뿐이다. 따라서 시간이 지나며 DDTL 4.0을 더 많이 draw down할수록 debt도 증가한다.

![CoreWeave debt obligations](https://images.prismic.io/bethtechnology/aitoyalQnVZVEPH__CoreWeaveDebtBreakdownQ12026%E2%80%93DDTLFacilities%2CInterestRates%2CandTotalDebt.png?auto=compress,format&q=90&max-w=1000?w=3840)

*Table: CoreWeave의 Q1 2026 debt structure를 보여준다. Multiple DDTL facilities와 senior notes를 포함해 total debt는 약 25.1B 달러다. DDTL 4.0 facility는 총 8.5B 달러지만 1.26B 달러만 draw된 상태라, capital deployment에 따라 future debt expansion 여지가 크다. Source: [CoreWeave](https://d18rn0p25nwr6d.cloudfront.net/CIK-0001769628/c7e9d028-08c1-4ee3-b84d-e4b3993a63ff.pdf).*

CoreWeave는 investment-grade rating이 “investment-grade AI enterprise와의 long-term customer contract에 의해 support된다”고 설명한다. 이는 아마 Meta의 최신 contract와 연결되어 있을 것이다. 본질적으로 CoreWeave가 investment-grade customer와 체결한 contract와, CoreWeave가 구매하는 GPU의 value가 debt의 collateral이 된다. CoreWeave 자체의 balance sheet가 좋지 않음에도 facility가 investment-grade credit rating을 받을 수 있었던 이유가 여기에 있으며, CoreWeave는 otherwise 받을 수 없었을 훨씬 유리한 interest rate를 얻는다.

다만 CoreWeave가 peer보다 더 좋은 interest rate를 받을 수 있는 능력은 investment-grade customer contract의 backing에 의존한다. 5월에 closed되어 위 table에는 포함되지 않은 DDTL 5.0은 두 개의 non-investment-grade customer contract에 의해 backed되었다. 그 결과 이 facility는 investment-grade rating을 받지 못했고 interest rate도 더 높았다.

## Interest rate pressure: profitability에 커지는 risk

일반 rate의 상승은 CoreWeave와 다른 neocloud가 future funding round에서 받을 수 있는 rate에 추가적인 upward pressure를 가한다. DDTL 4.0의 fixed-rate tranche는 average weighted maturity가 3.14년인 U.S. Treasury에 2% premium을 더한 구조다. Yield curve의 이 구간은 올해 초 3.6% 미만에서 거의 4.2%까지 크게 상승했다.

![3-year U.S. Treasury yield trend in 2026](https://images.prismic.io/bethtechnology/aitoeqlQnVZVEPHk_3-YearU.S.TreasuryYieldTrendin2026%E2%80%93RisingRatesImpactAIInfrastructureFinancing.png?auto=compress,format&q=90&max-w=1000?w=3840)

*Chart: 3-year U.S. Treasury rate가 2026년 초 3.6% 미만에서 6월 약 4.16%까지 상승한 모습을 보여준다. Source: [YCharts](https://go.ycharts.com/io-fund).*

CoreWeave의 interest payment는 이미 elevated 상태다. Q1 interest payment는 536M 달러로, 2.08B 달러 revenue의 25.8%, 1.157B 달러 adjusted EBITDA의 46.3%에 해당한다. 회사는 다음 분기 midpoint revenue를 2.525B 달러, midpoint interest expense를 690M 달러로 guide하고 있다. 이는 interest-to-revenue ratio를 27.3%까지 밀어 올릴 수 있다. Interest expense는 이미 profitability에 큰 압박을 주고 있으며, 앞으로 더 중요한 line item이 될 것으로 보인다.

## Neocloud race: 급증하는 AI demand와 debt, circular risk의 균형

전체적으로 neocloud는 분명한 growth momentum을 갖고 있다. Revenue와 backlog가 급증하고 있으며, Microsoft와 Meta 같은 investment-grade hyperscaler와 OpenAI, Anthropic 같은 AI lab의 관심도 끌고 있다. Leading Nvidia system에 접근하는 능력과 GPU utilization advantage는 neocloud를 AI compute capacity를 빠르게 scale하려는 hyperscaler의 option으로 만든다.

동시에 operating cash flow와 capex 사이의 mismatch는 debt level을 빠르게 높이고 있으며, 이 dynamic은 near term에 바뀌기 어렵다. Elevated interest rate는 external risk로 남아 있다. Circular financing은 neocloud growth가 Nvidia의 capital support에 얼마나 의존하는지, 그리고 Nvidia의 GPU demand가 neocloud model에 얼마나 더 연결되고 있는지에 대한 질문을 만든다.

원문 말미에서 I/O Fund는 Q2가 마무리되는 시점에 upcoming **Top 15 AI Stocks for Q3 2026** report에서 다음 AI winner wave를 식별할 준비를 하고 있다고 설명한다. Coverage는 AI networking, memory, energy, custom silicon, 그리고 다음 leg of the trade를 이끄는 infrastructure bottleneck 전반을 포함한다.

원문의 disclosure도 중요하다. I/O Fund는 회사 portfolio를 위해 research를 수행하고 conclusion을 도출한 뒤 이를 reader에게 공유하며 real-time trade notification을 제공한다고 밝힌다. 이는 stock performance의 guarantee가 아니며 financial advice가 아니므로, 언급된 회사 주식을 매수하기 전 개인 financial advisor와 상담해야 한다. Beth Kindig와 I/O Fund는 작성 시점에 NVDA share를 보유하고 있으며 chart에 표시된 stock을 보유할 수 있다. Leo Miller는 이 analysis에 기여했으며 NVDA와 META share를 보유하고 있다.
