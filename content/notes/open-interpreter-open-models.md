---
title: "Open Interpreter: open model을 위한 application layer"
date: 2026-07-13
draft: false
source_url: "https://www.openinterpreter.com/blog/open-interpreter"
author: "Open Interpreter"
tags: ["AI", "Coding Agent", "Open Models", "Agent", "Developer Tools"]
summary: "새 Open Interpreter는 low-cost/open-weight model을 first-class citizen으로 다루기 위해 Codex CLI 기반의 terminal interface, app-server protocol, cross-platform sandboxing을 확장한 coding agent다. 핵심은 model별 harness emulation과 native sandboxing으로, frontier model 전용으로 설계된 agent stack을 open model 생태계에 맞게 재구성하는 것이다."
---

> **원문:** [Open Interpreter - The application layer for open models](https://www.openinterpreter.com/blog/open-interpreter) — Open Interpreter, 2026-07-13
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. Technical term은 Compendium 독자 맥락에 맞춰 필요한 경우 English를 유지했다.

<video controls autoplay loop muted playsinline preload="metadata" style="display:block; width:100%; max-width:100%; max-height:70vh; height:auto; object-fit:contain; margin:1rem auto;" src="https://www.openinterpreter.com/blog/open-interpreter/oi-sizzle-hero.mp4"></video>

가벼운 coding agent.

Low-cost model을 위해 설계되었다.

```bash
curl -fsSL https://www.openinterpreter.com/install | sh
```

## 새로운 frontier

AI에는 economics 문제가 있다. 지난달 Uber는 2026년 AI coding budget을 이미 다 써버렸다. 기업들은 frontier model 사용량을 rationing하기 시작했거나, 더 저렴한 model을 찾아다니고 있다.

강력한 open-weight model은 이 문제의 절반을 해결하고 있다. DeepSeek의 최신 model은 Claude Opus 4.7 대비 지능이 80%를 넘는 수준이지만, 비용은 100배 낮다. Factory는 open-model 사용량이 closed model 대비 지난 한 달 사이 3배 늘었다고 보고했고, inference provider들도 같은 흐름을 보고 있다.

Intelligence와 cost의 새로운 Pareto frontier에서, 왼쪽 band가 올라오고 있다.

### Intelligence vs. Price

Open / low-cost model variants와 frontier models.

Artificial Analysis Intelligence Index vs. price in USD per 1M tokens.

하지만 문제는 model을 실제로 유용하게 만드는 product 대부분이 frontier intelligence model을 전제로 만들어졌다는 점이다. Claude Code와 Cowork은 Claude를 위해 만들어졌고, Codex는 GPT를 위해 만들어졌다.

Open Interpreter는 open-weight model을 first-class citizen으로 다루는 open application layer를 만들고 있다.

## Open Interpreter

오늘 Open Interpreter는 permissive Apache 2.0 License 아래 완전히 새로운 Open Interpreter를 공개한다.

Open Interpreter는 OpenAI의 Codex CLI 위에 구축되었다. 성숙한 terminal interface, app-server protocol, cross-platform sandboxing을 그대로 물려받는다. 하지만 그 기반을 low-cost model을 위해 몇 가지 방식으로 넓혔다.

## Harness Emulation

Coding model은 harness를 통해 세상과 상호작용하도록 훈련된다. 여기서 harness란 agent가 운전하는 “vehicle”이며, tool behavior, system instruction, context compaction workflow 등을 포함한다.

전통적인 coding agent는 Codex나 Claude Code처럼 하나의 model을 중심으로 만들어져 있거나, generic harness를 사용한다. 그러나 model의 RL environment가 generic harness와 다르면 performance가 손상될 수 있다.

Open Interpreter는 다른 접근을 택한다. 각 model에서 가장 좋은 성능을 끌어내는 harness를 emulate하여, model이 가장 “편하게” 운전할 수 있는 vehicle을 몰게 한다.

### Generic harness

```text
bash command, timeout
read filePath, offset
write filePath, content
edit filePath, oldString
grep pattern, path
system message instructions
compaction system context
```

### Model에 최적화된 harness

```text
list_directory path, ignore
read_file path, offset
write_file path, content
grep_search pattern, include
glob pattern
system message instructions
compaction system context
```

Open Interpreter 내부에서 Claude는 Claude Code와 유사한 emulated harness를 사용한다. GPT는 Codex harness를 사용한다. Kimi, Qwen, DeepSeek은 하나의 generic harness가 아니라 provider-recommended harness의 emulation을 사용한다.

이 접근의 benefit을 검증하기 위해 Open Interpreter는 generic harness를 사용하는 popular coding agent인 OpenCode 내부에서 DeepSeek V4 Flash를 Terminal-Bench 2.1로 측정한 결과와, provider-recommended harness를 emulate하는 Open Interpreter에서 측정한 결과를 비교했다.

점점 더 다양한 agent가 등장하고 inference market의 경쟁이 치열해지는 환경에서, Open Interpreter는 harness emulation이 model routing보다 agentic application을 위한 더 강한 foundation이라고 본다.

## Native Sandboxing

지금까지 open model을 위한 인기 agent들은 built-in sandboxing이 부족했다. 따라서 developer는 계속 뜨는 permission prompt를 직접 monitoring하거나, 격리된 machine에서만 작업하거나, Docker 같은 무거운 virtualization system을 사용해야 했다.

Agent가 몇 시간 또는 며칠 동안 안전하게 일하려면 이런 방식은 실용적이지 않다.

Open Interpreter는 Codex의 lightweight sandboxing을 Windows, macOS, Linux 전반에서 물려받았다. 이를 통해 agent는 working directory 위에서 autonomous하게 작업할 수 있고, OS가 network와 filesystem access를 제한한다.

## Developer를 위해

현재 사용 중인 coding agent를 선택하면, Open Interpreter가 무엇이 다른지 설명해준다.

## Agent Builder를 위해

Open Interpreter는 app-server SDK workflow에서 Codex를 대체할 수 있다.

### Open Interpreter를 사용하는 Codex app-server SDK

### CI의 Codex에서 CI의 Open Interpreter로

Open Interpreter는 [Agent Client Protocol](https://www.openinterpreter.com/docs/terminal/acp) agent로도 실행될 수 있다. 따라서 [Zed](https://zed.dev/acp), [JetBrains IDEs](https://www.jetbrains.com/acp/), [VS Code](https://marketplace.visualstudio.com/items?itemName=strato-space.acp-plugin), [Obsidian](https://rait-09.github.io/obsidian-agent-client/reference/acp-support.html) 같은 ACP client가 Open Interpreter를 직접 launch할 수 있다. Open Interpreter는 생태계가 더 open tooling을 개발할 수 있도록 이 protocol로 standardize하는 것을 권장한다.

## Enterprise를 위해

조직이 현재 expensive coding agent를 사용하고 있다면 [Open Interpreter에 문의](https://www.openinterpreter.com/savings-estimate?intent=enterprise&source=open-interpreter-enterprise)할 수 있다. Open Interpreter는 low-cost model이 frontier model을 안정적으로 대체할 수 있는 agentic workflow를 식별하고, 다음 token bill에서 절감할 수 있는 비용을 추정할 수 있다고 설명한다.

팀은 Open Interpreter와 함께 기존 [intelligence provider](https://www.openinterpreter.com/docs/terminal/providers)를 그대로 사용할 수 있으며, 추가로 agent가 task를 low-cost model에 delegate하도록 만들 수 있다.

Open Interpreter는 Codex fork이므로, Codex를 쓰는 팀에는 이 전환이 특히 단순하다. 팀이 설정해 둔 terminal interface, skill, plugin은 그대로 유지된다.

Open Interpreter는 model lab에도 application layer를 bootstrap하기 위해 협업하자고 제안한다. 어떤 model이 특정 harness에서 RL-tuned되었거나 evaluate되었다면, model lab이 spec을 제공하고 Open Interpreter가 이를 implement할 수 있다. 이렇게 하면 developer는 해당 model에 대해 더 나은 첫 경험을 얻고, model lab은 API 이상의 product를 직접 만들지 않고도 product feedback을 얻을 수 있다.

## Continuity

2023년에 처음 공개된 original Python version인 Open Interpreter Classic은 [community-maintained fork](https://github.com/endolith/open-interpreter)로 계속 유지된다. Open Interpreter는 Discord에서 많은 사람이 이를 사용하고 확장하고 서로 배우도록 도운 maintainer Anton(Discord의 notnaton)과 Endolith(Discord의 deseculavalutent)에게 감사를 전한다.

## Beyond the Terminal

Non-developer를 위해 Open Interpreter는 최근 [Claude Cowork와 유사한 desktop app](https://www.openinterpreter.com/blog/the-new-knowledge-worker)을 공개했다. 이 app은 browser, Office document, 기타 local application 안에서 작업할 수 있으며, 새로운 Open Interpreter runtime 위에 구축되었다.

기업이 Claude Cowork과 Codex를 업무에 실험하고 있다면, Open Interpreter는 lab들이 제공하는 cost와 같거나 더 낮은 비용으로 같은 feature를 제공하겠다고 말한다. [문의](https://www.openinterpreter.com/savings-estimate?intent=knowledge-worker&source=open-interpreter-knowledge-worker)하거나 [Interpreter를 무료로 사용](https://www.openinterpreter.com/)해볼 수 있다.

## Practitioner 관점에서 읽을 포인트

이 글의 핵심은 “또 하나의 coding agent 출시”보다, open model을 product-grade agent로 쓰기 위한 application layer를 어떻게 설계할 것인가에 있다.

1. Cost frontier가 바뀌면서 open-weight/low-cost model은 충분히 강해지고 있지만, 실제 agent product는 여전히 frontier model의 harness와 assumption에 묶여 있다.
2. Open Interpreter의 차별점은 model routing이 아니라 harness emulation이다. 같은 model이라도 어떤 tool schema, instruction, compaction workflow에서 RL-tuned되었는지에 따라 performance가 달라질 수 있다는 관찰을 product architecture로 반영했다.
3. Codex CLI를 fork함으로써 terminal UX, app-server protocol, sandboxing 같은 이미 검증된 substrate를 재사용한다. 즉 model 생태계 쪽은 open/low-cost로 넓히되, agent runtime의 안전성과 developer experience는 기존 Codex stack에서 가져온다.
4. Native sandboxing은 단순한 편의 기능이 아니라 long-running autonomous agent의 전제 조건이다. Permission prompt를 사람이 계속 감시하거나 Docker만으로 격리하는 방식은 enterprise workflow에서 지속 가능하지 않다.
5. ACP 지원은 IDE와 editor 생태계가 특정 agent vendor에 묶이지 않도록 하는 protocol layer 전략으로 읽을 수 있다.

따라서 Open Interpreter의 주장은 명확하다. Open model 시대에는 “어떤 model을 route할 것인가”만큼이나, “그 model이 훈련되고 평가된 방식에 맞는 harness를 어떻게 제공할 것인가”가 중요하다. 이 관점은 coding agent뿐 아니라 향후 tool-using LLM product 전반에 적용될 수 있다.
