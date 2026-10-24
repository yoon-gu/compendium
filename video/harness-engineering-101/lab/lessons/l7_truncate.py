#!/usr/bin/env python3
"""Harness v3 + 수업 6 캐시 + 수업 7: 배열 크기를 재고, 거절되면 이유를 보여 준다.

Chapter 6 of Harness Engineering 101: truncate at the source, say so, read ranges.
"""
import json
import time
import os
import subprocess
import sys
import urllib.error
import urllib.request

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-haiku-5-5"
SYSTEM = ("You are a capable engineering agent working on the local machine. "
          "Use your tools to complete the user's task, then summarize what "
          "you did. Reply in the user's language.")                # 2편: 대답은 사용자 말로
SYSTEM_TEXT = lambda: SYSTEM                                      # 수업 6: 늘 같은 바이트
MAX_ROUNDS = 50                                      # NEW: runaway-loop cap
MAX_RESULT_CHARS = 20_000                                     # 수업 7: 도구 결과 하나의 상한
SILENT = "--silent" in sys.argv                               # 수업 7: 말없이 자르는 나쁜 판

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
     "description": "Run a shell command and return stdout+stderr.",
     "input_schema": {"type": "object",
                      "properties": {"command": {"type": "string"}},
                      "required": ["command"]}},
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


def truncate(text):
    """수업 7: 머리와 꼬리만 남기고, 잘랐다고 말하고, 전체는 파일에 둔다."""
    if len(text) <= MAX_RESULT_CHARS:
        return text
    keep = MAX_RESULT_CHARS // 2
    if SILENT:
        return text[:keep] + text[-keep:]
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
            return truncate("".join(lines[off - 1:off - 1 + lim] if lim else lines))
        if name == "write_file":
            with open(args["path"], "w") as f:
                f.write(args["content"])
            return f"wrote {len(args['content'])} bytes to {args['path']}"
        if name == "run_command":
            out = subprocess.run(args["command"], shell=True,
                                 capture_output=True, text=True, timeout=120)
            return truncate(out.stdout + out.stderr) or "(no output)"   # 수업 7
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
        messages.append({"role": "user", "content": results})
    print("\n[harness] hit MAX_ROUNDS, stopping this turn")


def main():
    messages = []
    while True:
        user_text = input("\nyou> ").strip()
        if user_text in ("/quit", ""):
            break
        messages.append({"role": "user", "content": user_text})
        run_turn(messages)


if __name__ == "__main__":
    main()
