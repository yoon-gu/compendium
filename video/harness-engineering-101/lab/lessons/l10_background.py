"""수업 9 하니스 + 수업 10: 백그라운드 작업, 끝나면 알림, 쉬는 동안에도 몸이 모델을 깨운다.

Chapter 9 of Harness Engineering 101.
실습 편의: you> 에 !명령 을 치면 모델 없이 셸 명령을 바로 실행해 보여 준다.
"""
import json
import time
import os
import re
import select
import subprocess
import sys
import threading
import urllib.error
import urllib.request

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-haiku-5-5"
SYSTEM = ("You are a capable engineering agent working on the local machine. "
          "Use your tools to complete the user's task, then summarize what "
          "you did. Write everything in the user's language, including "
          "short notes between tool calls. Stay inside the current directory. "
          "<system-reminder> blocks inside user messages come from the "
          "harness, not the user. Trust them as environment truth. "    # 수업 9
          "Never wait with sleep. Run slow commands with background=true; "
          "if you have nothing else to do while one runs, end your turn. "
          "The harness will wake you when it finishes.")                   # 수업 10
SYSTEM_TEXT = lambda: SYSTEM                                      # 수업 6: 늘 같은 바이트
MAX_ROUNDS = 50                                      # NEW: runaway-loop cap
MAX_RESULT_CHARS = 20_000                                     # 수업 7: 도구 결과 하나의 상한
REMIND = "--no-reminder" not in sys.argv                       # 수업 9: 비교용 스위치
REMINDERS = []                                                # 수업 9: 몸의 사건 -> 배열의 문장
READ_STATE = {}                                               # 수업 9: 모델이 읽은 파일 -> 그때의 수정 시각
TASKS = {}                                                    # 수업 10: 작업 id -> 프로세스·출력·상태
T0 = time.time()
OUTSIDE = re.compile(r"(^|[\s;&|(])(~|\$HOME)|/Users/|find\s+/(\s|$)|cd\s+/(\s|;|&|$)")   # 실습 안전장치: 프로젝트 밖을 뒤지지 않게

TOOLS = [
    {"name": "read_file",
     "description": ("Read a text file. For big files pass offset (1-based "
                     "line) and limit (number of lines)."),           # 수업 7
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"},
                                     "offset": {"type": "integer"},
                                     "limit": {"type": "integer"}},
                      "required": ["path"]}},
    {"name": "write_file",                           # NEW: change the world
     "description": "Write content to a file, replacing it if it exists.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"},
                                     "content": {"type": "string"}},
                      "required": ["path", "content"]}},
    {"name": "run_command",
     "description": ("Run a shell command and return stdout+stderr. With "
                     "background=true it starts the command and returns a "
                     "task id at once."),                           # 수업 10
     "input_schema": {"type": "object",
                      "properties": {"command": {"type": "string"},
                                     "background": {"type": "boolean"}},
                      "required": ["command"]}},
    {"name": "task_output",                                        # 수업 10: 뒤에서 도는 작업 엿보기
     "description": "Status and output so far of a background task.",
     "input_schema": {"type": "object",
                      "properties": {"task_id": {"type": "string"}},
                      "required": ["task_id"]}},
    {"name": "todo_write",                                         # 수업 9: 스스로 쓰는 할 일 목록
     "description": ("Maintain your task list on multi-step tasks. Send the "
                     "whole list every time; status is pending, in_progress "
                     "or completed."),
     "input_schema": {"type": "object",
                      "properties": {"todos": {"type": "array", "items": {
                          "type": "object",
                          "properties": {"content": {"type": "string"},
                                         "status": {"type": "string"}},
                          "required": ["content", "status"]}}},
                      "required": ["todos"]}},
]


