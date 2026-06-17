---
title: "로컬 모델로 Claude/GPT를 대체할 수 있는가"
date: 2026-06-17
draft: false
source_url: "https://news.ycombinator.com/item?id=48542100"
author: "Hacker News / cloudking 외"
tags: ["AI", "LLM", "Agentic Coding", "Local Models", "Hacker News"]
summary: "Hacker News의 Ask HN 토론에서 개발자들은 로컬 LLM이 일상 코딩에서 Claude/GPT를 어느 정도 대체할 수 있는지 경험을 공유했다. 대체 가능하다는 쪽은 Qwen 3.6, Gemma 4, Pi/OpenCode/llama.cpp 조합과 충분한 VRAM·메모리를 강조했고, 회의적인 쪽은 Claude Code급 추론, 컨텍스트, 하네스 완성도, 기회비용을 아직 넘기 어렵다고 보았다."
---

> **원문:** [Ask HN: Has anyone replaced Claude/GPT with a local model for daily coding?](https://news.ycombinator.com/item?id=48542100) — cloudking 및 Hacker News 댓글 참여자들, 2026년 6월 15일
>
> 아래 글은 Hacker News 토론의 질문과 댓글 흐름을 한국어로 구조화해 옮긴 것이다. 원문은 538개 댓글의 토론이므로, 전체 댓글을 기계적으로 전부 번역하기보다 주요 입장·설정·성능 수치·실패 양상을 보존하는 토론 노트로 정리했다.

## 질문

원 질문은 간단하다. “여기서 Claude/GPT를 일상 코딩의 주 도구로, 단순 실험이 아니라 실제로 로컬 모델로 완전히 바꾼 사람이 있는가? 그렇다면 설정과 성능, 예를 들어 tok/s를 공유해달라.”

토론은 1,264점, 538개 댓글 규모로 이어졌다. 댓글 전체에서 눈에 띄게 많이 언급된 단어는 Qwen, Pi, local, Claude, Mac, Gemma, llama.cpp, DeepSeek, RTX, OpenCode/Zed 등이었다. 결론은 단일하지 않다. “이미 바꿨다”는 사람도 많았고, “Claude Code/Sonnet/Opus의 기회비용을 생각하면 아직 아니다”라는 반론도 강했다.

## 한 줄 결론

로컬 모델은 이미 일부 개발자에게 주력 코딩 도구가 되었다. 다만 성공 조건은 꽤 분명하다. 대략 27B-35B급 이상의 좋은 모델, 30-150 tok/s 수준의 실사용 가능한 추론 속도, 64GB-128GB 이상의 메모리나 다중 GPU, Pi/OpenCode/llama.cpp 같은 하네스(harness), 테스트·린트·명확한 작업 분해가 함께 필요하다. 반대로 “Claude/GPT처럼 알아서 설계까지 해주는 선임 개발자”를 기대하면 실망하기 쉽다.

## 긍정 사례: 이미 대체했다

가장 강한 긍정 사례는 `Greenpants`의 댓글이다. 그는 데이터 프라이버시와 무료 사용을 이유로 Pi coding harness를 컨테이너와 샌드박스 안에서 완전 오프라인으로 실행한다고 했다. Mac Studio 128GB RAM 또는 MacBook 36GB RAM에서 Qwen3.6 35B를 쓰며, 활성 파라미터가 3B뿐이라 빠르게 동작한다고 설명했다. Django와 Wagtail 기반 웹사이트 홈·블로그 재설계까지 처리했지만, Claude Opus와 비교하면 차이를 분명히 인정했다.

그가 제시한 비유가 토론의 분위기를 잘 요약한다. 에이전트형 Qwen3.6 35B는 “전반적 지식은 있지만 많이 지도해야 하는 주니어”에 가깝고, Claude Opus는 “아키텍처를 함께 생각해주는 시니어”에 가깝다. Opus가 15배 속도 향상을 준다면, 완전 오프라인 Qwen은 5배 속도 향상 정도라는 평가다. 그래도 무료·오프라인이라는 점을 고려하면 충분히 놀랍다고 본다.

`horsawlarway`도 Claude 월 100달러 구독을 중단하고 Pi harness, Unsloth Studio, Qwen3.6-35B-A3B-MTP-GGUF, Gemma 4 26B A4B 조합으로 옮겼다고 했다. 약 5년 전 만든 dual RTX 3090 머신에서 두 모델 모두 약 150 tok/s를 얻는다고 보고했다. 그는 이것이 가장 최신 Claude급 지능이라는 뜻은 아니지만, 개인 사용에서는 비용 대비 충분히 납득 가능하다고 보았다.

`bluejay2387`은 코딩의 약 90%를 Qwen 3.6 27B와 OpenCode, custom skills, Semble로 처리한다고 했다. Claude Code나 Codex만큼 똑똑하지는 않지만 대부분의 작업에는 충분하다는 입장이다. 그는 원래 RTX 6000을 다른 작업용으로 가지고 있었기 때문에 로컬 모델을 시험해본 것이고, 결과적으로 비용·속도·통제 가능성 면에서 계속 쓰게 되었다.

`pierotofy`는 Llama.cpp + Qwen3.6-35B(MTP) + OpenCode 조합이 단일 RTX 3090에서 충분히 유능하며, 일부 cloud model보다 빠르다고 썼다. 품질은 “8-12개월 전 edge model” 정도라고 보면서도, 구체적인 설정을 공개 저장소로 공유했다.

## 회의적 입장: 아직 Claude Code의 기회비용을 이기기 어렵다

반대편에서 `codinhood`는 이 질문에 “진짜 대체했다”는 답이 많지 않을 것이라고 했다. 최신 최고 모델을 쓰지 않는 기회비용이 아직 너무 크다는 것이다. 매달 조사해도 로컬 모델과 주변 도구를 Claude Code와 Sonnet/Opus에 가깝게 맞추는 데 필요한 시간·노력·비용이 지금은 맞지 않는다는 결론에 이른다고 했다.

`Roark66`은 더 강하게 부정했다. Qwen 480B와 Kimi 같은 큰 오픈 모델까지 시도했지만 Claude에 가까이 가지 못했다고 했다. 그가 하는 일은 스크립팅, DevOps, 데이터 처리, Ansible playbook, 네트워크 장비 관리, Helm chart 수정 같은 시스템 작업인데, 이 영역에서는 Sonnet을 쓰는 편이 낫다고 평가했다.

`HappySweeney`는 Optane과 많은 RAM으로 “full-fat” 모델을 밤새 돌려 AVX512 bit-matrix transpose 함수를 작성하게 했지만, cloud model들은 쉽게 처리하는 작업을 Kimi 2.6과 GLM 5.1은 실패했다고 했다. `mitchell_h`는 짧게 “컨텍스트 윈도가 충분히 크지 않았다”고 요약했다.

이 회의론은 단순한 보수성이 아니라 워크로드 차이에서 나온다. 로컬 모델을 긍정적으로 본 사람들도 “요구사항을 매우 명확히 주고, 작은 단위로 나누고, 테스트와 검증 루프를 갖춰야 한다”고 반복했다. 즉 로컬 모델은 지시가 느슨한 one-shot vibe coding보다, 범위가 좁고 검증 가능한 작업에서 강하다.

## 많이 언급된 모델

토론에서 가장 두드러진 모델은 Qwen 3.6 계열이다. Qwen 3.6 35B-A3B, Qwen 3.6 27B dense, Qwen 3.5 122B-A10B 등이 반복적으로 등장했다. 35B-A3B는 MoE(mixture of experts, 전문가 혼합) 구조 덕분에 빠르며, 27B dense는 느리지만 정확도가 더 좋다는 평가가 있었다.

Gemma 4도 자주 언급되었다. Gemma 4 31B는 채팅, 번역, 문서 작업에 쓰인다는 댓글이 있었고, Gemma 4 26B A4B는 Qwen과 함께 코딩 후보로 등장했다. 다만 코딩 주력으로는 Qwen 쪽을 더 자주 고른다는 의견이 많았다.

DeepSeek와 Kimi는 “로컬”이라기보다는 오픈 모델 또는 선택 가능한 inference provider 관점에서 많이 언급되었다. `goranmoomin`은 로컬 GPU는 아니지만 코딩 에이전트 세션의 80% 이상을 DeepSeek v4 Pro와 Kimi K2.6 thinking 같은 open source model로 돌린다고 했다. 그에게 중요한 점은 모델뿐 아니라 inference provider를 직접 고를 수 있다는 점이었다.

## 하드웨어와 속도: 30B급 모델을 어디에 올릴 것인가

실사용 사례에서 반복되는 하드웨어는 다음과 같다.

| 설정 | 댓글에서 나온 사용 예 |
| --- | --- |
| Mac Studio 128GB 또는 MacBook 36GB | Qwen3.6 35B, 오프라인 Pi sandbox |
| dual RTX 3090 | Qwen/Gemma 계열 약 150 tok/s |
| 단일 RTX 3090 | Qwen3.6-35B + Llama.cpp + OpenCode |
| RTX 6000 / RTX Pro 6000 Blackwell | Qwen, Gemma 4 31B, DeepSeek 계열 고속 실행 |
| Strix Halo 128GB unified memory | Qwen3.6-35B-A3B, llama.cpp, Pi |
| V100 32GB | Qwen3.6-27B, 200k context window, Pi |
| Mac Studio 512GB RAM | Qwen3.6 27B dense, OpenCode, LM Studio 계열 |

속도는 하드웨어·quantization·context length·MTP 설정에 따라 크게 흔들렸다. dual RTX 3090에서는 약 150 tok/s가 보고되었고, Ada 4000 20GB VRAM에서는 Qwen 3.6 35B-A3B Q4_KM으로 약 55 tok/s가 보고되었다. 4x RTX 5070 환경에서는 Qwen3.6 27B Q6_K가 Pi daily driver로 50-60 tok/s를 낸다는 사례도 있었다. 반대로 큰 모델을 CPU/RAM 중심으로 억지로 돌리면 0.7 t/s 같은 속도도 나와, 실사용이 어렵다는 보고가 있었다.

한 가지 중요한 관찰은 “tok/s가 전부가 아니다”라는 점이다. 더 빠른 35B-A3B보다 느린 27B dense가 전체 개발 시간을 줄였다는 댓글도 있었다. 속도보다 정확도와 되돌림 횟수, edit tool 실패율, loop 발생 빈도가 전체 생산성을 좌우한다는 것이다.

## 하네스가 모델만큼 중요하다

여러 댓글은 모델 자체보다 하네스가 병목이라고 봤다. Pi, OpenCode, Zed, Aider, Copilot custom endpoint, llama.cpp, LM Studio, Ollama가 반복해서 등장했다. `blurbleblurble`은 지금 제한은 모델 자체보다 queue management, interruption, subagents, goals 같은 기능이 빠진 대체 하네스의 어색한 ergonomics라고 했다.

`Greenpants`와 `lambda`의 하위 토론은 특히 구체적이다. Pi를 컨테이너 안에서 실행하고, llama.cpp를 다른 컨테이너에서 띄우며, 작업 디렉터리와 `~/.pi` 정도만 노출하는 방식이다. 네트워크를 완전히 막거나, credential에 접근하지 못하게 하는 격리가 핵심이다.

또 다른 기술적 이슈는 prompt caching과 thinking 보존이다. Qwen hybrid model이 매 turn마다 context를 다시 처리하는 문제를 겪은 사용자가 있었고, 답변에서는 llama.cpp 최신 버전, Vulkan 사용, `preserve_thinking` 설정, append-only context 유지가 해결책으로 제시되었다. 예시 설정은 다음과 같았다.

```ini
chat-template-kwargs = {"preserve_thinking": true}
```

일부 사용자는 OpenCode처럼 system prompt를 매 turn 변경하는 하네스는 KV cache와 잘 맞지 않을 수 있다고 지적했다. 즉 로컬 모델의 체감 속도는 모델 크기나 GPU뿐 아니라, 하네스가 메시지 배열과 system prompt를 얼마나 안정적으로 유지하는지에도 크게 의존한다.

## 로컬 모델의 강점

토론에서 반복된 로컬 모델의 장점은 다음과 같다.

1. 데이터 프라이버시와 오프라인성. 외부 Claude-like service에 source code를 넣지 않아도 된다는 점이 가장 강한 동기였다. EU 조직처럼 명확한 AI 사용 규칙이 없는 환경에서는 “내 로컬 sandbox 밖으로 데이터가 나가지 않는다”는 확신 자체가 가치가 된다.
2. 비용 예측 가능성. 이미 GPU나 Mac Studio를 보유하고 있거나, 개인 사용에서 cloud subscription을 줄이고 싶은 사람에게 매력적이다. 다만 새 Mac Studio 128GB를 사야 한다면 privacy의 가격은 매우 높다는 반론도 있었다.
3. 통제 가능성. quantization, context length, provider, sandbox, tool policy, guardrail을 직접 정할 수 있다.
4. 반복 가능한 실험. 자기 워크로드에 맞는 모델·하네스·prompting 패턴을 평가하고, unit test와 lint를 붙여 실패를 빨리 감지할 수 있다.

## 로컬 모델의 약점

약점도 분명하다.

1. Claude/GPT의 최고 모델처럼 “알아서 생각하는” 능력은 부족하다. 요구사항이 모호하면 쉬운 길을 택하거나, CSS를 HTML에 직접 넣는 식의 아키텍처상 덜 좋은 선택을 할 수 있다.
2. edit tool call 실패와 loop가 잦다. 실패 후 바로 retry하기보다 파일을 다시 읽거나 thinking token을 많이 소비하는 사례가 보고되었다.
3. 컨텍스트 윈도와 cache 문제가 실무에서 치명적일 수 있다. 큰 코드베이스에서는 65k context도 부족하다는 댓글이 있었고, 200k 이상을 선호한다는 의견도 있었다.
4. 하드웨어 초기비용과 전력 비용이 있다. Gemini Flash 같은 저렴한 cloud API를 오래 써도 Mac Studio 128GB 가격에 못 미칠 수 있다는 계산도 나왔다.
5. 벤치마크만으로는 부족하다. 실제 코드베이스에서 bug finding, feature addition, refactor, test writing 같은 자기 업무에 맞춘 평가가 필요하다는 의견이 반복되었다.

## 실무적으로 보이는 성공 패턴

토론을 종합하면 로컬 모델을 일상 코딩에 쓰는 사람들은 대체로 다음 패턴을 따른다.

- 8B급 모델로 one-shot 대형 작업을 기대하지 않는다. 최소 27B-35B급에서 시작한다.
- 작업을 작게 나누고, 계획·수정·검증을 분리한다.
- unit test, lint, typecheck, deterministic harness를 적극적으로 붙인다.
- credential과 작업 디렉터리를 분리한 컨테이너 sandbox를 쓴다.
- context window와 KV cache를 직접 관리한다.
- Q8 또는 더 좋은 quantization이 느리더라도 전체 churn을 줄일 수 있음을 고려한다.
- Claude/Opus가 만든 plan을 local agent가 실행하게 하는 hybrid workflow도 사용한다.

특히 “모델만 바꾸면 된다”가 아니라 “워크플로 전체를 바꿔야 한다”는 점이 중요하다. Claude Code나 Codex의 사용감은 모델 능력, context management, 도구 호출, UI, interruption, subagent, plan mode, diff ergonomics가 합쳐진 제품 경험이다. 로컬 모델은 이 중 모델만 대체해서는 같은 경험을 내기 어렵다.

## 대표 댓글 10개

1. `Greenpants`: Pi sandbox + Qwen3.6 35B를 완전 오프라인으로 사용. Claude Opus가 시니어라면 로컬 Qwen은 많이 지도해야 하는 주니어지만, 무료·프라이버시를 감안하면 충분히 가치가 있다고 평가.
2. `horsawlarway`: Claude 월 100달러 구독을 중단하고 dual RTX 3090, Pi, Unsloth Studio, Qwen/Gemma 조합으로 약 150 tok/s를 얻음.
3. `codinhood`: 최신 Claude Code/Sonnet/Opus를 쓰지 않는 기회비용이 아직 너무 크다고 반론.
4. `bluejay2387`: Qwen 3.6 27B + OpenCode로 코딩의 90%를 처리하지만, Claude Code나 Codex만큼 똑똑하지는 않다고 인정.
5. `pierotofy`: 단일 RTX 3090에서 Llama.cpp + Qwen3.6-35B + OpenCode가 충분히 유능하고 빠르다고 보고.
6. `sosodev`: 8B로 vibe coding을 기대하면 실패하지만, 30B급 모델에 잘 정의된 작업을 주면 꽤 잘한다고 정리.
7. `Kostic`: VS Code와 llama.cpp, Qwen 3.6 27B/Gemma 4 31B를 연결해 cloud subscription을 취소할 만큼 충분했다고 평가.
8. `Roark66`: Qwen 480B와 Kimi 같은 큰 모델까지 시도했지만 DevOps·시스템 작업에서는 Claude에 못 미친다고 반박.
9. `lambda`: Strix Halo 128GB, Pi container, llama.cpp 조합을 쓰며 Qwen 3.6 35B-A3B가 코딩 sweet spot이라고 평가. prompt caching 문제에는 `preserve_thinking`과 append-only context가 중요하다고 설명.
10. `blurbleblurble`: 현재 병목은 모델보다 하네스 ergonomics라고 지적. queue management, interruption, subagents, goals 같은 기능이 중요하다는 관점.

## Compendium 관점의 해석

이 토론은 “로컬 LLM이 Claude/GPT를 완전히 대체했는가?”라는 질문에 yes/no로 답하기보다, 코딩 에이전트의 성능이 모델 하나가 아니라 시스템 전체의 함수임을 보여준다. 모델은 Qwen 3.6과 Gemma 4 수준까지 올라왔고, 소비자·워크스테이션 하드웨어에서도 30B급 모델을 쓸 수 있게 되었다. 하지만 실제 생산성은 context window, KV cache, tool call 안정성, edit 실패 복구, harness ergonomics, 테스트 루프, 보안 격리, 작업 분해 능력에 의해 결정된다.

따라서 지금의 실무적 결론은 이렇다. 비용·프라이버시·오프라인성이 중요하고, 자기 워크플로를 손볼 의지가 있다면 로컬 모델은 이미 daily coding의 상당 부분을 맡을 수 있다. 반대로 빠른 납기, 복잡한 아키텍처 판단, 큰 코드베이스 전반 이해, 낮은 운영 부담이 더 중요하다면 Claude Code/Sonnet/Opus 같은 frontier service의 기회비용 우위가 아직 크다.

가장 현실적인 전환 경로는 완전 대체가 아니라 hybrid다. cloud frontier model로 계획과 난해한 설계를 처리하고, 로컬 모델로 반복적 구현·테스트·리팩터링·사내 민감 코드 작업을 맡기는 방식이다. 토론의 여러 경험담은 이 중간 지대가 이미 꽤 넓어졌음을 보여준다.
