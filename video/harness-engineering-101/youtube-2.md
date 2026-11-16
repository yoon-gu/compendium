에이전트를 무너뜨리는 건 도구 결과다, 300줄 코딩 에이전트 직접 만들기 2편 예산과 서브에이전트 (Isuru Wijesiri)
태그: 코딩 에이전트 만들기, AI 에이전트 만들기, 서브에이전트, 컨텍스트 윈도우, 컨텍스트 엔지니어링, 컨텍스트 열화, 토큰 예산, 도구 결과 자르기, 하니스 엔지니어링, 에이전트 루프, 클로드 API, 파이썬 에이전트, LLM 에이전트, 에이전트 실습, 핸즈온 강의, 클로드 코드 원리, AI 코딩, 개발자 강의, Harness Engineering 101, Isuru Wijesiri, harness engineering, subagent, context window, context engineering, context rot, truncation, prompt too long, AI agent from scratch, agent loop, Claude API, Claude Haiku, Python, coding agent, hands-on, 듣는편람

에이전트에게 긴 일을 맡기면 왜 무너질까요? 서브에이전트는 언제 쓰고 무엇을 아껴 줄까요?
파이썬으로 만든 코딩 에이전트에 2.3MB짜리 빌드 로그를 읽혀 보면, 도구 결과 한 번에 컨텍스트 윈도우가 넘쳐 API가 호출을 거절합니다. 그 자리를 직접 고치는 핸즈온 강의 2편입니다.

WSO2에서 코딩 도우미를 세 개 만든 Isuru Wijesiri의 공개 책 "Harness Engineering 101"을 교재로 삼았습니다. 책의 장난감 하니스(MIT 라이선스)를 Anthropic API의 Claude Haiku로 실제로 돌렸고, 화면의 터미널은 그 실행 기록을 글자 그대로 다시 그린 것입니다. 터미널 아래에서는 지금 그 출력을 만든 코드 줄이 함께 켜집니다.

이 영상에서 하는 것
- 수업 7 컨텍스트 예산: 로그를 통째로 읽으면 배열이 2,331,535바이트가 되고, 1,267,285 토큰이 100만 토큰 한도를 넘어 HTTP 400이 납니다. 예산을 다 먹은 건 시스템 프롬프트도 질문도 아닌 도구 결과 하나였습니다.
- 도구 결과 자르기: 2만 자에서 머리와 꼬리만 남기고, 잘랐다는 표시와 원본 파일 경로를 붙입니다. 같은 질문에 배열은 20,873바이트에 그치고, 모델은 저장된 파일을 grep으로 다시 뒤져 로그 한가운데 묻힌 ModuleNotFoundError를 찾아냅니다.
- 자주 막히는 곳: 표시 없이 말없이 자르면 모델은 로그가 끊겼다고 추측할 뿐 원인을 찾지 못합니다.
- 수업 8 서브에이전트: 빈 배열에서 같은 루프를 한 번 더 돌리는 것이 전부입니다. 부모 배열은 57,052바이트에서 38,515바이트로 줄지만, 입력 토큰 합계는 36,558에서 134,816으로 늘어납니다. 돈을 더 내고 부모의 작업 기억을 아끼는 거래입니다.
- 일감 쓰는 법: 자식은 부모 대화를 전혀 모릅니다. 위치를 빠뜨렸더니 컴퓨터 전체를 뒤지기 시작한 첫 시도와, 좋은 일감에 들어갈 네 가지를 봅니다.

이런 분께 맞습니다
- 에이전트가 긴 작업 중에 "prompt is too long"으로 멈추거나 앞의 내용을 잊어버리는 문제를 겪는 개발자
- Claude Code의 서브에이전트가 정확히 무엇을 아껴 주는지, 비용은 얼마나 드는지 숫자로 보고 싶은 분
- 컨텍스트 엔지니어링을 말이 아니라 코드 몇 줄로 이해하고 싶은 분
- 1편을 보셨거나, 파이썬과 LLM API를 한 번이라도 다뤄 본 분

{챕터}

원문(영어): https://github.com/IsuruMaduranga/harness-engineering-101
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/harness-engineering-101/
실습 코드와 실행 기록: https://github.com/yoon-gu/compendium/tree/master/video/harness-engineering-101/lab
함께 보기, 1편 에이전트는 while 루프다: https://youtu.be/HMMcNYNLxEI

화면 자료 출처: 코드는 원문 저장소의 장난감 하니스(MIT)이고, 터미널 출력은 2026년 10월 claude-haiku-5-5로 실제 실행한 기록입니다. 그림과 애니메이션은 그 실측값으로 새로 그렸습니다. 책 본문은 CC BY-NC-ND 4.0이라 문장을 옮기지 않고 우리 말로 다시 설명했습니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#AI에이전트 #서브에이전트 #하니스엔지니어링