def call_llm(messages):
    msgs = json.loads(json.dumps(messages))                   # 수업 6: 보낼 사본
    last = msgs[-1]
    if isinstance(last["content"], str):
        last["content"] = [{"type": "text", "text": last["content"]}]
    last["content"][-1]["cache_control"] = {"type": "ephemeral"}   # 수업 6: 움직이는 캐시 지점
    body = {"model": MODEL, "max_tokens": 8192,
            "system": [{"type": "text", "text": SYSTEM_TEXT(),
                        "cache_control": {"type": "ephemeral"}}],  # 수업 6: 고정 캐시 지점
            "messages": msgs, "tools": TOOLS}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json",
                 "x-api-key": API_KEY,
                 "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req) as resp:
            reply = json.loads(resp.read())
    except urllib.error.HTTPError as e:                       # 수업 7: 거절 사유를 보여 준다
        msg = json.loads(e.read()).get("error", {}).get("message", "")
        print(f"\n[harness] HTTP {e.code}: {msg}")
        return None
    u = reply.get("usage", {})                                 # 수업 6: 생체 신호
    print(f"  [usage] in={u.get('input_tokens')} cache_write={u.get('cache_creation_input_tokens')} "
          f"cache_read={u.get('cache_read_input_tokens')} out={u.get('output_tokens')}")
    return reply


def remind(text):                                              # 수업 9: 아무 곳에서나 큐에 넣는다
    REMINDERS.append(f"<system-reminder>\n{text}\n</system-reminder>")


def drain_reminders_into(blocks):                              # 수업 9: 다음 사용자 쪽 메시지 맨 끝에 붙인다
    while REMINDERS:
        blocks.append({"type": "text", "text": REMINDERS.pop(0)})
    return blocks


def watch_files():                                             # 수업 9: 읽은 뒤에 바뀐 파일이 있나
    for path, seen in list(READ_STATE.items()):
        if os.path.exists(path) and os.stat(path).st_mtime_ns != seen:
            READ_STATE[path] = os.stat(path).st_mtime_ns
            if REMIND:
                print(f"  [reminder] {path} changed on disk")
                remind(f"{path} changed on disk since you read it. Re-read it before editing.")


