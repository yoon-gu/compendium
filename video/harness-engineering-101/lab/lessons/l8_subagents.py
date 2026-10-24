#!/usr/bin/env python3
"""Harness v4: subagents. The agent loop, called as a function.

Chapter 7 of Harness Engineering 101. 수업 7(자르기·범위 읽기·캐시·배열 크기)을 그대로 두고 agent 도구를 더했다.
    python3 l8_subagents.py              # 서브에이전트 있음
    python3 l8_subagents.py --no-agent   # 같은 코드에서 agent 도구만 뺀 판(비교용)
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-haiku-5-5"
MAX_ROUNDS = 50
MAX_RESULT_CHARS = 20_000
USE_AGENT = "--no-agent" not in sys.argv                         # 수업 8: 비교용 스위치
HERE = os.getcwd()
OUTSIDE = re.compile(r"(^|[\s;&|(])(~|\$HOME)|/Users/|find\s+/(\s|$)|cd\s+/(\s|;|&|$)")   # 실습 안전장치: 프로젝트 밖을 뒤지지 않게

MAIN_SYSTEM = ("You are a capable engineering agent working on the local "
               "machine. Use your tools to complete the user's task. "
               "Reply in the user's language. "
               f"Your working directory {HERE} is the project root; stay inside it."
               + (" Delegate self-contained searches and research to the agent "
                  "tool to keep your own context small." if USE_AGENT else ""))
SUB_SYSTEM = ("You are a focused subagent. Complete the task you were "
              "given using your tools, then end with a clear, "
              "self-contained report of your findings. Cite file paths. "
              f"Your working directory {HERE} is the project root; stay inside it.")

BASE_TOOLS = [
    {"name": "read_file",
     "description": ("Read a text file. For big files pass offset (1-based "
                     "line) and limit (number of lines)."),
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"},
                                     "offset": {"type": "integer"},
                                     "limit": {"type": "integer"}},
                      "required": ["path"]}},
    {"name": "write_file",
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

AGENT_TOOL = {                                                   # 수업 8: 맡기는 도구
    "name": "agent",
    "description": ("Delegate a self-contained task to a subagent with its "
                    "own fresh context. It can read files and run commands, "
                    "and returns only its final answer. Use it for searches "
                    "and research whose details you don't need to keep. "
                    "The subagent knows NOTHING about this conversation, so "
                    "include all necessary background in the task, and ask "
                    "for file paths and line numbers so you don't need to "
                    "re-check its work."),                          # 수업 8: 근거를 요구한다
    "input_schema": {"type": "object",
                     "properties": {"task": {"type": "string"}},
                     "required": ["task"]},
}

MAIN_TOOLS = BASE_TOOLS + ([AGENT_TOOL] if USE_AGENT else [])
SUB_TOOLS = BASE_TOOLS                                           # 수업 8: 손자는 없다
SPENT = {"parent": 0, "sub": 0}                                  # 수업 8: 입력 토큰 장부


def call_llm(messages, tools, system, who):
    msgs = json.loads(json.dumps(messages))
    last = msgs[-1]
    if isinstance(last["content"], str):
        last["content"] = [{"type": "text", "text": last["content"]}]
    last["content"][-1]["cache_control"] = {"type": "ephemeral"}
    body = {"model": MODEL, "max_tokens": 8192,
            "system": [{"type": "text", "text": system,
                        "cache_control": {"type": "ephemeral"}}],
            "messages": msgs, "tools": tools}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json",
                 "x-api-key": API_KEY,
                 "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req) as resp:
            reply = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        msg = json.loads(e.read()).get("error", {}).get("message", "")
        print(f"\n[harness] HTTP {e.code}: {msg}")
        return None
    u = reply.get("usage", {})
    SPENT[who] += (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                   + u.get("cache_read_input_tokens", 0))
    return reply


def truncate(text):
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


def execute_tool(name, args, allow_agent):
    try:
        if name == "read_file":
            lines = open(args["path"]).read().splitlines(keepends=True)
            off, lim = int(args.get("offset", 1)), int(args.get("limit", 0))
            return truncate("".join(lines[off - 1:off - 1 + lim] if lim else lines))
        if name == "write_file":
            with open(args["path"], "w") as f:
                f.write(args["content"])
            return f"wrote {len(args['content'])} bytes to {args['path']}"
        if name == "run_command":
            if OUTSIDE.search(args["command"]):
                return "BLOCKED: stay inside the project folder (the current directory)."
            out = subprocess.run(args["command"], shell=True,
                                 capture_output=True, text=True, timeout=120)
            return truncate(out.stdout + out.stderr) or "(no output)"
        if name == "agent" and allow_agent:                      # 수업 8
            return run_subagent(args["task"])
        return f"ERROR: unknown tool {name}"
    except Exception as e:
        return f"ERROR: {e}"


def run_loop(messages, tools, system, quiet=False, allow_agent=False):
    """Chapter 4's agent loop, now reusable. Returns the final text."""
    final_text = ""
    who = "sub" if quiet else "parent"
    for _ in range(MAX_ROUNDS):
        reply = call_llm(messages, tools, system, who)
        if reply is None:
            return final_text
        messages.append({"role": "assistant", "content": reply["content"]})
        for block in reply["content"]:
            if block["type"] == "text" and block["text"].strip():
                final_text = block["text"]
                if not quiet:
                    print(f"\nassistant> {block['text']}")

        if reply["stop_reason"] != "tool_use":
            return final_text

        results = []
        for block in reply["content"]:
            if block["type"] == "tool_use":
                tag = "    [sub]" if quiet else "[tool]"
                print(f"{tag} {block['name']}({json.dumps(block['input'], ensure_ascii=False)[:100]})")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": execute_tool(block["name"], block["input"],
                                            allow_agent),
                })
        messages.append({"role": "user", "content": results})
    return final_text


def run_subagent(task):
    """A subagent IS the agent loop, run over a fresh array."""
    sub_messages = [{"role": "user", "content": task}]           # 수업 8: 빈 배열에서 시작
    final_text = run_loop(sub_messages, tools=SUB_TOOLS,
                          system=SUB_SYSTEM, quiet=True)
    print(f"    [sub] done: {len(sub_messages)} messages, "
          f"{len(json.dumps(sub_messages)):,} bytes -> thrown away")   # 수업 8
    return final_text or "(subagent returned no answer)"         # 수업 8: 이것만 살아남는다


def main():
    messages = []
    while True:
        user_text = input("\nyou> ").strip()
        if user_text in ("/quit", ""):
            break
        messages.append({"role": "user", "content": user_text})
        run_loop(messages, tools=MAIN_TOOLS, system=MAIN_SYSTEM,
                 allow_agent=True)
        print(f"\n  [array] parent: {len(messages)} messages, {len(json.dumps(messages)):,} bytes")   # 수업 8
        print(f"  [tokens] parent_in={SPENT['parent']:,} sub_in={SPENT['sub']:,}")


if __name__ == "__main__":
    main()
