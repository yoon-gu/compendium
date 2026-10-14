에이전트가 코드를 쓰면 git이 병목이 된다, Anthropic이 Scion을 만든 이유 (Anthropic)
태그: 소스 컨트롤, 버전 관리, 깃, 모노레포, CI, 지속적 통합, 개발 인프라, 개발자 생산성, AI 에이전트, 코딩 에이전트, AI 코딩, 클로드, 앤트로픽, 사이온, 체크아웃, 병합 큐, 캐시, 분산 시스템, 백엔드, 소프트웨어 엔지니어링, 플랫폼 엔지니어링, DevOps, 개발 문화, Anthropic, Claude, Claude Code, Scion, Antique, git, monorepo, source control, version control, CI/CD, merge queue, sparse checkout, shallow clone, content addressed storage, Spanner, Piper, Sapling, GitHub, GitLab, agentic coding, developer infrastructure, 코드 리뷰, 사내 도구, 에이전트 인프라, code review, Claude Tag, internal tools, 듣는편람

AI 에이전트가 코드를 쓰기 시작하면 무엇이 먼저 무너질까요? Anthropic에서는 git이었습니다. 하루 병합 변경이 다섯 달 만에 2,500건에서 3만 건으로 늘자, 사람 속도에 맞춰 만든 소스 컨트롤과 CI가 병목이 됐습니다.

Anthropic 엔지니어링 블로그 "Redesigning source control at Anthropic"을 10장면으로 풀어 읽습니다. 모노레포, 분산 git, CI 체크아웃이 무엇인지부터 짚고, 하루 600PB가 넘는 git 트래픽 계산(25GB × 2,500만 회), "클라이언트는 늘 온라인"이라는 전제에서 나온 원칙 여섯 가지, git 커밋 대신 바뀐 파일만 적는 체인지셋과 비교 후 교환(CAS), 캐시 적중률 99%의 3층 캐시 구조를 다룹니다. 일곱 명이 다섯 달 만에 옮긴 결과(인프라 1/200, 체크아웃 분 → 초)와 함께 엔지니어의 일이 Claude에게 "아니오"라고 말하는 쪽으로 바뀐 이야기, 구성 요소마다 붙은 '슈퍼팬' Claude, 병합 큐 대신 병합 뒤 복구를 택한 이유까지 짚습니다. 애니메이션 네 편으로 병합량 증가, 전부 받기와 읽는 것만 받기, 3층 캐시, 병합 큐와 병합 뒤 복구를 보여 드립니다.

이런 분께 맞습니다
- 코딩 에이전트를 팀에 들이면서 CI·빌드·리뷰가 막히기 시작한 개발자와 플랫폼 엔지니어
- 대형 모노레포의 git 성능과 체크아웃 비용으로 고민하는 분
- AI 시대에 개발 인프라와 엔지니어의 역할이 어떻게 바뀌는지 궁금한 분

{챕터}

원문(영어): https://www.anthropic.com/engineering/redesigning-source-control
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/redesigning-source-control/
함께 보기, 안 보면 AGI다(GPT 6 Astra에게 35시간 코딩을 맡긴 기록): https://youtu.be/Yqb3h5GK60U

화면의 그림과 애니메이션은 원문 그림을 쓰지 않고 새로 그렸습니다. 애니메이션의 점 개수와 비율은 원리를 보여 주려는 개념 그림이고, 성능 수치는 Anthropic이 직접 잰 값입니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#AI에이전트 #git #개발인프라
