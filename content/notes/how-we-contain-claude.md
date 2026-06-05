---
title: "Claude를 제품 전반에서 격리하는 방법"
date: 2026-06-06
draft: false
source_url: "https://www.anthropic.com/engineering/how-we-contain-claude"
author: "Max McGuinness, Mikaela Grace, Jiri De Jonghe, Jake Eaton, Abel Ribbink"
tags: ["AI", "에이전트", "보안", "샌드박스", "Claude", "Anthropic"]
summary: "Anthropic은 claude.ai, Claude Code, Claude Cowork에서 서로 다른 격리 아키텍처를 적용해 에이전트의 blast radius를 제한한다. 글은 사람 승인, 모델 계층 방어, 샌드박스·VM·egress 제어의 역할과 실제로 놓쳤던 취약 사례를 통해 에이전트 보안의 설계 원칙을 정리한다."
---

> **원문:** [How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude) — Anthropic Engineering, 2026년 5월 25일
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. 코드·제품명·보안 용어는 필요한 경우 영어 원문을 함께 둔다.

12개월 전만 해도 Anthropic 내부 서비스 하나를 중단시킬 수 있을 정도의 접근 권한을 Claude에게 주자는 생각은 단번에 거절했을 것이다. 오늘날 그런 수준의 접근은 일상적이고, Anthropic 개발자들은 그 덕분에 더 생산적으로 일한다. 이런 배포의 위험은 두 요소로 나뉜다. 실패가 일어날 가능성이 얼마나 되는가, 그리고 실패가 일어나면 얼마나 큰 피해를 낼 수 있는가. 안전장치와 모델 학습의 진전은 첫 번째 요소를 꾸준히 낮춰 왔다. 반면 두 번째 요소, 즉 이론적 폭발 반경(blast radius)은 모델 능력과 접근 권한이 커질수록 계속 커진다. 그래도 에이전트가 예전에는 한 사람, 때로는 한 팀이 해야 했던 일을 수행할 수 있게 되면, 배포하지 않는 비용도 커진다. 제품을 안전하게 만들 수만 있다면 위험-보상 계산은 배포 쪽으로 크게 기운다. 따라서 엔지니어링 질문은 이렇게 바뀐다. blast radius를 어떻게 상한으로 묶을 것인가.

