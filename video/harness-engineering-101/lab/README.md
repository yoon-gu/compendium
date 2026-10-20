# 실습 폴더

- `harness/`: Isuru Wijesiri의 *Harness Engineering 101* 장난감 하니스 원본 사본 (MIT, `harness/LICENSE`).
  출처: https://github.com/IsuruMaduranga/harness-engineering-101 커밋 745c433, `src/harness/`
- `sample-project/`: 수업용 예제. `page_count`에 일부러 심은 off-by-one 버그가 있어 테스트 1개가 실패한다.

API 키는 `~/.config/anthropic-key.txt`에서 읽는다(저장소에 두지 않는다).

    export ANTHROPIC_API_KEY="$(cat ~/.config/anthropic-key.txt)"
