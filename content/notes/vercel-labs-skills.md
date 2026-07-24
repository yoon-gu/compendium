---
title: "vercel-labs/skills: agent skill ecosystem을 위한 open CLI"
date: 2026-07-24
draft: false
source_url: "https://github.com/vercel-labs/skills"
author: "Vercel Labs"
tags: ["AI", "Agent Skills", "CLI", "Coding Agents", "Vercel", "Developer Tools"]
summary: "vercel-labs/skills는 여러 coding agent가 공유할 수 있는 SKILL.md 기반 instruction package를 설치·검색·업데이트·실행하는 CLI다. Claude Code, Codex, Cursor, OpenCode, GitHub Copilot, Hermes Agent 등 다양한 agent별 project/global skill directory를 추상화하고, GitHub/GitLab/git/local source에서 skill을 가져와 agent runtime에 연결한다."
---

> **원문:** [vercel-labs/skills](https://github.com/vercel-labs/skills) — Vercel Labs, GitHub repository
>
> 이 항목은 전통적인 blog article이 아니라 GitHub repository/CLI landing page다. 따라서 README를 그대로 line-by-line dump하지 않고, 원문 README의 구조를 따라 `skills` CLI의 기능, command model, agent compatibility, skill packaging convention, 운영상 caveat를 한국어로 정리했다.

## 한눈에 보기

`vercel-labs/skills`는 open agent skills ecosystem을 위한 CLI다. Repository description은 “The open agent skills tool - npx skills”이며, npm package name은 `skills`, 현재 README의 tagline은 “The CLI for the open agent skills ecosystem.”이다.

핵심 아이디어는 단순하다. Coding agent별로 흩어진 skill directory layout을 CLI가 알고 있고, 사용자는 GitHub repository, GitLab repository, arbitrary git URL, local path 등에서 `SKILL.md` 기반 skill package를 가져와 agent별 project/global location에 설치한다. 반대로 설치하지 않고 특정 skill prompt만 생성해 stdout으로 흘려보내거나, 지원 agent를 바로 interactive하게 실행할 수도 있다.

2026-07-24 확인 시점의 repository metadata는 다음과 같다.

- Repository: [github.com/vercel-labs/skills](https://github.com/vercel-labs/skills)
- Description: “The open agent skills tool - npx skills”
- License: MIT
- Stars/Forks: 약 27.1k stars, 2.3k forks
- Package: `skills` v1.5.20, Node `>=22.20.0`, package manager `pnpm@10.17.1`
- 주요 binary: `skills`, `add-skill`

## Skill 설치와 사용 model

가장 기본적인 설치 command는 다음과 같다.

```bash
npx skills add vercel-labs/agent-skills
```

이 command는 source repository에서 skill을 찾아 현재 project 또는 global agent directory에 설치한다. 특정 skill만 고르거나, 특정 agent만 target할 수도 있다.

```bash
# repository 안의 skill 목록 보기
npx skills add vercel-labs/agent-skills --list

# 특정 skill 설치
npx skills add vercel-labs/agent-skills --skill frontend-design --skill skill-creator

# 특정 agent에 설치
npx skills add vercel-labs/agent-skills -a claude-code -a opencode

# CI/CD friendly non-interactive install
npx skills add vercel-labs/agent-skills --skill frontend-design -g -a claude-code -y

# repository의 모든 skill을 모든 agent에 설치
npx skills add vercel-labs/agent-skills --all
```

설치하지 않고 skill을 한 번만 사용할 수도 있다.

```bash
npx skills use vercel-labs/agent-skills@web-design-guidelines | claude
npx skills use vercel-labs/agent-skills --skill web-design-guidelines --agent claude-code
```

`skills use`는 `skills add`와 같은 source resolution rule을 사용한다. 선택된 skill file을 temporary directory에 쓰고, 기본적으로 generated prompt만 stdout에 출력한다. `--agent`가 주어지면 지원되는 coding agent를 interactive하게 시작한다.

## Source format

README가 강조하는 점은 source가 특정 marketplace에 갇혀 있지 않다는 것이다. `skills add`는 다음 형태를 지원한다.

```bash
# GitHub shorthand
npx skills add vercel-labs/agent-skills

# Full GitHub URL
npx skills add https://github.com/vercel-labs/agent-skills

# Repository 안의 특정 skill path
npx skills add https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines

# GitLab URL
npx skills add https://gitlab.com/org/repo

# Any git URL
npx skills add git@github.com:vercel-labs/agent-skills.git

# Local path
npx skills add ./my-local-skills
```

Practitioner 관점에서 중요한 점은 skill distribution을 Git repository 중심으로 둔다는 것이다. 즉, skill은 package registry에만 의존하지 않고, team 내부 repository, monorepo subdirectory, local workspace에서 직접 versioning될 수 있다.

## Command surface

README의 command set은 `add`, `use`, `list`, `find`, `remove`, `update`, `init`으로 구성된다.

| Command | 역할 |
| --- | --- |
| `npx skills add <source>` | source에서 skill을 찾아 agent directory에 설치한다. |
| `npx skills use <source>` | skill을 설치하지 않고 prompt를 생성하거나 agent를 실행한다. |
| `npx skills list` / `npx skills ls` | project/global에 설치된 skill을 나열한다. |
| `npx skills find [query]` | local/remote skill을 interactive 또는 keyword로 검색한다. |
| `npx skills remove [skills]` | 설치된 skill을 제거한다. |
| `npx skills update [skills]` | 설치된 skill을 최신 source로 업데이트한다. |
| `npx skills init [name]` | 새 `SKILL.md` template을 만든다. |

`skills find`는 owner scope를 지정해 조직이나 user의 repository 전체에서 검색할 수 있다.

```bash
npx skills find typescript
npx skills find react --owner vercel
```

`skills update`는 scope detection을 제공한다. Project 안에서 실행하면 project skill을 우선 update하고, 그렇지 않으면 global scope를 대상으로 삼는 식이다.

```bash
npx skills update
npx skills update my-skill
npx skills update frontend-design web-design-guidelines
npx skills update -g
npx skills update -p
npx skills update -y
```

## 설치 scope와 방식

설치 scope는 project와 global 두 가지다.

| Scope | 위치 | 사용 상황 |
| --- | --- | --- |
| Project | `./<agent>/skills/` | repository와 함께 commit해 team convention으로 공유한다. |
| Global | `~/<agent>/skills/` | user machine 전체에서 쓰는 personal skill로 관리한다. |

Interactive install에서는 symlink와 copy 중 하나를 선택할 수 있다.

- Symlink: canonical copy 하나를 두고 각 agent directory에서 symlink한다. Single source of truth와 update 관리에 유리하다.
- Copy: agent별 independent copy를 만든다. Symlink가 적합하지 않은 filesystem/runtime에서 선택한다.

이 구분은 agent skill 운영에서 꽤 중요하다. Team convention skill은 project scope로 두고 review/commit 대상에 포함하는 편이 좋고, 개인 workflow skill은 global scope로 두는 편이 자연스럽다. Symlink 방식은 여러 agent를 동시에 쓰는 developer에게 중복 drift를 줄이는 장점이 있다.

## Agent Skills란 무엇인가

README에서 정의하는 Agent Skill은 coding agent capability를 확장하는 reusable instruction set이다. Directory 안의 `SKILL.md` file로 정의되며, YAML frontmatter에 최소한 `name`과 `description`을 포함한다.

```markdown
---
name: my-skill
description: What this skill does and when to use it
---

# My Skill

Instructions for the agent to follow when this skill is activated.

## When to Use

Describe the scenarios where this skill should be used.

## Steps

1. First, do this
2. Then, do that
```

Skill이 다루는 task example은 release note generation, team convention을 따르는 PR creation, Linear/Notion 같은 external tool integration 등이다. 이 repository는 skill 자체의 내용보다, 이런 skill package를 여러 agent runtime에 배포하고 발견하게 만드는 CLI layer에 초점이 있다.

## Supported agents와 directory abstraction

README는 OpenCode, Claude Code, Codex, Cursor를 포함해 다수의 agent를 지원한다고 밝힌다. 실제 table에는 Claude Code, Codex, Cursor, GitHub Copilot, Hermes Agent, Gemini CLI, OpenCode, OpenHands, Roo Code, Windsurf, Zed, Qwen Code 등 많은 target이 포함되어 있고, 각 agent별 project/global path가 다르게 정의되어 있다.

예를 들어 일부 대표 target은 다음과 같다.

| Agent | `--agent` | Project path | Global path |
| --- | --- | --- | --- |
| Claude Code | `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `codex` | `.agents/skills/` | `~/.codex/skills/` |
| Cursor | `cursor` | `.agents/skills/` | `~/.cursor/skills/` |
| GitHub Copilot | `github-copilot` | `.agents/skills/` | `~/.copilot/skills/` |
| Hermes Agent | `hermes-agent` | `.hermes/skills/` | `~/.hermes/skills/` |
| OpenCode | `opencode` | `.agents/skills/` | `~/.config/opencode/skills/` |
| Gemini CLI | `gemini-cli` | `.agents/skills/` | `~/.gemini/skills/` |

이 abstraction의 가치는 각 agent가 skill loading directory를 서로 다르게 정의한다는 현실을 CLI가 흡수한다는 데 있다. 사용자는 “이 skill을 Codex와 Claude Code에 넣어라”라고 말하고, CLI가 `.agents/skills/`, `.claude/skills/`, `~/.codex/skills/` 같은 path convention을 처리한다.

## Skill discovery rule

CLI는 repository 안에서 skill을 찾을 때 여러 container directory를 탐색한다. 대표적으로 root `SKILL.md`, `skills/`, `skills/.curated/`, `skills/.experimental/`, `skills/.system/`, `.agents/skills/`, `.claude/skills/`, `.hermes/skills/` 등이 포함된다.

Discovery depth도 명시되어 있다. 일반적인 flat layout인 `skills/<name>/SKILL.md`는 한 level deep으로 탐색하고, catalog layout인 `skills/<category>/<name>/SKILL.md`는 한 level 더 깊게 탐색한다. Shallow level의 `SKILL.md`가 발견되면 그 아래 nested skill은 shadow된다. `--full-depth`를 쓰면 `examples/`나 `tests/` 같은 standard container 밖의 `SKILL.md`도 탐색할 수 있다.

또한 `.claude-plugin/marketplace.json` 또는 `.claude-plugin/plugin.json`이 있으면 plugin manifest에 선언된 skill도 discovery 대상이 된다. 이는 Claude Code plugin marketplace ecosystem과의 compatibility를 위한 bridge다.

## Compatibility model

README는 skill이 대체로 shared Agent Skills specification을 따르기 때문에 agent 간 호환된다고 설명한다. 하지만 일부 feature는 agent-specific이다. Compatibility table의 핵심은 다음과 같다.

- Basic skills는 주요 agent 전반에서 지원된다.
- `allowed-tools`는 여러 agent가 지원하지만 Cursor, Zencoder 등 일부 target에서는 지원되지 않는다.
- `context: fork`는 Claude Code 중심 feature로 보이며, 다수 agent에서는 지원되지 않는다.
- Hooks는 Claude Code, Cline, Cursor 등 일부에서만 지원된다.

따라서 portable skill을 만들려면 core instruction은 `SKILL.md`의 plain Markdown과 frontmatter에 두고, `allowed-tools`, hook, context fork 같은 feature는 target agent별 fallback을 고려해야 한다.

## Troubleshooting과 운영 환경

README의 troubleshooting은 세 가지 기본 문제를 다룬다.

1. “No skills found”: repository 안에 valid `SKILL.md`가 있고 frontmatter에 `name`, `description`이 있는지 확인한다.
2. Skill not loading in agent: 올바른 agent path에 설치되었는지, agent documentation에서 loading requirement가 있는지, YAML frontmatter가 valid한지 확인한다.
3. Permission errors: target directory에 write access가 있는지 확인한다.

환경 변수도 간단하다.

| Variable | 의미 |
| --- | --- |
| `INSTALL_INTERNAL_SKILLS` | `internal: true` skill을 표시하고 설치한다. |
| `DISABLE_TELEMETRY` | anonymous usage telemetry를 비활성화한다. |
| `DO_NOT_TRACK` | telemetry disable을 위한 alternative variable이다. |

Telemetry는 anonymous usage data를 수집하며, CI environment에서는 자동으로 비활성화된다고 README는 설명한다.

## Related links

원문 README가 제공하는 주요 link는 다음과 같다.

- [Agent Skills Specification](https://agent-skills.io)
- [Skills Directory](https://www.skills.sh)
- [Vercel Agent Skills Repository](https://github.com/vercel-labs/agent-skills)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Codex/OpenAI Skills Documentation](https://learn.chatgpt.com/docs/build-skills)
- [GitHub Copilot Agent Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Cursor Skills Documentation](https://cursor.com/docs/skills)
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills)

## Practitioner 관점의 읽을거리

1. Skill은 “prompt snippet”보다 운영 단위에 가깝다. `SKILL.md` frontmatter, directory layout, source resolution, install/update/remove lifecycle이 함께 정의되어야 team에서 재사용 가능하다.
2. Multi-agent user에게 가장 큰 pain point는 directory convention drift다. 이 CLI는 agent별 path mapping을 중앙에서 관리해 Claude Code, Codex, Cursor, Hermes Agent 같은 runtime에 같은 skill source를 배포할 수 있게 한다.
3. Git repository를 source of truth로 쓰는 model은 reviewability와 versioning에 유리하다. Team skill은 PR review, change history, release note, rollback과 자연스럽게 결합된다.
4. Portable skill을 목표로 한다면 agent-specific feature에 주의해야 한다. Basic instruction은 넓게 호환되지만 `allowed-tools`, hooks, `context: fork`는 agent별 support matrix를 확인해야 한다.
5. `skills use`는 설치 없이 skill prompt를 생성하므로 evaluation이나 one-off workflow에 유용하다. 반면 반복적으로 쓰는 skill은 project/global scope에 설치해 update lifecycle을 관리하는 편이 낫다.

## Caveats

- 이 note는 repository README와 GitHub API metadata를 기준으로 작성했다. CLI behavior는 package release와 README update에 따라 바뀔 수 있다.
- Star/fork 수는 확인 시점의 snapshot이다.
- `skills` CLI가 지원하는 agent 목록은 빠르게 늘어날 수 있으므로, 실제 install 전에는 README의 Supported Agents table과 target agent documentation을 다시 확인하는 것이 좋다.
- Telemetry를 원하지 않는 환경에서는 `DISABLE_TELEMETRY` 또는 `DO_NOT_TRACK` 설정을 명시적으로 두는 편이 안전하다.
