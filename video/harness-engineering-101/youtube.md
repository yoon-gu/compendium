에이전트는 while 루프다, 300줄 코딩 에이전트 직접 만들기 1편 에이전트의 뼈대 (Isuru Wijesiri)
태그: 코딩 에이전트 만들기, AI 에이전트 만들기, 에이전트 직접 만들기, 코딩 에이전트, 하니스 엔지니어링, 에이전트 루프, while 루프, 도구 호출, 함수 호출, 프롬프트 캐싱, 컨텍스트 윈도우, 클로드 API, 앤트로픽 API, 파이썬 에이전트, LLM 에이전트, 에이전트 실습, 핸즈온 강의, 클로드 코드 원리, 랭체인 없이, AI 코딩, 개발자 강의, Harness Engineering 101, Isuru Wijesiri, harness engineering, AI agent from scratch, build an AI agent, agent loop, tool use, function calling, prompt caching, Anthropic API, Claude API, Claude Haiku, Python, coding agent, LLM agent tutorial, hands-on, 듣는편람

코딩 에이전트는 안에서 어떻게 돌아갈까요? Claude Code 같은 AI 코딩 에이전트를 프레임워크 없이 파이썬 백 줄로 직접 만들며 그 원리를 확인합니다.
에이전트는 채팅 API 호출을 while 루프로 감싼 것입니다. 이 한 문장을 실제 실행으로 하나씩 보여 드리는 핸즈온 강의 1편입니다.

WSO2에서 코딩 도우미를 세 개 만든 Isuru Wijesiri의 공개 책 "Harness Engineering 101"을 교재로 삼았습니다. 책에 실린 장난감 하니스(MIT 라이선스)를 Anthropic API의 Claude Haiku로 실제로 돌렸고, 화면의 터미널은 그 실행 기록을 글자 그대로 다시 그린 것입니다. 터미널 아래에서는 지금 그 출력을 만든 코드 줄이 함께 켜집니다.

이 영상에서 하는 것
- 수업 0 준비물: 파이썬 3.10과 API 키만 있으면 됩니다. 설치할 패키지는 없고, 모델 이름 한 줄만 바꿉니다.
- 수업 1 30줄 채팅: 서버는 아무것도 기억하지 않습니다. 대화 배열이 턴마다 2,589바이트에서 4,362바이트로 자라고, /clear 는 messages = [] 한 줄입니다.
- 수업 2 세션 파일: 저장된 JSON에서 모델의 지난 답을 손으로 고치면, 모델은 그 말을 자기가 한 것으로 믿습니다.
- 수업 3 도구 붙이기: 도구 정의(스키마)와 디스패치 표를 만듭니다. 모델은 부탁만 하고 실행은 내 코드가 합니다. 자주 만나는 HTTP 400 오류의 원인도 짚습니다.
- 수업 4 에이전트 루프: for 루프 하나를 더해, 21개를 10개씩 나누면 3쪽이어야 하는데 2쪽이 나오는 실패한 테스트를 에이전트가 스스로 고칩니다. 모델이 바퀴마다 한 말과 고친 한 줄, 그렇게 고칠 수 있었던 이유를 차근차근 따라갑니다.
- 수업 5 오류 돌려주기: 도구 오류를 그대로 돌려준 판은 도구 호출 9번에 끝났고, 오류를 빈 문자열로 삼킨 판은 12번을 헤맸습니다.
- 수업 6 비용 재기: 프롬프트 캐싱을 켜면 cache_read 가 633, 1,068, 1,768, 2,254로 자라고, 시스템 프롬프트 맨 위에 현재 시각 한 줄을 넣으면 0으로 떨어집니다.

이런 분께 맞습니다
- Claude Code나 Cursor를 매일 쓰지만 그 속이 어떻게 생겼는지 궁금한 개발자
- 에이전트 프레임워크의 낯선 용어에 지쳐 바닥부터 이해하고 싶은 분
- 내 에이전트의 API 비용이 왜 이렇게 나오는지, 캐시가 왜 안 맞는지 직접 재 보고 싶은 분
- 파이썬은 읽을 줄 알고, LLM API를 한 번이라도 불러 본 분

{챕터}

원문(영어): https://github.com/IsuruMaduranga/harness-engineering-101
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/harness-engineering-101/
실습 코드와 실행 기록: https://github.com/yoon-gu/compendium/tree/master/video/harness-engineering-101/lab
함께 보기, AI 에이전트는 도구를 하나씩 부르지 말고 코드로 묶어 불러야 한다(Codemode 해설): https://youtu.be/lzKaQiJ6_dU

화면 자료 출처: 코드는 원문 저장소의 장난감 하니스(MIT)이고, 터미널 출력은 2026년 10월 claude-haiku-5-5로 실제 실행한 기록입니다. 그림과 애니메이션은 그 실측값으로 새로 그렸습니다. 책 본문은 CC BY-NC-ND 4.0이라 문장을 옮기지 않고 우리 말로 다시 설명했습니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#AI에이전트 #코딩에이전트 #하니스엔지니어링
