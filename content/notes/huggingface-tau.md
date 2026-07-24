---
title: "huggingface/tau: 작은 Python coding-agent harness"
date: 2026-07-25
draft: false
source_url: "https://github.com/huggingface/tau"
author: "Hugging Face"
tags: ["AI", "Coding Agents", "Agent Harness", "CLI", "Python", "Developer Tools"]
summary: "huggingface/tau는 terminal에서 동작하는 작은 Python coding agent이자, coding agent가 어떻게 구성되는지 읽기 쉽게 보여주는 teaching codebase다. 핵심은 provider-neutral stream을 담당하는 `tau_ai`, reusable agent brain인 `tau_agent`, 실제 CLI/TUI coding app인 `tau_coding`을 분리해 harness, event stream, tool, durable session의 경계를 명확히 드러내는 것이다."
---

> **원문:** [huggingface/tau](https://github.com/huggingface/tau) — Hugging Face, GitHub repository
>
> 이 항목은 전통적인 blog article이 아니라 GitHub repository / CLI landing page다. 따라서 README를 줄 단위로 그대로 옮기지 않고, 원문 README와 repository metadata의 정보 구조를 따라 Tau의 목적, 설치/실행 model, architecture boundary, library usage, development workflow, 운영 caveat를 한국어 practitioner note로 정리했다.

## 한눈에 보기

`huggingface/tau`는 “A Python port of Pi’s minimalist coding agent.”라는 설명을 가진 Python coding-agent project다. README는 Tau를 두 가지로 소개한다.

첫째, Tau는 terminal 안에서 동작하는 coding agent다. 사용자는 “explain this repo”, “add tests”, “fix this stack trace” 같은 request를 입력하고, Tau는 file을 읽고, code를 edit하고, command를 실행하며, durable session history를 유지한다.

둘째, Tau는 읽기 위한 codebase다. 거대한 production agent system을 바로 파고들지 않고도 coding-agent system의 shape을 이해할 수 있게 만든 teaching project다. 그래서 README와 contributor guide 모두 “작은 layer”, “typed event stream”, “portable harness”, “inspectable session” 같은 design principle을 반복해서 강조한다.

2026-07-25 확인 시점의 repository/package metadata는 다음과 같다.

- Repository: [github.com/huggingface/tau](https://github.com/huggingface/tau)
- Description: “A Python port of Pi’s minimalist coding agent.”
- License: MIT
- Language: Python
- Stars/Forks: 약 2.0k stars, 212 forks
- PyPI package: [`tau-ai`](https://pypi.org/project/tau-ai/) v0.3.2
- Python requirement: `>=3.12`
- Default branch: `main`
- Roadmap: [GitHub issue #1](https://github.com/huggingface/tau/issues/1)

## Core architecture

README가 가장 먼저 제시하는 구조는 다음 세 package의 layering이다.

```text
tau_coding  →  tau_agent  →  tau_ai
```

각 layer의 역할은 명확히 나뉜다.

| Layer | 역할 |
| --- | --- |
| `tau_ai` | model provider를 Tau의 provider-neutral stream으로 변환한다. |
| `tau_agent` | portable brain을 담당한다. message, tool, event, loop, harness, session primitive가 여기에 속한다. |
| `tau_coding` | reusable brain을 실제 coding app으로 감싼다. CLI, TUI, file/shell tool, provider config, project instruction, skill, on-disk session을 포함한다. |

README가 강조하는 boundary는 다음과 같다.

```text
AgentHarness = reusable brain
CodingSession = coding-agent environment
TUI = one possible frontend
```

핵심은 reusable harness가 Textual, Rich, local config path, slash command, rendering 같은 app/UI detail을 모른다는 점이다. Frontend는 harness가 내보내는 event를 consume한다. 이 구조는 agent를 “한 덩어리 application”으로 보지 않고, provider stream, agent loop, tool execution, rendering/UI를 나눠 생각하게 만든다.

## 설치 model

Tau는 PyPI에서 `tau-ai` package로 배포되며 `tau` command를 설치한다. README 기준 권장 설치 방식은 `uv`를 사용한 installer다.

macOS / Linux:

```bash
curl -LsSf https://twotimespi.dev/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://twotimespi.dev/install.ps1 | iex
```

Installer는 `sudo`를 쓰지 않고, 필요하면 `uv` 설치를 먼저 안내한 뒤 isolated tool environment에 Tau를 설치하고 `tau --version`으로 검증한다. 이미 package manager가 있다면 다음처럼 직접 설치할 수 있다.

```bash
uv tool install tau-ai
# or
pipx install tau-ai
# or
python -m pip install tau-ai
```

설치 확인은 간단하다.

```bash
tau --version
```

`conda-forge` / `pixi` 경로도 제공된다.

```bash
pixi global install tau-ai
```

일반 설치 update는 다음 command로 처리한다.

```bash
tau update
```

## Local development와 editable install

Source checkout에서 개발하려면 `uv` workflow를 사용한다.

```bash
git clone https://github.com/huggingface/tau.git
cd tau
uv sync --dev
uv run tau --version
```

Checkout-backed command를 global하게 노출하려면 editable tool install을 사용한다.

```bash
uv tool install --editable --force .
```

README가 명시하는 caveat는 중요하다. Editable install은 source-code change를 즉시 반영하지만, tool environment의 package metadata, dependency, entry point는 `uv`가 tool을 다시 설치할 때 갱신된다. 따라서 `git pull` 이후에는 위 command를 다시 실행해야 `tau --version` 같은 metadata가 이전 install 값에 머물지 않는다.

## Quickstart와 실행 방식

Tau는 작업하고 싶은 project directory에서 실행한다.

```bash
cd my-project
tau
```

이후 prompt를 입력하고 Enter를 누른다.

```text
explain what this project does
```

Script나 quick prompt에는 one-shot print mode가 유용하다.

```bash
tau -p "summarize the architecture"
tau --cwd /path/to/project -p "find the CLI entry point"
```

Tau는 model provider가 필요하다. Interactive session에서 `/login`으로 provider를 연결하고 `/model`로 model을 선택한다.

```text
/login
/login openai
/login openai-codex
/model
```

README 기준 built-in provider support는 OpenAI, Anthropic, OpenAI Codex subscription auth, OpenRouter, Hugging Face, custom OpenAI-compatible endpoint를 포함한다. README에는 local model도 가능하다고 되어 있지만, Compendium 운영 관점에서는 사용자의 명시적 선호에 따라 local LLM backend를 사용하지 않는 쪽이 기본이다.

Provider/model catalog는 code가 아니라 data로 관리된다. Built-in catalog는 `src/tau_coding/data/catalog.toml`에 있고, 개인 provider나 unreleased model은 같은 schema의 `~/.tau/catalog.toml`을 추가해 overlay할 수 있다. 즉 provider 추가를 위해 반드시 core code를 수정할 필요는 없다.

## Tau가 제공하는 기능

README의 기능 목록을 practitioner 관점으로 묶으면 다음과 같다.

1. Interactive Textual TUI와 non-interactive print mode를 함께 제공한다.
2. Built-in coding tool로 `read`, `write`, `edit`, `bash`를 제공한다.
3. Durable JSONL session을 `~/.tau/sessions/` 아래 저장하고 resume/branching을 지원한다.
4. Login, model selection, session, compaction, export, theme 등을 slash command로 다룬다.
5. Project instruction을 `AGENTS.md`, `.tau/`, `.agents/` resource에서 읽는다.
6. User skill, prompt template, custom TUI theme를 지원한다.
7. Context accounting, manual compaction, optional automatic compaction을 제공한다.
8. Rich, plain text, JSON, transcript, custom frontend를 위한 provider-neutral event rendering을 제공한다.

여기서 눈에 띄는 점은 “agent UX”와 “agent internals”가 함께 설계되어 있다는 것이다. Tau는 단순 CLI wrapper가 아니라, session persistence, context compaction, event rendering, tool schema, provider adapter까지 포함한 작은 reference implementation에 가깝다.

## Design philosophy

README의 philosophy section은 Tau의 설계 방향을 다섯 가지 규칙으로 요약한다.

- Small layers beat magic: 각 package는 하나의 job을 갖고 독립적으로 읽을 수 있어야 한다.
- Events are the contract: provider, renderer, TUI, custom frontend는 typed event stream에서 만난다.
- The core stays portable: reusable harness는 CLI, Textual, Rich, Tau file layout에 의존하지 않는다.
- Tools are ordinary typed functions: tool은 schema와 async executor가 structured result를 반환하는 형태다.
- Sessions are durable and inspectable: history는 append-only JSONL이고, active context는 record를 rewrite하지 않고 compact할 수 있다.

이 철학은 agent system을 debugging하거나 확장할 때 유용하다. Event가 contract라면 UI rendering 문제와 model/tool loop 문제를 분리해 볼 수 있고, session이 append-only JSONL이면 reproduce/export/branching이 쉬워진다. Provider catalog가 data라면 provider 추가가 core loop와 덜 결합된다.

## Library로 사용하는 방식

Tau는 CLI만 제공하는 것이 아니라 `tau_agent`의 `AgentHarness`를 library로 사용할 수 있다.

```python
from tau_agent import AgentHarness, AgentHarnessConfig

harness = AgentHarness(
    AgentHarnessConfig(
        provider=provider,
        model="my-model",
        system="You are a helpful coding agent.",
        tools=tools,
    )
)

async for event in harness.prompt("Explain this package"):
    print(event)
```

이 example의 의미는 “frontend가 무엇이든 core harness는 event를 emit한다”는 것이다. 같은 core가 built-in TUI, print mode, custom frontend를 구동할 수 있다. Agent framework를 연구하거나 내부 tool harness를 만들 때 참고할 만한 boundary다.

## Development workflow

README와 `CONTRIBUTING.md`가 제시하는 local check는 다음과 같다.

```bash
uv sync --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Checkout에서 Tau를 직접 실행할 수도 있다.

```bash
uv run tau
uv run tau -p "explain this repo"
```

Documentation site는 Hugo project이며 `website/content/` 아래 user docs를 둔다.

```bash
cd website
hugo server -D
hugo --minify
```

Contributor guide의 layer ownership도 명확하다.

| 변경 영역 | 들어갈 위치 |
| --- | --- |
| Provider integration, model adapter, provider-neutral streaming | `tau_ai` |
| Agent loop, tool abstraction, event, message, harness, portable session primitive | `tau_agent` |
| CLI behavior, slash command, TUI integration, local config, resource, skill, prompt template, coding-specific tool | `tau_coding` |
| Textual-specific code | TUI layer 뒤쪽 |
| Rich rendering | reusable harness 밖 |

변경이 layer를 넘나들 때는 app-specific detail을 core에 import하기보다 작은 typed boundary를 추가하라는 지침이 붙어 있다.

## Documentation entry points

README가 연결하는 주요 user/developer docs는 다음과 같다.

- [Documentation](https://twotimespi.dev/)
- [Quickstart](https://twotimespi.dev/quickstart/)
- [What is Tau?](https://twotimespi.dev/what-is-tau/)
- [Core concepts](https://twotimespi.dev/concepts/)
- [Architecture overview](https://twotimespi.dev/internals/architecture/)
- [The agent loop & events](https://twotimespi.dev/internals/agent-loop/)
- [CLI reference](https://twotimespi.dev/reference/cli/)
- [Provider guide](https://twotimespi.dev/guides/providers-and-models/)
- [PyPI package](https://pypi.org/project/tau-ai/)
- [Roadmap issue](https://github.com/huggingface/tau/issues/1)

## Practitioner 관점의 읽을거리

1. Tau의 가장 큰 가치는 “작은 agent를 쓸 수 있다”보다 “agent architecture를 읽을 수 있다”에 있다. Provider stream, harness, coding session, TUI가 어디서 분리되는지 명확히 드러난다.
2. `AgentHarness = reusable brain`과 `CodingSession = environment`의 구분은 agent product를 설계할 때 좋은 출발점이다. Core loop가 UI/config/path/tooling에 오염되면 testability와 portability가 빠르게 나빠진다.
3. Event stream을 contract로 두면 renderer, transcript, JSON output, custom frontend를 같은 core 위에 얹기 쉽다. 이는 observability와 replay/debugging에도 유리하다.
4. Session을 append-only JSONL로 두는 선택은 단순하지만 강력하다. Resume, branching, export, compaction을 구현할 때 “현재 context”와 “영구 기록”을 분리할 수 있다.
5. Provider catalog를 TOML data로 둔 점은 operationally 실용적이다. 조직 내부 endpoint나 unreleased model을 core code 변경 없이 overlay할 수 있다.
6. `read`, `write`, `edit`, `bash` 같은 built-in tool만으로도 coding agent loop의 essential path를 확인할 수 있다. 더 많은 integration보다, tool schema와 executor result boundary가 어떻게 구성되는지 보는 것이 더 중요하다.

## Caveats

- 이 note는 2026-07-25에 확인한 README, GitHub API metadata, `pyproject.toml`, `AGENTS.md`, `CONTRIBUTING.md`, PyPI metadata를 기준으로 한다.
- Star/fork 수와 package version은 snapshot이다.
- README는 Tau가 local model endpoint도 지원한다고 설명하지만, 이 Compendium note의 작성/검증에는 local LLM backend를 사용하지 않았다.
- Repository가 활발히 개발 중이므로 CLI flags, provider catalog schema, session layout, docs URL은 바뀔 수 있다. 실제 사용 전에는 [CLI reference](https://twotimespi.dev/reference/cli/)와 current README를 다시 확인하는 편이 좋다.