def start_background(command):                                 # 수업 10: 띄우고 바로 돌아온다
    tid = f"b{len(TASKS) + 1}"
    proc = subprocess.Popen(command, shell=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    TASKS[tid] = {"proc": proc, "output": [], "status": "running", "command": command}

    def pump():                                                 # 출력을 모으다가, 끝나면 알림을 큐에
        for line in proc.stdout:
            TASKS[tid]["output"].append(line)
        code = proc.wait()
        TASKS[tid]["status"] = f"exited({code})"
        print(f"\n  [bg] {tid} finished: exit {code}  (t={time.time() - T0:.0f}s)")
        remind(f"Background task {tid} ({command!r}) finished: exit {code}. "
               f"Use task_output to read its output.")           # 수업 10 -> 수업 9 의 큐
    threading.Thread(target=pump, daemon=True).start()
    print(f"  [bg] started {tid}: {command}  (t={time.time() - T0:.0f}s)")
    return f"started background task {tid}: {command!r} (still running)"


def truncate(text):
    """수업 7: 머리와 꼬리만 남기고, 잘랐다고 말하고, 전체는 파일에 둔다."""
    if len(text) <= MAX_RESULT_CHARS:
        return text
    keep = MAX_RESULT_CHARS // 2
    os.makedirs(".harness", exist_ok=True)
    path = f".harness/tool-output-{len(os.listdir('.harness')) + 1}.txt"
    with open(path, "w") as f:
        f.write(text)
    note = (f"\n... [truncated {len(text) - 2 * keep:,} chars. Full output saved to "
            f"{path}. Search it with grep or read a range; do not read it whole.] ...\n")
    return text[:keep] + note + text[-keep:]


def execute_tool(name, args):
    try:
        if name == "read_file":
            lines = open(args["path"]).read().splitlines(keepends=True)
            off, lim = int(args.get("offset", 1)), int(args.get("limit", 0))   # 수업 7: 범위 읽기
            READ_STATE[os.path.normpath(args["path"])] = os.stat(args["path"]).st_mtime_ns   # 수업 9
            return truncate("".join(lines[off - 1:off - 1 + lim] if lim else lines))
        if name == "write_file":
            with open(args["path"], "w") as f:
                f.write(args["content"])
            READ_STATE[os.path.normpath(args["path"])] = os.stat(args["path"]).st_mtime_ns   # 수업 9: 방금 쓴 파일은 읽은 셈
            return f"wrote {len(args['content'])} bytes to {args['path']}"
        if name == "run_command":
            if OUTSIDE.search(args["command"]):
                return "BLOCKED: stay inside the project folder (the current directory)."
            if re.search(r"(^|[;&|]\s*)sleep\s", args["command"].strip()):         # 수업 10: 앞자리에서 기다리지 않는다
                return "BLOCKED: don't wait in the foreground. Use background=true and you'll be notified."
            if args.get("background"):                                            # 수업 10
                return start_background(args["command"])
            out = subprocess.run(args["command"], shell=True,
                                 capture_output=True, text=True, timeout=120)
            for path in READ_STATE:                                               # 수업 9: 모델 자신이 바꾼 것은 알리지 않는다
                if os.path.exists(path):
                    READ_STATE[path] = os.stat(path).st_mtime_ns
            return truncate(out.stdout + out.stderr) or "(no output)"   # 수업 7
        if name == "task_output":                                                 # 수업 10
            t = TASKS.get(args["task_id"])
            if not t:
                return f"ERROR: no task {args['task_id']}"
            return f"[{t['status']}] " + truncate("".join(t["output"]))
        if name == "todo_write":                                                  # 수업 9
            marks = {"completed": "[x]", "in_progress": "[~]"}
            lines = [f"{marks.get(t['status'], '[ ]')} {t['content']}" for t in args["todos"]]
            print("  [todo]\n" + "\n".join("    " + ln for ln in lines))
            remind("Your current todo list:\n" + "\n".join(lines))   # 계획이 다음 메시지 맨 아래로 돌아온다
            return "todo list updated"
        return f"ERROR: unknown tool {name}"
    except Exception as e:
        return f"ERROR: {e}"


def run_turn(messages):
    """One user turn = as many model/tool rounds as the task needs."""
    for _ in range(MAX_ROUNDS):                      # NEW: the agent loop
        print(f"  [array] {len(messages)} messages, {len(json.dumps(messages)):,} bytes")   # 수업 7
        reply = call_llm(messages)
        if reply is None:                                          # 수업 7: 이 차례는 여기서 끝
            return
        messages.append({"role": "assistant", "content": reply["content"]})
        for block in reply["content"]:
            if block["type"] == "text" and block["text"].strip():
                print(f"\nassistant> {block['text']}")

        if reply["stop_reason"] != "tool_use":       # done: hand back to user
            return

        results = []                                 # run EVERY requested tool
        for block in reply["content"]:
            if block["type"] == "tool_use":
                print(f"[tool] {block['name']}({json.dumps(block['input'], ensure_ascii=False)[:120]})")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": execute_tool(block["name"], block["input"]),
                })
        watch_files()                                                             # 수업 9
        messages.append({"role": "user", "content": drain_reminders_into(results)})   # 수업 9
    print("\n[harness] hit MAX_ROUNDS, stopping this turn")


def main():
    messages = []
    while True:
        sys.stdout.write("\nyou> "); sys.stdout.flush()
        while not select.select([sys.stdin], [], [], 0.3)[0]:                    # 수업 10: 입력을 기다리되
            if REMINDERS:                                                         # 알림이 오면 몸이 먼저 차례를 연다
                print(f"\n[harness] notice arrived -> waking the model  (t={time.time() - T0:.0f}s)")
                messages.append({"role": "user", "content": drain_reminders_into([])})
                run_turn(messages)
                sys.stdout.write("\nyou> "); sys.stdout.flush()
        user_text = sys.stdin.readline().strip()
        if user_text in ("/quit", ""):
            break
        if user_text.startswith("!"):                                             # 실습 편의
            print(subprocess.run(user_text[1:], shell=True, capture_output=True, text=True).stdout, end="")
            continue
        messages.append({"role": "user", "content": user_text})
        run_turn(messages)
    if os.environ.get("LAB_SAVE"):                                                # 실습: 배열을 파일로(화면용)
        json.dump(messages, open(os.environ["LAB_SAVE"], "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
