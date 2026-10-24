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
  | `l7_budget.py` | v3 | 7 | 수업 6 + 바퀴마다 배열 크기, 거절되면 `HTTP 400` 사유 출력 |
  | `l7_truncate.py` | v3 | 7 | + `truncate()`(머리·꼬리, 잘랐다는 표시, 전체는 `.harness/`에 저장), `read_file` 범위 읽기. `--silent`는 말없이 자르는 나쁜 판 |
  | `l8_subagents.py` | v4 | 8 | 위 + `agent` 도구, 부모·자식 입력 토큰 장부. `--no-agent`는 비교용 |
  | `l9_reminders.py` | v4 | 9 | 리마인더 큐, 읽은 파일 감시, `todo_write`. `--no-reminder`는 비교용, `LAB_HUMAN_EDIT`는 사람이 끼어들어 고치는 연출 |
  | `l10_background.py` | v4 | 10 | 작업 표, `run_command(background)`, `task_output`, 앞자리 `sleep` 차단, 쉬는 동안 알림이 오면 몸이 모델을 깨움 |
- `sample-project/`: 수업용 예제. `page_count`에 일부러 심은 off-by-one 버그가 있어 테스트 1개가 실패한다.
- `sample-project2/`, `minishop/`: 2편 예제. `make_samples.py`가 만든다(시드 고정). `sample-project2/logs/build.log`(2.3MB, 하이쿠 입력 한도 1M 토큰을 넘는다)는 커밋하지 않으니 이 스크립트로 다시 만든다.
- 2편 녹화는 `/tmp/he101/`에 예제를 복사하고 `lessons`를 링크해서 돌렸다(화면에 집 경로가 찍히지 않게). l8 이후 하니스는 프로젝트 밖을 뒤지는 명령(`~`, `/Users/`, `find /`)을 막는다.
- `run_lesson.py`: 실습 프로그램을 pty에서 돌리며 입력·출력을 시각과 함께 `runs/<이름>.jsonl`에 기록한다. 영상의 터미널 클립(`../figures/terminal.py`)은 이 기록을 글자 그대로 다시 그린 것이다.
- `runs/`: 실제 API 호출 기록(2026-10-20, claude-haiku-5-5). `work-*/`는 실행 중 고쳐진 예제 사본이라 커밋하지 않는다.

API 키는 `~/.config/anthropic-key.txt`에서 읽는다(저장소에 두지 않는다).

    export ANTHROPIC_API_KEY="$(cat ~/.config/anthropic-key.txt)"

실행 예:

    python3 run_lesson.py l1-chat --cwd runs --input "안녕하세요." --input "제 이름이 뭐죠?" -- python3 ../lessons/l1_chat.py l1-session.json
