from pathlib import Path
from typing import Annotated, TypedDict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

SKILLS = {p.parent.name: p for p in Path("skills").glob("*/SKILL.md")}

@tool
def load_skill(name: str) -> str:
    """스킬 본문(SKILL.md)을 읽어 온다."""
    return SKILLS[name].read_text()

@tool
def get_weather(city: str) -> dict:
    """도시의 현재 날씨(예시 데이터)."""
    return {"city": city, "temp_c": 18, "sky": "맑음, 오후 소나기"}

@tool
def c_to_f(celsius: float) -> float:
    """섭씨를 화씨로 바꾼다."""
    return round(celsius * 9 / 5 + 32, 1)

tools = [load_skill, get_weather, c_to_f]
llm = ChatAnthropic(model="claude-sonnet-5-5").bind_tools(tools)
system = SystemMessage("쓸 수 있는 스킬: travel-memo — "
                       "여행지 날씨를 메모로 정리. 쓰기 전에 load_skill로 읽어라.")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def agent(state: State):
    reply = llm.invoke([system] + state["messages"])
    return {"messages": [reply]}

def route(state: State):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", route, ["tools", END])
graph.add_edge("tools", "agent")
app = graph.compile()

if __name__ == "__main__":
    out = app.invoke({"messages": [("user", "다음 주 서울 여행 메모 써 줘")]})
    print(out["messages"][-1].content)
