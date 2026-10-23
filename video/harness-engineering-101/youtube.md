에이전트는 while 루프다, 300줄 코딩 에이전트 직접 만들기 1편 에이전트의 뼈대 (Isuru Wijesiri)
태그: AI 에이전트 만들기, 코딩 에이전트, 하니스, 하니스 엔지니어링, 에이전트 루프, 도구 호출, 함수 호출, 프롬프트 캐싱, 컨텍스트 윈도우, 클로드 API, 앤트로픽 API, 파이썬 에이전트, LLM 에이전트, 에이전트 실습, 핸즈온, 따라 하기, 클로드 코드 원리, 에이전트 프레임워크, 랭체인 없이, 서브에이전트, AI 개발, Harness Engineering 101, Isuru Wijesiri, harness engineering, AI agent from scratch, agent loop, tool use, function calling, prompt caching, Anthropic API, Claude, Python, LLM agent tutorial, hands-on, One Code, WSO2, 듣는편람

코딩 에이전트는 안에서 어떻게 돌아갈까요? 프레임워크 없이, 파이썬 백 줄로 직접 만들어 보면 답이 보입니다. 채팅 API 호출을 while 루프로 감싼 것, 그게 에이전트입니다.

WSO2에서 코딩 도우미를 세 개 만든 Isuru Wijesiri의 공개 책 "Harness Engineering 101"을 따라 하는 핸즈온 강의 1편입니다. 책의 장난감 하니스(MIT 라이선스)를 실제 API로 돌리며 여섯 수업을 진행합니다. 30줄 채팅을 만들어 서버가 아무것도 기억하지 않는 것을 확인하고, 세션 JSON을 손으로 고쳐 모델이 배열에 적힌 것을 그대로 믿는 것을 봅니다. 도구를 붙여 모델은 부탁만 하고 실행은 내 코드가 한다는 것을 확인하고, 한 턴에 도구 한 번만 돌리면 왜 HTTP 400이 나는지도 겪어 봅니다. 그다음 for 루프 하나를 더해 실패한 테스트를 스스로 고치는 에이전트를 만들고, 도구 오류를 삼켰을 때와 그대로 돌려줬을 때를 나란히 비교합니다. 마지막으로 프롬프트 캐싱을 켜고 cache_read_input_tokens가 바퀴마다 자라는 것을 본 뒤, 시스템 프롬프트 맨 위에 현재 시각 한 줄을 넣어 캐시가 0으로 떨어지는 것을 확인합니다. 터미널 화면은 실제 실행 기록을 그대로 다시 그린 것이고, 그 아래 코드에서 지금 그 출력을 만든 줄이 함께 켜집니다. 모션 그래픽 다섯 편으로 배열이 자라는 모습, 루프의 흐름, 캐시 적중 비교를 보여 드립니다.

이런 분께 맞습니다
- Claude Code나 Cursor를 매일 쓰지만 그 속이 어떻게 생겼는지 궁금한 개발자
- 에이전트 프레임워크의 낯선 용어에 지쳐 바닥부터 이해하고 싶은 분
- API 비용이 왜 이렇게 나오는지, 캐시가 왜 안 맞는지 직접 재 보고 싶은 분

{챕터}

원문(영어): https://github.com/IsuruMaduranga/harness-engineering-101
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/harness-engineering-101/
실습 코드와 실행 기록: https://github.com/yoon-gu/compendium/tree/master/video/harness-engineering-101/lab
함께 보기, AI 에이전트는 도구를 하나씩 부르지 말고 코드로 묶어 불러야 한다(Codemode 해설): https://youtu.be/lzKaQiJ6_dU

화면 자료 출처: 코드는 원문 저장소의 장난감 하니스(MIT)이고, 터미널 출력은 2026년 10월 20일 claude-haiku-5-5로 실제 실행한 기록입니다. 그림과 애니메이션은 그 실측값으로 새로 그렸습니다. 책 본문은 CC BY-NC-ND 4.0이라 문장을 옮기지 않고 우리 말로 다시 설명했습니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Qwen3-TTS, 소희)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#AI에이전트 #코딩에이전트 #하니스엔지니어링
