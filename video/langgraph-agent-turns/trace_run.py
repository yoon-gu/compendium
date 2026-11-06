"""agent.py 를 실제로 돌리며 (1) agent.py 안에서 실행된 줄 (2) 노드별 상태 갱신을 시간순으로 trace.json 에 남긴다."""
import json, os, sys, threading, time
from pathlib import Path

os.environ.setdefault("ANTHROPIC_API_KEY", (Path.home() / ".config/anthropic-key.txt").read_text().strip())
sys.path.insert(0, str(Path(".").resolve()))
SRC = str(Path("agent.py").resolve())
events, t0 = [], time.time()

def tracer(frame, event, arg):
    if frame.f_code.co_filename != SRC:
        return None
    if event == "line":
        events.append({"t": round(time.time() - t0, 3), "kind": "line", "line": frame.f_lineno,
                       "fn": frame.f_code.co_name})
    return tracer

sys.settrace(tracer); threading.settrace(tracer)
import agent  # noqa: E402  (등록 단계의 줄도 기록된다)

def msg(m):
    d = {"type": m.type, "content": m.content if isinstance(m.content, str) else
         " ".join(b.get("text", "") for b in m.content if isinstance(b, dict))}
    if getattr(m, "tool_calls", None):
        d["tool_calls"] = [{"name": c["name"], "args": c["args"]} for c in m.tool_calls]
    if m.type == "tool":
        d["name"] = m.name
    return d

for upd in agent.app.stream({"messages": [("user", "다음 주 서울 여행 메모 써 줘")]}, stream_mode="updates"):
    for node, val in upd.items():
        events.append({"t": round(time.time() - t0, 3), "kind": "update", "node": node,
                       "messages": [msg(m) for m in val["messages"]]})
sys.settrace(None); threading.settrace(None)
Path("trace.json").write_text(json.dumps(events, ensure_ascii=False, indent=1))
print(sum(e["kind"] == "update" for e in events), "updates,", len(events), "events")
for e in events:
    if e["kind"] == "update":
        print(e["node"], json.dumps(e["messages"], ensure_ascii=False)[:300])
