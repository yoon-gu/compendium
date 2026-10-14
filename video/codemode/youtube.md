Armin Ronacher의 Codemode 해설, AI 에이전트는 도구를 코드로 묶어 불러야 한다
태그: Armin Ronacher, 아르민 로나허, Codemode, 코드모드, Code Mode, MCP, MCP 서버, 엠씨피, AI 에이전트, 코딩 에이전트, 도구 호출, 툴 호출, 함수 호출, 에이전트 하니스, 컨텍스트 엔지니어링, 컨텍스트 윈도우, 토큰 절약, 샌드박스, 클로드 코드, 클라우드플레어, what is codemode, Pi agent, model context protocol, MCP server, tool calling, function calling, agent harness, context engineering, Cloudflare Code Mode, QuickJS, progressive discovery, Claude Code, AI agents, Flask, 듣는편람

AI 에이전트에 MCP 서버를 붙일수록 왜 더 느리고 헷갈려질까요? Flask를 만든 아르민 로나허는 모델에게 도구 수십 개를 보여 주는 대신, 도구 하나 안에서 코드를 쓰게 하라고 말합니다.

아르민 로나허의 글 "What is Codemode"를 12장면으로 풀어 읽습니다. 도구 호출·하니스·MCP가 무엇인지부터 짚고, 모델과 백 번 왕복하던 일을 스크립트 한 편으로 끝내는 Codemode의 구조, GitHub 이슈 100개를 읽고 12줄만 돌려주는 예시, QuickJS와 WebAssembly로 가둔 샌드박스, 하니스(뇌)와 실행 환경(손)의 구분, 그리고 지금의 MCP 서버와 부딪히는 "Codemode 안의 Codemode" 문제와 저자가 MCP에 바라는 네 가지까지 다룹니다.

이런 분께 맞습니다
- MCP 서버와 도구를 붙이다 컨텍스트가 넘쳐 고민인 에이전트 개발자
- Claude Code 같은 코딩 에이전트가 안에서 어떻게 도구를 부르는지 궁금한 분
- 도구 호출 대신 코드 실행으로 에이전트를 설계하는 흐름을 따라가고 싶은 분

{챕터}

원문(영어): https://lucumr.pocoo.org/2026/10/6/codemode/
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/codemode/
함께 보기, 코딩용 Astra, 우리는 왜 또 이러고 있나: https://youtu.be/Yqb3h5GK60U

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#AI에이전트 #MCP #Codemode