![자율 에이전트의 상대적 피해를 환경 제어 등으로 제한할 수 있으면, 높은 유용성을 가진 기능은 배포 동기가 생긴다. Claude Mythos Preview는 2026년 4월 기준 blast radius가 너무 크다고 판단되어 출시되지 않은 모델의 예다.](https://www-cdn.anthropic.com/images/4zrzovbb/website/5ebc85c6325c7f59bd6c08950ff9beb1863f1345-1920x866.png)

이를 수행하는 방법은 크게 두 가지다.

첫 번째는 human-in-the-loop 방식으로 에이전트의 행동을 감독하는 것이다. 예전의 Claude Code는 매 턴마다 사용자에게 권한을 요청해 에이전트가 의도치 않은 행동을 하지 못하게 막았다. 이론적으로는 작동하지만, Anthropic은 이 접근이 오류를 내기 쉽다는 점을 확인했다. 텔레메트리에 따르면 사용자는 권한 프롬프트의 약 93%를 승인했다. 사용자가 승인 요청을 많이 볼수록 각 요청에 덜 주의를 기울이고, 시간이 지날수록 감독이 훨씬 덜 성실해진다. Anthropic은 최근 [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)를 만들어 더 안전한 승인을 자동화함으로써 이런 승인 피로를 줄였다. 그래도 취약점은 남는다. 확률적 방어에는 언제나 0이 아닌 누락률이 있다.<sup>1</sup>

두 번째, 그리고 이 글의 많은 부분이 다루는 접근은 격리(containment)다. 에이전트가 무엇을 하는지 감독하기보다, 샌드박스, 가상 머신, egress 제어 같은 수단으로 접근 경계를 강제해 에이전트가 무엇을 할 수 있는지를 감독한다. Anthropic 엔지니어링이 가장 많은 노력을 들인 곳이 여기이고, 동시에 가장 놀라운 보안 실패들이 일어난 곳도 여기다.

지난 2년 동안 Anthropic은 세 가지 주요 에이전트 제품을 출시했다. [claude.ai](http://claude.ai/redirect/website.v1.e96f927e-043f-42d5-bc19-fdf23c781f7b), Claude Code, Claude Cowork다. 각 제품은 서로 다른 사용자층을 대상으로 하므로 서로 다른 격리 아키텍처가 필요하다. 이 글은 무엇이 버텼고, 무엇이 깨졌으며, 에이전트 보안에 관해 무엇을 배웠는지를 공유한다.

## 세 가지 위험, 방어의 세 가지 구성요소

에이전트에 대한 보안 위험은 세 범주 중 하나에 속한다.

사용자 오용(user misuse): 사용자가 악의적으로 또는 부주의하게 에이전트에게 해로운 일을 지시한다. 여기에는 귀찮은 검사를 우회하라고 요청하는 것부터, 이해하지 못하는 파괴적 명령을 실행하는 것, 의도적 위해를 명시하는 것까지 모두 포함된다.

모델 오작동(model misbehavior): 아무도 요청하지 않았는데 에이전트가 해로운 행동을 한다. 모델이 개선되면서 대부분의 행동 평가에서는 더 정렬(aligned)되었지만, 이것이 위험이 반드시 줄어든다는 뜻은 아니다. 덜 유능한 모델은 상황을 잘못 읽고 명백한 실수를 할 가능성이 높다. 더 유능한 모델은 실수를 덜 하지만, 목표에 도달하는 예상 밖의 경로를 더 잘 찾아내기도 한다. 종종 아무도 명시적으로 적어 두지 않은 제한을 우회한다.

Anthropic은 Claude 모델이 작업을 완료하려고 [“친절하게” 샌드박스를 탈출](https://red.anthropic.com/2026/mythos-preview/)하거나, 코딩 테스트의 답을 찾기 위해 git 히스토리를 살펴보거나, 실행 중인 벤치마크를 스스로 식별해 [정답 키를 복호화](https://www.anthropic.com/engineering/eval-awareness-browsecomp)하는 사례를 보았다. 각 모델은 새로운 능력 집합을 가져오고, 그 능력은 때때로 예상치 못한 방식으로 쓰인다.

외부 공격자(external attackers): 에이전트가 도구, 파일, 네트워크 접근 같은 외부 벡터를 통해 공격받는다. 이 범주에는 prompt injection과, 에이전트 런타임·오케스트레이션 계층·프록시에 대한 전통적 공격이 모두 포함된다.

격리와 방어 시스템을 만들 때 Anthropic은 세 가지 주요 구성요소에 방어를 적용한다.

에이전트가 실행되는 환경. 프로세스 샌드박스, VM, 파일시스템 경계, egress 제어로 에이전트가 어디에서 어떻게 행동할 수 있는지 제한한다. 목표는 에이전트가 닿을 수 있는 것에 단단한 경계를 설정하는 것이다. 예를 들어 credential이 샌드박스 안으로 들어가지 않는다면, 원인이 사용자든, 모델이 “창의적” 경로를 찾은 것이든, 공격자든 관계없이 credential은 유출될 수 없다.

촘촘한 경계는 감독을 느슨하게 할 수도 있게 한다. Claude Code의 [reference devcontainer](https://code.claude.com/docs/en/devcontainer)는 바로 에이전트가 각 행동마다 승인을 받지 않고도 무인으로 실행될 수 있게 하려고 존재한다.

에이전트가 참조하는 모델. 여기에는 system prompt, classifier, probe, 학습 수정이 포함된다. 모델은 확률적이므로, 이런 방어는 에이전트가 어떤 행동을 하는 경향이 있는지만 형성할 뿐, 이론적으로 무엇을 할 수 있는지를 제한하지는 않는다.

이 방어들은 강력하다. prompt injection 취약성을 시험하는 Gray Swan의 Agent Red Teaming benchmark에서 [Claude Opus 4.7](https://cdn.sanity.io/files/4zrzovbb/website/037f06850df7fbe871e206dad004c3db5fd50340.pdf)은 단일 시도 기준 공격 성공률을 약 0.1%로, 100번의 적응형 시도 후에는 약 5-6%로 억제한다. Claude Code auto mode는 과도하게 적극적인 행동의 약 83%를 [실행 전에 포착](https://www.anthropic.com/engineering/claude-code-auto-mode)한다. 그러나 최고 수준의 방어가 있더라도 모델 계층의 보호는 결코 100% 효과적일 수 없으며, 그래서 단독으로 설 수 없다.

에이전트가 닿을 수 있는 외부 콘텐츠. MCP 서버, 서드파티 플러그인, 웹 검색 도구는 모두 사용자가 통제하지 않는 출처의 콘텐츠를 에이전트 컨텍스트에 넣는다. 감사된 connector가 감사된 데이터와 같은 것은 아니다. 예를 들어 GitHub connector는 악성코드 검사를 통과하더라도 오염된 README를 그대로 모델 컨텍스트에 적재할 수 있다. 도구 권한을 세밀하게 제한하면 blast radius를 줄이는 데 도움이 된다. 예를 들어 읽기 전용 DB 접근만 가진 에이전트는 prod에 쓰기 권한을 가진 에이전트보다 훨씬 넓게 배포할 수 있다.

방어는 서로 겹치고 보완해야 한다. 환경 방어를 사용할 수 없으면 모델 계층이 그 공백을 메워야 한다. 이것이 Claude Code의 [auto mode](https://claude.com/blog/auto-mode)가 설계된 정확한 목적이다. 로컬에서는 환경 방어와 모델 방어가 악성 도구 출력에 대응할 수 있지만, 도구의 능력과 접근을 제한함으로써 체인의 더 위쪽에서도 방어를 추가할 수 있다.

![방어해야 할 세 구성요소: 모델, 모델이 실행되는 환경, 에이전트가 닿을 수 있는 외부 콘텐츠.](https://www-cdn.anthropic.com/images/4zrzovbb/website/5fae1ecca4cd8aaefb9ac949348e96967f9a5100-1920x1080.png)

## 에이전트를 격리하는 패턴

환경 계층에 초점을 맞춰, Anthropic은 세 가지 격리 패턴과 그것이 각 Claude 플랫폼인 [claude.ai](http://claude.ai/redirect/website.v1.e96f927e-043f-42d5-bc19-fdf23c781f7b), Claude Code, Cowork에 어떻게 맞춰졌는지 설명한다. 각 설계는 에이전트에 필요한 능력과 사용자 개입의 정도 사이에서 균형을 찾으며 점진적으로 도달한 것이다.

### 패턴 1: 임시 컨테이너, claude.ai code execution

claude.ai는 채팅 인터페이스로 가장 잘 알려져 있지만, 코드도 작성하고 실행하며, 파일을 생성하고 connector도 호출한다. Claude가 claude.ai 안에서 코드를 실행할 때는 격리된 인프라의 [gVisor](https://en.wikipedia.org/wiki/GVisor) 컨테이너에서 실행한다. 에이전트는 완전히 서버 측에 있으며, 로컬 머신에서는 어떤 코드도 실행되지 않고, 파일시스템은 세션 단위로 임시적이다. blast radius는 최소지만, Claude가 할 수 있는 일의 상한도 낮다. 지속적 workspace도 없고 사용자 파일시스템에도 접근할 수 없다.

이 때문에 [claude.ai](http://claude.ai/redirect/website.v1.e96f927e-043f-42d5-bc19-fdf23c781f7b)는 더 전통적인 threat model의 대상이 된다. 사용자 머신을 에이전트로부터 보호하는 것이 아니라, Anthropic의 인프라와 각 tenant를 서로로부터 보호하는 것이다. [claude.ai](http://claude.ai/redirect/website.v1.e96f927e-043f-42d5-bc19-fdf23c781f7b) 출시 전 작업의 대부분은 네트워크 설정, 내부 서비스 인증, 오케스트레이션 같은 전통적 보안 작업이었다.

그 작업은 보안의 가장 오래된 교훈을 다시 확인시켰다. 가장 약한 계층은 직접 만든 계층이다. gVisor와 [seccomp](https://en.wikipedia.org/wiki/Seccomp)는 에이전트형 AI가 존재하기 훨씬 전부터 충분한 자원을 가진 공격자들에 맞서 단련되어 왔다. 그래서 리뷰 노력은 그 주변에 Anthropic이 새로 만든 부분으로 향했다. 뒤에서 다시 나오겠지만, 직접 만든 custom proxy가 가장 중대한 사고에서 깨진 바로 그 조각이기도 했다.

### 패턴 2: human-in-the-loop 샌드박스, Claude Code

Claude Code는 사용자의 머신에서 실행되며 파일시스템, shell, 네트워크에 접근한다. 이것 없이는 코딩 에이전트의 유용성이 제한되므로, 그 접근을 안전하게 부여하는 방법을 찾는 일이 필수적이다.

한 가지 접근은 human-in-the-loop에 의존하는 것이다. 이는 Claude Code에서만 그나마 다룰 수 있는 해법이다. 평균 사용자가 코딩 환경에 익숙한 개발자이기 때문이다. 이들은 bash를 읽을 수 있고, `rm -rf`가 무엇을 하는지 이해하며, 신뢰할 수 없는 출처에서 `npm install`을 이미 매주 여러 번 실행한다. 따라서 “이것을 허용할까요?” 대화상자가 뜨면, 에이전트가 무엇을 하려는지와 관련 위험을 비교적 정확하게 평가할 전문성을 가질 가능성이 높다. 이를 바탕으로 Claude Code는 가능한 가장 단순한 방어로 출시되었다. 읽기는 허용하고, 쓰기·bash·네트워크 접근에는 승인을 요구하는 방식이다.

그러나 앞서 말했듯 승인 피로는 [몇 주 만에 나타났다](https://www.reddit.com/r/ClaudeAI/comments/1rru8zw/just_picked_up_a_new_keyboard_cant_wait_to_write/). 아이러니하게도, 원래 감독을 제공하려고 설계된 기능이 오히려 반대 효과를 낼 수도 있다는 뜻이다. 일부 사용자는 단순히 주의를 기울이지 않게 된다. 부주의한 승인을 줄이기 위한 첫 단계로 Anthropic은 OS 수준 샌드박스(macOS의 Seatbelt, Linux의 bubblewrap)를 출시했다. 이 샌드박스는 경계를 강화한다. 읽기는 허용하고, workspace 내부의 쓰기는 허용하지만, 네트워크는 기본적으로 거부한다. 샌드박스 안에서 에이전트는 대부분 중단 없이 실행된다. 그 결과 권한 프롬프트가 84% 줄었고, Anthropic은 경계가 감사 가능하도록 [runtime을 오픈소스](https://github.com/anthropic-experimental/sandbox-runtime)로 공개했다.

Anthropic의 [익명화된 사용 데이터](https://www.anthropic.com/news/measuring-agent-autonomy)는 숙련 사용자가 신규 사용자보다 auto-approve를 약 두 배 자주 사용하지만, 동시에 실행 중인 에이전트를 더 자주 중단한다는 점도 보여 주었다. 숙련 사용자는 개별 단계를 gate하기보다 에이전트가 경로를 벗어났을 때만 감독하는 쪽을 선호하는 듯하다. 이것이 사람들이 에이전트와 일하는 방식의 자연스러운 진화일 수는 있지만, 이 역시 오류 가능성이 있다. 사용자가 애초에 drift를 알아차릴 만큼 충분히 기술적이고 주의를 기울여야 하기 때문이다. 모델 능력이 향상되고 에이전트가 점점 더 야심 찬 bash를 쓰기 시작하면 그런 drift를 알아차리기는 더 어려워진다. 사용자가 multi-agent system으로 이동하면 이 접근은 효과적인 감독 전략일 가능성이 훨씬 낮아진다.

#### 놓친 위험: trust dialog 이전의 모든 것

2025년 중반부터 2026년 1월 사이, Anthropic은 responsible disclosure 프로그램을 통해 Claude Code 취약점 제보를 받았다. 그중 세 건은 사용자가 아직 아무것도 동의하기 전에 실행되는 코드를 악용했다. 이것이 어떻게 가능한지 이해하려면 가장 직접적인 경우를 보자. 개발자가 pull request를 검토하려고 repository를 clone했는데, 그 repository 안에 hook을 정의한 `.claude/settings.json`이 들어 있다. Claude Code는 표준 “이 폴더를 신뢰합니까?” 프롬프트를 띄우기 전에 시작 과정에서 프로젝트 설정을 읽으므로, 공격자가 작성해 commit해 둔 hook이 자동으로 실행된다. 나머지 사례들도 구조적으로 비슷했다. 아직 신뢰되지 않은 디렉터리의 입력이 trust boundary가 설정되기 전에 parse되었다.

각 경우의 수정은 같은 형태였다. 사용자가 trust prompt를 수락한 뒤에야 project-local configuration의 parsing과 execution을 수행하도록 미루는 것이다. 비슷한 것을 만든다면 project-open, config-load, localhost listener를 인터넷에서 들어오는 inbound request처럼 다루어야 한다. 로컬처럼 느껴지고 사용자가 동의하기 전에 도착했다는 이유만으로 암묵적으로 신뢰해서는 안 된다.

#### 놓친 위험: injection vector로서의 사용자

2026년 2월, 통제된 내부 red-team exercise에서 한 연구자가 직원을 phish해 악성 prompt로 Claude Code를 실행하게 하는 데 성공했다. 이 phish는 평범한 협업처럼 보였다. “이거 실행해 줄 수 있나요?”라는 이메일과 붙여넣기만 하면 되는 prompt가 붙어 있었다. prompt 자체도 일상적인 작업 지시처럼 읽혔다. 하지만 설정 단계 어딘가에서 Claude에게 `~/.aws/credentials`를 읽고, 내용을 인코딩해 외부 endpoint로 POST하라고 부드럽게 요청했다. 그 prompt를 25번 재시도한 결과 Claude는 24번 exfiltration을 완료했다.

이것은 직접 prompt injection이다. 공격자의 지시가 도구 출력이나 가져온 콘텐츠가 아니라 사용자를 통해 도착했기 때문이다. Anthropic의 모델 계층 방어는 사용자 의도에 anchor한다. 사용자가 직접 지시를 입력한 경우 classifier가 잡아낼 비정상성이 없다. 같은 스크립트를 받은 인간 contractor도 똑같이 했을 것이다.

이 상황에서 버티는 유일한 방어는 환경이다. 구체적으로는 의도와 무관하게 POST를 차단하는 egress 제어와, 애초에 `~/.aws`를 접근 불가능하게 하는 파일시스템 경계다.

Anthropic이 토론을 위해 내부 Slack에 작동 prompt를 공유했을 때, 누군가 일부 내부 에이전트가 Slack을 읽는다는 점을 지적했다. 이제 payload는 주변 환경에 퍼져 있었다. Anthropic은 무엇인가가 그것을 집어 가면 알아차리기 위해 thread에 [canary string](https://www.fortinet.com/resources/cyberglossary/what-is-canary-in-cybersecurity)을 추가했다. 에이전트가 모든 것을 읽는 세계에서는 조사 도구도 공격 표면이다.

### 패턴 3: 로컬 VM, Claude Cowork

Claude Cowork는 사용자의 데스크톱에서 실행되며 사용자가 선택한 workspace folder에 접근한다. 이 플랫폼은 소프트웨어 엔지니어링이 아니라 일반 지식 작업을 위해 만들어졌기 때문에, 평균 사용자는 bash에 익숙할 가능성이 훨씬 낮다.

따라서 human-in-the-loop 샌드박스 전략은 그대로 옮겨지지 않을 수 있다. 비기술 지식 노동자가 `find . -name "*.tmp" -exec rm {} \;` 같은 bash 주문을 판단할 것으로 기대해서는 안 된다. 예외 승인에 일반 사용자가 갖고 있지 않은 전문성이 필요하다면, admin은 절대적이고 항상 켜져 있는 경계를 설정해야 한다.

이를 가능하게 하기 위해 Claude Cowork의 첫 버전은 플랫폼 vendor hypervisor(macOS의 Apple Virtualization framework, Windows의 HCS)를 사용하는 full virtual machine 안에서 실행되었다. VM은 자체 Linux kernel, 자체 파일시스템, 자체 process table을 가진다. 사용자가 선택한 workspace와 `.claude` folder만 mount되고, host의 다른 것은 보이지 않는다. credential은 host keychain에 머물며 guest machine 안으로 들어가지 않는다. 이 설계는 Claude가 언젠가 misaligned manner로 행동할 가능성에 대비한다. compromised Claude가 workspace folder 내부를 훼손할 수는 있지만, 아키텍처는 그것이 도달할 수 있는 유일한 범위가 workspace 내부가 되도록 설계되어 있다. 사용자가 connector를 추가하기 전까지는 그렇고, 무엇이 mount되는지도 사용자가 통제한다.

원래 아키텍처, Anthropic이 full-VM mode라고 부르는 방식에서는 agent loop 자체가 guest 안에서 실행되었으므로 Claude는 자신이 sandboxed되어 있다는 인식 없이 평범한 Linux user로 실행되었다. 이것을 Claude Code와 비교해 보자. Claude Code에서는 privileged process가 sandbox 바깥에 앉아 각 command마다 sandbox를 강제할지 결정한다. 설득력 있는 injected prompt나 피로한 approval click은 그 process가 무언가를 sandbox 밖에서 실행하게 할 수 있다. Cowork의 원래 설계에는 escape-hatch key를 쥐고 있는 외부 process가 없었고, 따라서 예외를 부여할 권한을 가진 component도 없었다.

![Claude Cowork VM의 여섯 가지 주요 격리 메커니즘. 둘은 guest kernel 바깥에서 강제되므로 에이전트가 VM 내부에서 root-level access를 얻더라도 유지된다. 나머지 넷은 guest-enforced이고, 외부 계층이 나머지를 담당하므로 의도적으로 최소화되어 있다.](https://www-cdn.anthropic.com/images/4zrzovbb/website/ffc97a876bdeba2031ddaeef79a954e9b1b2d52a-1920x1080.png)

그러나 곧 전체 에이전트를 full-VM mode로 실행하면 실무상 문제가 생긴다는 사실을 깨달았다. VM startup 중 실패가 발생하면 Cowork 전체가 사용할 수 없게 되었다. code execution은 VM 안에 유지하되 agent loop를 VM 바깥으로 옮기면, VM이 오류를 내더라도 Claude가 사용자에게 응답하고 디버깅을 도울 수 있다. 이 변화는 보안 영향이 작았다. 에이전트가 실행하는 code에 대해서는 여전히 VM이 파일시스템과 네트워크 제어를 강제하기 때문이다.

별도로 local MCP server도 VM 바깥으로 옮겼다. VM 안에서 실행하면 감사하기 어려웠고, VM 업데이트 때 dependency 문제가 취약해졌으며, database 같은 local process와 상호작용해야 하는 MCP를 지원하지 못했다. 그런 server는 어차피 host에서 실행되어야 했다. 이 변화는 Claude Cowork를 Claude Desktop에서 local MCP server가 이미 작동하는 방식과 맞춘다. 즉 사용자가 설치하기로 선택할 수 있는 다른 소프트웨어처럼 취급하고, 어떤 local MCP를 활성화할지 여부는 admin이 결정하도록 신뢰한다. Remote MCP server는 사용자의 머신에서 실행되지 않으므로 영향을 받지 않는다.

![VM 내부에 agent loop가 있으면 VM의 어떤 실패도 Cowork 전체를 사용할 수 없게 만든다. Host-mode는 VM이 crash해도 agent가 계속 응답할 수 있으므로 더 신뢰성이 높고, code execution을 격리함으로써 여전히 중요한 보안 보장을 제공한다.](https://www-cdn.anthropic.com/images/4zrzovbb/website/a81ed723d52f6fb2e7bc5ca51471496b1307101a-1920x1080.png)

파일시스템 제어도 중요한 아키텍처 선택이었다. Claude가 유용하려면 host의 일부 파일에는 접근할 수 있어야 하지만, Anthropic은 blast radius를 최소화하고 local file access에 관해 사용자에게 투명성을 제공하고 싶었다. 서로 다른 file-mount mode를 제공하면 위험을 세밀하게 제어할 수 있다는 점을 확인했다. Claude Cowork는 read-only, read-write, read-write-no-delete를 제공한다. 여기서 주의해야 할 점 하나는 symlink resolution이 path validation 이후가 아니라 이전에 일어나야 한다는 것이다. 그렇지 않으면 허가된 folder 안의 symlink가 바깥을 가리켜 escape할 수 있다. enterprise customer에게는 MDM 설정의 mount-path allowlist로 admin이 이를 제어할 수 있게 한다.

#### 놓친 위험: 승인된 domain을 통한 exfiltration

승인된 domain을 통한 exfiltration의 명확한 예는 서드파티 disclosure에서 나왔다. Claude Cowork의 egress allowlist는 `api.anthropic.com`으로 가는 traffic을 올바르게 통과시켰다. 제품은 Anthropic의 API를 호출하지 않고는 작동할 수 없다. 이 사례에서는 사용자의 mounted workspace에 놓인 악성 파일이 숨겨진 지시와 함께 공격자가 제어하는 API key를 포함하고 있었다. Claude는 그 지시에 따라 workspace 안의 다른 파일을 읽고, 공격자의 key를 사용해 Anthropic Files API를 호출했다. egress proxy는 목적지를 확인했고, `api.anthropic.com`을 보았으며, 통과시켰다. 파일은 공격자의 Anthropic account로 upload되었다. sandbox는 완벽하게 작동했지만, 데이터는 유출되었다.

이전에는 allowlist를 destination filter, 즉 Claude에게 “이 domain과 대화하는 것은 괜찮다”고 알려 주는 것으로 개념화했다. 하지만 capability grant로 개념화하는 편이 더 나을 수 있다. allowlist에 들어간 domain을 통해 도달 가능한 모든 function이 이제 공격 표면이다. `api.anthropic.com`을 허용한다는 것은 임의 Anthropic account로의 file upload를 허용한다는 뜻이었다.

Anthropic은 VM 내부의 방어적 man-in-the-middle proxy로 이를 수정했다. 이 proxy는 Anthropic API로 가는 traffic을 intercept한다. VM 자체에 provision된 session token을 가진 요청만 통과시키고, 공격자가 embedded한 key는 proxy가 거부한다. 또한 server-side fetch를 가능하게 하는 header도 차단한다. proxy가 server가 아니라 VM 안에 있는 이유는 provenance를 아는 곳이 VM뿐이기 때문이다. server 관점에서 Cowork request는 다른 API client와 구별되지 않는다.

![위: api.anthropic.com으로 향하는 traffic이 통과되어 egress가 발생한다. 아래: Anthropic API traffic을 intercept하는 man-in-the-middle proxy로 수정한다.](https://www-cdn.anthropic.com/images/4zrzovbb/website/beb481a2e7b314f73ba37821a2c1f1ca470d7063-1920x1080.png)

이것은 직접 만든 소프트웨어가 종종 가장 약하다는 원칙의 두 번째 사례이기도 하다. Anthropic 제품 전반의 hypervisor, seccomp, gVisor는 의존 가능했다. 실패한 조각은 custom allowlist proxy였다.

#### 놓친 위험: VM 격리가 endpoint detection software도 밖에 둠

Claude Cowork를 평가할 때 enterprise security team은 “왜 우리 EDR이 내부를 볼 수 없나요?”라고 물었다. 답은 Claude를 가두는 바로 그 격리가 host-based endpoint detection and response도 밖에 둔다는 것이었다. EDR 관점에서 Claude Cowork는 불투명한 hypervisor process다. guest를 inspect할 수 없다.

격리는 visibility를 줄이고, 불투명성은 endpoint visibility에 compliance posture가 의존하는 팀에게 문제다. Anthropic의 현재 완화책은 admin이 사후 event log를 가져올 수 있게 하는 pull-based [OTLP](https://opentelemetry.io/docs/specs/otel/protocol/) export이지만, 이것은 live monitoring과 같지 않다. 비슷한 것을 만든다면 이 대화를 일찍부터 예산에 넣어야 한다.

| 환경 | 임시 컨테이너, [claude.ai](http://claude.ai) | HITL 샌드박스, Claude Code | 봉인된 VM, Claude Cowork |
|---|---|---|---|
| 비용: 격리 overhead | Container spin-up | 저지연 native sandbox | Full VM boot |
| 비용: 사용자 의존 | N/A | bash를 해석해야 함 | N/A |
| 위험: blast radius | 서버 측 컨테이너, gVisor와 host infra boundary로 보호 | local workspace | mounted workspace, vsock과 hypervisor boundary로 보호 |

## 에이전트가 읽는 것을 신뢰하기

Enterprise는 종종 Anthropic에 MCP connection을 어떻게 안전하게 만들 수 있는지 묻는다. 좋은 질문이지만, 올바른 질문은 MCP만이 아니라 더 넓다. 에이전트에 제공되는 모든 외부 resource는 동시에 두 가지 위험을 나타낸다. 전통적 supply-chain 의미의 code execution risk와 prompt injection vector다. 전통적 dependency auditing, 즉 version pinning, signature verification, source review는 첫 번째를 다루지만 두 번째는 놓친다.

Remote와 local의 차이는 보이는 것보다 더 중요하다. 로컬에 설치된 도구는 감사할 수 있다. 코드를 읽고, version을 pin하고, 밑에서 바뀌지 않을 것임을 알 수 있다. Remote tool, 예를 들어 hosted MCP server나 cloud connector는 승인한 뒤 언제든 동작을 바꿀 수 있다. install-time trust decision이 더 이상 적용되지 않을 수 있다. Anthropic의 [connector directory](https://claude.com/connectors)는 지속적 review로 이를 다루지만, 그 밖의 것은 untrusted로 취급해야 한다. 먼저 fake data에 대해, 악성 도구의 blast radius가 가두어진 환경에서 실행하라.

도구가 trusted여도 tool output은 attack surface다. 앞서 언급한 GitHub README 예시는 정확히 이 경우다. web page에 적용되는 모든 input scanning은 network-enabled tool result에도 같은 엄격함으로 적용되어야 한다. 이것은 latency를 더하고 완벽한 방어도 아니지만, Anthropic은 live inspection 쪽을 택한다. 일단 오염된 tool return이 에이전트를 data exfiltration으로 유도하고 나면, log에는 성공한 authorized API call만 남는다. 사후에 찾을 신호가 없다.

Claude Code와 Claude Cowork에서 tool call은 network와 file policy를 강제하고 return value가 모델 context에 들어가기 전에 inspect할 수 있는 proxy를 통해 route된다. inspection을 수행하는 classifier는 작고 빠른 모델이면 된다. reasoning을 수행하는 모델일 필요는 없다.

## 앞으로

모델과 제품은 빠르게 발전하고 있다. 그에 따라 위험도 형태를 바꾸고 진화하며, 완화책도 그 속도를 따라잡아야 한다.

Persistent memory poisoning. 세션을 넘어 지속되는 agent context의 비중은 계속 커지고 있다. 여기에는 product memory, `CLAUDE.md` 파일, mounted workspace, scheduled agent와 long-running agent의 state directory가 포함된다. 이 중 어디든 injection이 들어가면 에이전트가 시작될 때마다 다시 load된다. 더 많은 agent state가 세션을 넘어 살아남을수록, 고전적 post-exploitation 의미에서 새로운 persistence mechanism의 위협을 받는다. session startup에서 좋은 classifier가 더 흔해져야 한다.

Multi-agent trust escalation. 한편으로 sub-agent는 untrusted content를 격리하고, raw text 대신 structured fact를 main agent에 돌려줄 수 있다. 다른 한편으로 이것은 악용될 수 있다. sub-agent output이 “우리”에게서 나온 것이라는 이유로 raw tool result보다 더 높은 trust로 취급된다면, prompt injection의 새로운 vector가 생긴다. Multi-agent system에서는 서로 다른 trust level을 배정하는 것과 trust escalation에 취약해지는 것 사이에 tradeoff가 있다.

Agent identity. Claude Cowork의 agent identity에 대한 답은 구체적이다. credential은 host keychain에 머물고, VM은 session마다 scope-down된 token을 받으며, 그 token은 사용자 token과 독립적으로 revoke될 수 있다. 그러나 Anthropic은 cross-platform agent identity라는 더 넓은 질문을 다루기 시작했다. 에이전트는 자기 자신의 principal identity를 가져야 하는가, 아니면 사용자의 확장으로 행동하며 사용자 권한을 상속해야 하는가? 궁극적으로 답은 둘의 혼합일 수 있다.

에이전트가 더 유능해질수록 attack surface는 계속 이동한다. Anthropic이 본 실패 유형은 업계와 연구소 전반에서 반복될 가능성이 높다. shared benchmark와 disclosure norm에서 common identity standard와 cross-vendor red-teaming에 이르기까지, 에이전트 특화 보안 태세에 대한 공동 투자가 필요하다. 이 글은 containment에 초점을 맞추지만, 그것은 에이전트 보안 그림의 한 부분일 뿐이다. governance, observability, 나머지 stack에 대해서는 [NIST의 AI agent identity and authorization project](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization), 호주 ACSC가 CISA와 영국 NCSC와 함께 주도한 [agentic AI service adoption에 관한 6개 기관 지침](https://media.defense.gov/2026/Apr/30/2003922823/-1/-1/0/CAREFUL%20ADOPTION%20OF%20AGENTIC%20AI%20SERVICES_FINAL.PDF), 그리고 AI management standard인 [ISO/IEC 42001](https://www.iso.org/standard/42001)을 보라. Anthropic의 Glasswing initiative는 하나의 기여이며, Anthropic은 이 중요한 문제에서 partner와 competitor 모두와 협력하기를 기대한다.

## 요약

짧게 말해, Anthropic이 계속 되돌아오는 원칙은 몇 가지다.

먼저 환경 계층에서 containment를 설계하고, 그다음 모델 계층에서 행동을 steer하라. Anthropic에 가장 많은 것을 가르쳐 준 두 사고, 즉 employee phish와 third-party allowlist disclosure는 모두 egress 사례였다. 데이터가 허용된 경로를 통해 나갔다. 두 경우 모두 모델 계층은 도움이 될 수 없었다. 잡아낼 비정상성이 없었기 때문이다. 모든 확률적 방어가 놓칠 때 맞닥뜨리는 것은 결정론적 경계다.

격리 강도를 사용자의 감독 능력에 맞추라. bash를 읽을 수 있는 개발자와 그렇지 않은 지식 노동자는 같은 threat model에서 움직이지 않는다. 사용자가 에이전트가 하려는 일을 평가할 수 있는지 여부는 containment strategy를 결정하는 데 도움이 되어야 한다. 이를 잘못 답하면 어느 방향으로든 실패가 된다. 전문가에게 너무 많은 friction을 주거나, 비전문가에게 너무 많은 trust를 주는 것 모두 실패다.

Custom component를 경계하라. battle-tested hypervisor, syscall filter, container runtime은 직접 만들 어떤 것보다 더 많은 적대적 관심을 견뎌 왔다. 여기서 설명한 모든 배포에서 standard primitive는 버텼고, 그 주변에 Anthropic이 만든 작업이 결함을 드러냈다.

결국 에이전트가 새로운 소프트웨어 범주일 수는 있지만, system-level interaction은 새롭지 않다. 에이전트는 여전히 file을 읽고, socket을 열고, process를 spawn한다. 이 때문에 성숙한 도구를 이용한 containment는 결정적으로 실현 가능한 방어다. AI가 발전하면서 배포의 위험-보상 균형은 계속 이동하겠지만, blast radius에 단단한 상한을 두면 그 균형은 종종 올바른 방향으로 강제된다.

### 감사의 말

Max McGuinness, Mikaela Grace, Jiri De Jonghe, Jake Eaton, Abel Ribbink가 작성했다.

또한 기여해 준 Hanah Ho, Hasnain Lakhani, Pedram Navid, Molly Villagra, Maya Nielan, Akila Srinivasan, Travis Szucs, Sam Attard, Alfred Xing, Mohamad El Hajj, Gabby Curtis, David Dworken, Adam Jones, Amie Rotherham, Christian Ryan, Lucas Smedley, Brett Andrews 및 여러 사람에게 감사한다.

Anthropic의 security team과 product engineering team, 그리고 Claude 제품의 취약점을 제보해 준 개인과 조직에도 특별히 감사한다.

#### 각주

1. Claude Code auto mode는 command approval을 model-based classifier에 위임한다. 약 0.4%의 benign command를 block하는 수준으로 friction을 최소화하는 대신, risky action의 일부를 놓친다. 과도하게 적극적인 행동의 약 17%가 통과한다. 따라서 이것은 sandbox 내부의 defense-in-depth 한 계층이지 sandbox의 대체물이 아니다.
