#!/usr/bin/env python3
"""실습 프로그램을 가짜 터미널(pty)에서 돌리며 입력·출력을 시각과 함께 기록한다. 영상의 터미널 클립 원본.

    python3 run_lesson.py <이름> --cwd <폴더> --input "첫 줄" --input "둘째 줄" -- python3 l1_chat.py s.json

- 프로그램이 `you> ` 프롬프트를 띄우면 다음 --input 줄을 넣는다. 입력이 다 떨어지면 `/quit`.
- `--input "@wait 60"` 은 60초 동안 아무것도 치지 않는다(수업 10: 그 사이 하니스가 스스로 모델을 깨우는지 본다).
- 기록: runs/<이름>.jsonl — 한 줄에 {"t": 초, "k": "cmd"|"in"|"out", "s": 글자}. 실제 출력만 담고 고치지 않는다.
- 환경 변수: ANTHROPIC_API_KEY 는 ~/.config/anthropic-key.txt 에서 읽어 넘긴다.
"""
import json
import os
import pty
import select
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = b"you> "


def main():
    args = sys.argv[1:]
    name = args.pop(0)
    inputs, cwd, env_extra = [], HERE, {}
    while args and args[0] != "--":
        a = args.pop(0)
        if a == "--input":
            inputs.append(args.pop(0))
        elif a == "--cwd":
            cwd = Path(args.pop(0)).resolve()
        elif a == "--env":
            k, v = args.pop(0).split("=", 1)
            env_extra[k] = v
    assert args and args[0] == "--", "명령 앞에 -- 를 둔다"
    cmd = args[1:]
    inputs.append("/quit")

    env = dict(os.environ, **env_extra)
    env["ANTHROPIC_API_KEY"] = (Path.home() / ".config/anthropic-key.txt").read_text().strip()
    env["PYTHONUNBUFFERED"] = "1"
    out = HERE / "runs" / f"{name}.jsonl"
    out.parent.mkdir(exist_ok=True)
    log = out.open("w", encoding="utf-8")
    t0 = time.time()

    def rec(k, s):
        log.write(json.dumps({"t": round(time.time() - t0, 3), "k": k, "s": s}, ensure_ascii=False) + "\n")
        log.flush()

    rec("cmd", " ".join(cmd))
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.execvpe(cmd[0], cmd, env)
    buf, wait_until = b"", 0.0
    while True:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                break
            if not data:
                break
            text = data.decode("utf-8", errors="replace")
            sys.stdout.write(text); sys.stdout.flush()
            rec("out", text)
            buf = (buf + data)[-64:]
        if buf.endswith(PROMPT) and inputs and inputs[0].startswith("@wait"):
            wait_until = time.time() + float(inputs.pop(0).split()[1])
        if buf.endswith(PROMPT) and inputs and time.time() >= wait_until:
            line = inputs.pop(0)
            time.sleep(0.4)
            rec("in", line)
            os.write(fd, (line + "\n").encode())
            buf = b""
    os.waitpid(pid, 0)
    rec("end", "")
    print(f"\n[run_lesson] {out}")


if __name__ == "__main__":
    main()
