---
title: "Cerebras가 internal Knowledge Base를 구축한 방법"
date: 2026-07-15
draft: false
source_url: "https://www.cerebras.ai/blog/how-we-built-our-knowledge-base"
author: "Isaac Tai, Daniel Kim, Mike Gao, Cerebras"
tags: ["AI", "Knowledge Base", "RAG", "Search", "MCP", "Agent Infrastructure"]
summary: "Cerebras는 Slack, wiki, code repository, incident, custom database를 하나의 embeddings table과 retrieval interface로 연결해 하루 15,000개 이상의 internal question을 처리하는 Knowledge Base를 구축했다. 핵심은 source별 behavior를 바꾸지 않고 data가 존재하는 곳에서 직접 ingest한 뒤, Slack distillation, code embedding, RRF/rerank, MCP/Web UI, project-scoped search를 조합하는 것이다."
---

> **원문:** [How We Built Our Knowledge Base](https://www.cerebras.ai/blog/how-we-built-our-knowledge-base) — Isaac Tai, Daniel Kim, Mike Gao, Cerebras, 2026-07-15
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. RAG, embeddings, retrieval, reranking, MCP, planner, executor, synthesis 같은 practitioner term은 English를 기본으로 유지했다.

Cerebras 직원들은 internal knowledge base에 매일 15,000개가 넘는 질문을 던진다. 출시 3개월 만에 회사에서 가장 널리 채택된 internal tool 중 하나가 되었고, human, automation, agent가 모두 사용하고 있다.

Cerebras의 team은 data center operations, chip design, hardware, training, inference, cloud platform 등 여러 영역에서 일한다. 매년 수백 명의 새 직원이 합류하면서 communication channel에는 같은 질문이 반복해서 쌓이고 있었다.

> “X는 어디서 찾을 수 있나요?”
>
> “Y의 expert는 누구인가요?”
>
> “Z는 무엇인가요?”

Cerebras는 사람과 system이 유용한 information에 연결되도록 돕기 위해 Cerebras Knowledge를 만들었다.

![Internal knowledge base stack](/compendium/images/cerebras-knowledge-base/figure-01.svg)

## Meeting data where it lives

Organization 내부에서 information을 찾는 일은 어렵다. Data는 여러 tool에 흩어져 있고, 분기마다 누군가는 같은 훌륭한 fix를 제안한다. 모든 information을 한곳에 모으기 위해 모든 것을 하나의 platform에 기록하자는 것이다. 그러나 single source of truth라는 꿈은 실제로는 거의 작동하지 않는다.

Information은 편하고 ergonomic한 곳에서 생성된다. Document의 suggested edit, Slack thread, GitHub의 code reference, Jira의 status metadata가 그렇다. 이런 platform은 각자의 domain에 맞게 tailor-made되어 있고, 수년의 product engineering과 analytics를 거쳐 optimize되어 있다. Google Docs에서 pull request를 논의하는 것은 끔찍한 경험일 것이다.

그래서 Cerebras는 기존 behavior를 거의 바꾸지 않아도 되는 system을 설계하기로 했다. Data collection 측면에서는 각 platform에서 data를 직접 extract한다는 뜻이었다.

## Anatomy of a knowledge base

Cerebras의 knowledge base는 세 가지를 제공한다.

1. Internal data를 collect하고 store하는 platform.
2. 그 data를 query하는 platform.
3. Authentication과 authorization을 enforce하고 auditing과 analytics를 제공하는 layer.

Core에는 여러 source의 embeddings, raw summary, metadata를 담는 단일 Postgres table이 있다. System은 company 전반에서 data를 지속적으로 ingest하고, query-ready datastore를 유지한다.

Cerebras는 단순하면서도 대부분의 data form에 적용할 수 있는 data interface를 원했다. 또한 Cerebras의 다른 developer가 custom connector를 만들 수 있기를 원했다. 결과는 의도적으로 단순하다. Slack thread부터 netlist까지 모든 source는 같은 embeddings table에 들어가고, 그 table에 들어온 것은 모두 같은 interface로 즉시 query할 수 있다.

![Many data sources feeding one queryable embeddings table](/compendium/images/cerebras-knowledge-base/figure-02.svg)

각 data source는 data가 무엇인지, 어떻게 connect하는지, 얼마나 자주 fetch해야 하는지를 정의한다. 생성된 embedding row는 Slack, code repository, document system, custom database 중 어디에서 왔든 같은 interface를 따른다.

## Slack

Slack은 Cerebras가 가장 중요하게 설계해야 했던 data source였다. 회사 전반에서 가장 최신 engineering discussion이 벌어지는 곳이 Slack이기 때문이다.

![Slack event flow from Socket Mode through distillation and embedding](/compendium/images/cerebras-knowledge-base/figure-03.svg)

## How we process unstructured Slack conversations

처음에는 raw text에 대한 simple embeddings만으로 충분히 잘 동작하는지 시험했다. 그러나 vector search만으로는 모든 relevant data를 match하기에 부족하다는 것을 빠르게 깨달았다.

Slack message에는 몇 가지 challenge가 있다.

- Information density가 크게 다르다. “hey yeah sure mike”와 detailed kernel explanation은 둘 다 message다.
- Message length가 다양하고, cosine similarity에서는 짧은 message가 더 길고 자세한 message보다 자주 이긴다.
- Message의 meaning은 주변 conversation에 의존하는 경우가 많다.

따라서 hybrid approach가 필요했다. Cerebras는 각 technique이 다른 technique의 약점을 보완하도록, 모든 thread가 여러 search technique으로 동시에 retrievable하게 Slack ingestion을 만들었다.

- Full-text search는 embeddings가 뭉개기 쉬운 exact token을 잡는다. Error string, flag name, host name이 여기에 해당한다. Engineer가 literal error message를 붙여 넣었을 때는 exact lexical match가 거의 항상 가장 좋은 evidence이며, 어떤 semantic similarity도 이를 밀어내서는 안 된다.
- Embedding search는 paraphrase를 잡는다. “restore hangs after manifest load”라고 묻는 사람과 “checkpoint stalls on the NFS mount”라고 답한 사람은 vocabulary를 전혀 공유하지 않을 수 있다. Vector similarity가 서로 다른 단어로 쓰인 question과 answer를 연결한다.[^1]
- Inverse document frequency는 signal과 filler를 분리한다. Obscure config flag 같은 rare token을 중심으로 한 짧은 message는 rank될 가치가 있다. 반면 “sounds good, thanks!”는 embedding space에서는 많은 query와 가까울 수 있지만, term rarity를 고려하면 score가 거의 0에 가깝다.
- Age decay는 Slack answer가 expire된다는 사실을 encode한다. 두 thread가 같은 question에 답할 수 있고, 6개월 전 thread는 더 이상 존재하지 않는 infrastructure를 설명할 수 있다. Relevance가 같다면 더 새로운 thread가 이긴다.

No single scorer is trusted on its own. 각 technique은 같은 corpus에 대해 자기 ranked view를 만들고, 그 view들은 query time에 fusion된다. 이 내용은 Reranking section에서 다시 다룬다.

## Socket Mode

Real-time으로 data를 collect하기 위해 Cerebras는 Slack bot을 workspace에 설치하고 Socket Mode로 실행했다. Slack은 persistent WebSocket을 통해 모든 message event를 push한다. 따라서 Web API를 polling하면서 rate limit을 소모하지 않고도 real-time update를 받을 수 있다.

Event가 도착하면 system은 즉시 acknowledge하고, stable event ID를 사용해 deduplicate한 뒤, message를 ingest consumer 대상으로 mark한다.

Ingest consumer는 새 message 하나만 따로 저장하지 않는다. 그 message가 속한 thread를 resolve하고, parent와 모든 reply를 포함한 전체 conversation을 Slack API에서 다시 fetch한다. 그런 다음 thread 전체를 하나의 row로 다시 쓴다. 따라서 기존 thread에 reply가 붙으면 parent와 sibling 전체를 다시 pull하므로, stored content, participant list, last-activity timestamp는 항상 complete conversation을 반영한다.

System의 모든 Slack channel은 각자의 data source를 가진다. 이렇게 하면 data freshness를 세밀하게 tuning할 수 있다. 예를 들어 team은 busy incident channel을 더 자주 ingest하도록 선택할 수 있다.

## Threads and messages

Raw Slack text는 landing 즉시 keyword-searchable하다. Raw content 위에 Postgres full-text GIN index를 유지하기 때문이다. 그러나 useful vector search를 위해서는 추가 processing이 필요하다.[^8]

Distillation 중에 LLM은 full thread에서 structured data를 extract한다.

- Engineer가 실제로 search할 법한 one-line question.
- Short summary.
- Resolution.
- Mention된 system과 code reference.

```json
{
  "question": "Why does restore stall after manifest load?",
  "summary": "Large restores stop before cache warmup.",
  "resolution": "Set CKPT_PREFETCH=4 for the NFS mount.",
  "systems": ["checkpoint restore", "NFS"],
  "code_refs": ["CKPT_PREFETCH"]
}
```

Cerebras는 이 data point들을 embed하고 shared embeddings table에 쓴다. Original transcript 자체를 직접 embed하지는 않는다. Experiment에서 thread를 consistent format으로 normalize했을 때 accuracy가 크게 증가했다.[^7][^9] 추가 metadata도 semantic match에 더 useful한 signal을 제공한다.

## Bursting

이 시점에서 Slack search는 좋았지만, long thread 내부의 important message가 thread-level summary에 항상 반영되지는 않는다는 문제가 계속 나타났다.

Individual message의 signal을 높이기 위해 Cerebras는 bursting을 사용한다. Burst는 같은 author가 연속해서 쓴 message run이다. 때로 answer는 thread summary에 들어가지 않는 tangent message 하나에 있고, 그 message의 vocabulary가 thread summary에 전혀 들어가지 않을 수 있다. 따라서 thread topic을 context로 prepend한 뒤 individual burst를 embed한다.[^2] Burst embedding은 그런 message를 독립적으로 findable하게 만든다.

Low-signal data가 database에 들어가지 않도록, 각 burst는 weighted signal combination으로 score를 받고 threshold를 넘어야 embed된다.

- Corpus 전체에서 비교적 rare token을 포함하고, IDF가 최소 4.0 이상이다.
- Combined burst가 최소 200 characters 이상이다.
- Burst 안의 하나 이상의 message에 reaction이 있어 social boost를 제공한다.

![A Slack thread split into same-author bursts and filtered by signal](/compendium/images/cerebras-knowledge-base/figure-04.svg)

Distillation 이후 qualifying burst는 embed되어 thread-level record와 함께 embeddings table에 저장된다.

## Code repositories

처음에는 code repository를 embed하는 것이 필요한지 논의가 있었다. Claude Code와 다른 command-line tool이 부상하면서, “grep is all you need”처럼 보이는 상황에서 code embedding을 만드는 것은 counterintuitive하게 느껴졌다. 그러나 industry의 다른 사람들과 이야기하고, large codebase에서 semantic search에 대한 Cursor의 finding을 읽은 뒤 시도하기로 했다.

Cerebras에는 internal repository가 많고, 그중 일부는 40GB보다 크다. 가장 큰 concern은 이들을 어떻게 효율적으로 current하게 유지할 것인가였다.

## Using CocoIndex to maintain code embeddings

여러 experiment 끝에 Cerebras는 codebase vectorization에 특화된 open-source document embedding framework인 CocoIndex를 선택했다.

각 repository에 대해 language-specific regex boundary를 coarse-to-fine 순서로 사용해 code를 split한다. Splitter는 class 같은 higher-level boundary를 먼저 시도한다. 생성된 chunk가 여전히 너무 크면 method boundary로 fallback하고, 그다음 더 작은 block으로 fallback한다. 생성된 chunk를 embed하고 vector를 Postgres에 쓴다. 하나의 file은 file-level record와 function-level record처럼 서로 다른 specificity level의 embedding을 여러 개 만들 수 있다.

CocoIndex는 synchronization metadata를 Postgres에서 track한다. Commit마다 전체 repository를 다시 compute하는 대신 changed code chunk만 re-embed하고 re-export한다. Synchronization state와 embedding store가 같은 database에 있기 때문에 Cerebras에서는 특히 잘 맞았다.

Codebase 수가 늘어나면서 Cerebras는 repository onboarding을 team이 직접 submit할 수 있는 configuration file로 옮겼다. 여기에는 file-path level의 allowlist와 denylist가 포함된다.

## Custom data sources

일부 team은 이미 자체 database를 가지고 있었고, knowledge base에 참여하기 위해 data를 Slack이나 document system으로 옮기고 싶어 하지 않았다. 이들은 기존 table 위에서 같은 query surface를 원했다.

이를 지원하기 위해 Cerebras는 custom source를 plugin script로 취급한다. Team은 자기 system에서 read하고 embeddings table과 같은 shape의 row를 emit하는 작은 Python module과 matching data source entry를 pull request로 제출한다.

Script가 다른 모든 embedding row와 같은 schema로 shared database에 write하기만 하면, 나머지 stack은 바뀌지 않고 동작한다. Data는 Slack, code, document와 함께 queryable해지고, system의 다른 곳에서 특별한 handling이 필요하지 않다.

## Planning and tool fan-out

모든 query에 대해 system은 먼저 short planning pass를 실행한다. 여기서 LLM은 어떤 tool과 data source가 relevant할지 결정한다. 주요 tool은 다음과 같다.

- `subsystem_index`: per-file LLM summary.
- `search`: Slack, wiki, code, 기타 indexed source 전반의 unified vector pipeline. 내부적으로 merge와 rerank를 수행한다.
- `search_slack`: direct Slack retrieval.
- `search_code`: source repository 위의 ripgrep.
- `recent_prs`: question과 relevant한 recent pull request.
- `who_knows`: 특정 topic에 demonstrated expertise가 있는 사람.

Planner는 무엇이 index되어 있는지에 대한 compact description 위에서 동작한다. 어떤 project가 있고, 각 project에서 어떤 source를 사용할 수 있으며, 각 source가 어떤 question에 답하는 데 좋은지 설명한 것이다. User query와 active scope가 주어지면 planner는 tool selection을 emit하고, executor는 이를 parallel로 fan-out한다. 그런 다음 result를 common evidence format으로 normalize하고 final synthesis LLM에 전달한다.[^4]

![Planner, parallel tool execution, evidence normalization, and synthesis](/compendium/images/cerebras-knowledge-base/figure-05.svg)

## Reranking

Document는 query와 vocabulary를 공유한다는 이유만으로 top 근처에 나타날 수 있지만, 실제로는 다른 question에 답하고 있을 수 있다. Reranking 전에 Cerebras는 reciprocal rank fusion, 즉 RRF로 서로 incompatible한 retriever result list를 combine한다. 각 document에 대해 등장한 list마다 `weight / (60 + rank)`를 더한다. Default weight는 1.0이고 smoothing constant는 60이다.

```text
score(d) = Σ 1 / (60 + rank_l(d))  |  K = 60
```

Smoothing constant는 single strong vote보다 consensus를 더 중요하게 만든다. 여러 retriever에서 상위에 나타나는 document는 하나의 retriever에서만 1등인 document를 이길 수 있다. 이후 duplicate chunk를 하나의 source로 다시 merge하고, file 하나가 contribute할 수 있는 result 수를 cap해서 더 diverse한 top 20을 얻는다.

Cerebras는 original query와 candidate들을 small reranker model에 보낸다. Model은 각 document에 0부터 10까지 score를 주고, system은 top 10만 유지한다.[^6]

Ranking이 확정되면 winner에 context를 다시 추가한다. 예를 들어 wiki section이 match되면 neighboring section 두 개를 함께 가져와서, chunking 때문에 분리된 heading, precondition, caveat가 사라지지 않도록 한다. 이렇게 하면 reader는 중요한 context가 빠진 lonely paragraph가 아니라 complete snippet을 보게 된다.

따라서 search의 output은 rich packet of evidence다. 여러 retriever에서 fused되고, source level에서 deduplicate되고, actual question에 대해 rerank된 다음, 그제야 surrounding context로 expanded된 result다.

## MCP

MCP integration에서는 retrieval building block을 하나의 “answer this question” endpoint 뒤에 숨기지 않고 direct tool로 expose한다. 이 tool들은 client가 빠르고 저렴하게 query할 수 있도록 의도적으로 단순하고 가능한 한 LLM-free하게 설계되어 있다.[^5]

각 MCP tool은 `search_slack`, `search_code`, `search`, `who_knows` 같은 underlying retrieval primitive 하나에 대응한다. Tool input과 output은 narrow, structured, stable하므로, tool 자체에 추가 orchestration logic을 embed하지 않고도 어떤 client나 agent에서 쉽게 호출할 수 있다.

대부분의 tool은 vector search, lexical search, ripgrep 같은 하나의 query pipeline을 실행하고, lightweight scoring heuristic을 적용한 뒤 raw evidence row를 반환한다.

Claude Code 또는 MCP-compatible agent는 orchestration engine이 된다. 어떤 tool을 어떤 순서로 call할지, result를 final answer나 code edit으로 어떻게 assemble할지 결정한다. Retrieval layer 자체는 request를 serve하기 위해 그런 LLM decision에 의존하지 않는다.

## Web UI

Web UI에도 같은 tool이 있지만, 모든 user question에 대해 end-to-end로 실행되는 complete query pipeline에 연결되어 있다. UI agent가 planner와 executor step을 담당한다.

- Planner: lightweight LLM pass가 query와 active project를 inspect한 뒤 `search`, `search_slack`, `subsystem_index` 같은 어떤 retrieval tool을 invoke할지 선택한다.
- Executor: system은 tool call을 parallel로 fan-out하고, result를 모은 뒤 score, recency, source hint가 포함된 shared evidence schema로 normalize한다.
- Synthesis: final LLM pass가 typed evidence bundle과 original question을 받아, citation, caveat, cross-source synthesis를 포함한 UI answer를 생성한다.

User 관점에서 Web UI는 단순히 “question을 묻고 answer를 받는” 것이다. Under the hood에서는 MCP client가 명시적으로 재현할 수 있는 planner → executor → synthesizer pattern을 실행한다.

![MCP exposes retrieval primitives while the web UI runs the complete agent pipeline](/compendium/images/cerebras-knowledge-base/figure-06.svg)

## Organization

Corpus가 커지면서 “search everything everywhere”는 빠르게 유용하지 않게 되었다. Compiler team engineer는 infrastructure runbook이 result에 섞이기를 원하지 않고, 반대도 마찬가지다. Project는 search를 default로 relevant하게 만드는 방식이다.

## Projects and scoped search

Cerebras는 project를 query가 실행되는 workspace를 organize하는 기본 방식으로 도입했다. Project는 특정 team이나 initiative와 관련된 data source 묶음이다. 예를 들어 특정 Slack channel, code repository, internal database, document space가 들어간다.

Project는 의도적으로 lightweight하다. Shared incidents channel이나 central platform repository 같은 같은 data source는 duplicate하지 않고 여러 project에서 reference할 수 있다.

![Projects reference shared data sources without duplicating them](/compendium/images/cerebras-knowledge-base/figure-07.svg)

## Onboarding and defaults

Onboarding 중 user는 ML training infrastructure, Compiler, Data Center Operations처럼 자신의 일하는 방식에 맞는 default project를 선택하거나 생성하도록 prompt된다.

이 default project는 user profile에 저장되고 query scope를 자동으로 제한한다. 새 engineer는 어떤 Slack channel, repository, document space가 중요한지 먼저 배울 필요 없이 high-signal answer를 얻을 수 있다.

## Final Thoughts

결국 knowledge base가 작동하는 이유는 모든 것을 하나의 rigid system으로 강제하지 않고, information이 이미 존재하는 곳에서 사람들을 만났기 때문이다. 여러 search technique을 combine함으로써 evidence를 빠르게 surface할 수 있다. 그 결과 Cerebras가 계속 성장해도 real company data에 충분히 flexible하면서, 유용성을 유지할 만큼 structured한 search experience가 만들어졌다.

## Practitioner 관점에서 읽을 포인트

이 글은 enterprise RAG/knowledge base를 “vector DB 하나 붙이기”가 아니라 organization workflow를 존중하는 retrieval infrastructure로 설계해야 한다는 점을 잘 보여준다.

1. Single source of truth를 강요하지 않는다. Slack, code, wiki, incident, custom DB가 각자 잘하는 일을 유지하게 두고, ingestion과 retrieval layer가 그 위를 연결한다.
2. Slack retrieval은 raw embedding만으로는 부족하다. Full-text, embedding, IDF, age decay, LLM distillation, bursting을 함께 쓰고, query time에 fusion해야 실제 engineering discussion을 찾을 수 있다.
3. Code search도 grep과 semantic search의 역할을 분리한다. `ripgrep`은 exact lookup에 강하고, CocoIndex 기반 code embedding은 paraphrase와 structural similarity를 보완한다.
4. RRF + rerank + context expansion은 production search 품질의 핵심이다. Retriever별 score를 그대로 믿지 않고, consensus를 만들고, reranker로 질문 적합성을 재평가한 뒤, 주변 context를 복원한다.
5. MCP integration과 Web UI는 같은 retrieval primitive를 다르게 expose한다. MCP는 LLM-free raw evidence tool에 가깝고, Web UI는 planner/executor/synthesis를 포함한 complete agent pipeline이다.
6. Project-scoped search는 enterprise adoption에 중요하다. “모든 것을 검색”하는 것보다 team의 default workspace를 설정해 high-signal answer를 주는 편이 새 직원에게 훨씬 유용하다.

## References

[^1]: Malkov and Yashunin, *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs*, arXiv:1603.09320 / IEEE TPAMI 2018.
[^2]: Anthropic, *Introducing Contextual Retrieval*, 2024.
[^3]: Cormack, Clarke, and Büttcher, *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods*, SIGIR 2009.
[^4]: Li et al., *Search-o1: Agentic Search-Enhanced Large Reasoning Models*, arXiv:2501.05366, 2025.
[^5]: Anthropic, *Code Execution with MCP*, 2025.
[^6]: Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, arXiv:2307.03172, 2023.
[^7]: Anthropic, *Use XML Tags*.
[^8]: Salesforce/Slack Engineering, *How Slack AI Processes Billions of Messages*.
[^9]: Improving Agents, *Best Nested Data Format*.
[^10]: Cursor, *Improving Agent with Semantic Search*, 2025.
