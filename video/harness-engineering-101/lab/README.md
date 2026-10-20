# 실습 폴더

- `harness/`: Isuru Wijesiri의 *Harness Engineering 101* 장난감 하니스 원본 사본 (MIT, `harness/LICENSE`).
  출처: https://github.com/IsuruMaduranga/harness-engineering-101 커밋 745c433, `src/harness/`
- `lessons/`: 수업용 변형. 원본에서 모델 한 줄과 `# 수업 N` 표시가 붙은 줄만 다르다.
  | 파일 | 바탕 | 수업 | 더한 것 |
  |---|---|---|---|
  | `l1_chat.py` | v1 | 1·2 | 턴마다 배열 크기 출력, 세션을 JSON 파일로 저장·복원 |
  | `l3_tools.py` | v2 | 3 | (모델만) |
  | `l4_agent.py` | v3 | 4·5 | (모델만) |
  | `l5_agent_silent.py` | v3 | 5 | 도구 예외를 빈 문자열로 삼키는 나쁜 판 |
  | `l6_agent_cache.py` | v3 | 6 | `cache_control` 두 지점 + 바퀴마다 `usage` 출력 |
  | `l6_agent_cachebust.py` | v3 | 6 | 위와 같되 시스템 프롬프트 맨 위에 현재 시각 한 줄 |
- `sample-project/`: 수업용 예제. `page_count`에 일부러 심은 off-by-one 버그가 있어 테스트 1개가 실패한다.
- `run_lesson.py`: 실습 프로그램을 pty에서 돌리며 입력·출력을 시각과 함께 `runs/<이름>.jsonl`에 기록한다. 영상의 터미널 클립(`../figures/terminal.py`)은 이 기록을 글자 그대로 다시 그린 것이다.
- `runs/`: 실제 API 호출 기록(2026-10-20, claude-haiku-5-5). `work-*/`는 실행 중 고쳐진 예제 사본이라 커밋하지 않는다.

API 키는 `~/.config/anthropic-key.txt`에서 읽는다(저장소에 두지 않는다).

    export ANTHROPIC_API_KEY="$(cat ~/.config/anthropic-key.txt)"

실행 예:

    python3 run_lesson.py l1-chat --cwd runs --input "안녕하세요." --input "제 이름이 뭐죠?" -- python3 ../lessons/l1_chat.py l1-session.json
