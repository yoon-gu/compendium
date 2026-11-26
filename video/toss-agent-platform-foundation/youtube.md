에이전트에게 내부망을 다 열 수는 없다, 망분리 환경에서 실행은 가두고 대화는 잇는 에이전트 플랫폼 (토스)
태그: 토스 테크 블로그, 에이전트 플랫폼, AI 에이전트, 사내 AI 에이전트, 망분리, 금융 보안, 샌드박스, 에이전트 보안, 하니스, 하니스 엔지니어링, 쿠버네티스, 파드 격리, 리눅스 네임스페이스, 인증정보 관리, API 키 보안, 세션 관리, 영속 볼륨, 데이터 분석 자동화, 플랫폼 엔지니어링, Toss, agent platform, AI agent sandbox, agent harness, bubblewrap, OpenSandbox, Kubernetes, Linux namespace, egress policy, credential proxy, MCP, OpenResponses, persistent volume, 에이전트 권한 관리, 데이터 반출 방지, 전자금융감독규정, LLM 에이전트, 사내 데이터 분석, agent security, sandboxing, least privilege, session resume, 듣는편람

에이전트에게 회사 데이터를 맡긴다면 어디까지 열어 줘야 할까요? 어제 하던 분석을 오늘 이어 가게 하려면 무엇을 남겨 둬야 할까요?
토스 AI Platform Team의 글 "실행은 격리하고, 세션은 이어간다: 망분리 환경의 Agent Platform 설계기"를 12장면으로 풀어 읽습니다. 데이터를 밖으로 옮길 수 없는 망분리 환경에서 에이전트가 내부망 안에서 직접 코드를 돌리게 한 설계입니다.

모델이 쓴 코드를 실행하는 하니스를 사용자별 파드 안에서 bubblewrap으로 에이전트마다 따로 가둡니다. 파일은 필요한 폴더만 열고 참고 자료는 읽기 전용, 네트워크는 프록시 하나로만, 권한은 낮추고 울타리를 못 세우면 아예 실행하지 않습니다. API 키는 하니스에 대체값만 주고 나가는 길에 프록시가 진짜 키로 바꿔 끼웁니다. 파드가 바뀌어도 이어 가도록 작업 파일과 대화 상태를 영속 볼륨에 남기고, 하니스 고유 상태와 공통 실행 기록을 왜 따로 두는지까지 짚습니다. 막는 것과 검증하는 것, 키를 숨기는 것과 권한을 줄이는 것이 어떻게 다른지, 원문이 스스로 적어 둔 한계도 함께 봅니다.

이런 분께 맞습니다
- 사내 데이터에 AI 에이전트를 붙이려는 플랫폼·보안 엔지니어
- 에이전트 샌드박스와 인증정보 관리를 설계하는 개발자
- 금융·공공처럼 망분리 규정 아래에서 AI를 도입하려는 팀

{챕터}

원문: https://toss.tech/article/agent-platform-foundation
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/toss-agent-platform-foundation/
함께 보기, 300줄로 직접 만드는 코딩 에이전트와 하니스: https://youtu.be/HMMcNYNLxEI

화면의 그림과 애니메이션은 원문 그림을 쓰지 않고 새로 그렸습니다(Remotion).

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#토스 #AI에이전트 #샌드박스
