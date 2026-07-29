---
title: "LangGraph와 Strands를 AgentCore에 올린 시장 감시 agent"
date: 2026-07-28
draft: false
source_url: "https://aws.amazon.com/blogs/machine-learning/market-surveillance-agent-with-langgraph-and-strands-on-agentcore/"
author: "Gleb Geinke, Efren Faderanga, Siddhesh Tiwari, Wang Teng Lee"
tags: ["AI", "Agents", "AWS", "LangGraph", "Strands", "AgentCore", "Financial Services"]
summary: "AWS 글은 시장 감시(market surveillance) use case를 예로 들어 LangGraph를 macro-level workflow orchestration에, Strands를 node 내부 reasoning engine에, Amazon Bedrock AgentCore를 managed runtime과 memory/observability layer에 배치하는 hybrid multi-agent architecture를 설명한다. 핵심은 deterministic graph orchestration과 localized LLM reasoning을 분리해 production reliability와 flexible analysis를 함께 얻는 것이다."
---

> **원문:** [Market surveillance agent with LangGraph and Strands on AgentCore](https://aws.amazon.com/blogs/machine-learning/market-surveillance-agent-with-langgraph-and-strands-on-agentcore/) — Gleb Geinke, Efren Faderanga, Siddhesh Tiwari, Wang Teng Lee, 2026-07-28
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다. Code, framework 이름, AWS service 이름, API 이름, agent/workflow 용어는 practitioner가 읽기 쉬운 English form을 유지했다.

AI application이 단순한 chatbot에서 정교한 autonomous system으로 진화하면서, 조직은 real-world production scenario를 처리할 수 있는 복잡한 multi-agent workflow를 orchestrate해야 하는 새로운 과제에 직면한다. 전통적인 single-agent 접근은 specialized expertise, dynamic decision-making, robust error recovery mechanism을 요구하는 복잡한 business process를 다룰 때 한계가 드러나는 경우가 많다. Financial services industry가 이 문제를 잘 보여준다. Market surveillance system은 trading pattern을 분석하고, suspicious activity를 조사하고, comprehensive report를 생성하기 위해 여러 specialized agent를 조율해야 하며, 동시에 strict compliance와 reliability standard를 유지해야 한다.

이 solution은 두 framework를 결합한다. Macro-level workflow orchestration에는 [LangGraph](https://www.langchain.com/langgraph)를, intelligent agent reasoning에는 [Strands](https://strandsagents.com/)를 사용한다. LangGraph는 multi-agent coordination을 위한 state와 directed graph 관리에 강하다. Workflow execution과 agent 사이에 공유되는 state를 fine-grained하게 제어할 수 있다. Central persistence layer는 production에 중요한 feature, 예를 들어 human-in-the-loop interaction과 checkpoint-based failure recovery를 지원한다. 반면 Strands Agent는 individual workflow node 안에서 reasoning engine 역할을 한다. Strands는 여러 large language model(LLM) provider와 통합되는 model-agnostic capability를 제공하면서도 flexible tool integration과 comprehensive observability를 유지한다.

지난해 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)가 출시되면서, 여러 use case에서 agentic solution의 productionization이 단순해질 수 있다. 이 조합은 complex use case를 처리하면서 enterprise application이 요구하는 infrastructure reliability와 observability를 제공하는 production-ready agentic AI system의 기반이 된다.

이 글에서는 AWS infrastructure 위에서 LangGraph와 Strands를 사용해 multi-agent AI system을 설계하고 deploy하는 방법을 보여준다. LangGraph checkpoint system으로 state-driven workflow orchestration을 구현하고, specialized reasoning task에 Strands agent를 통합하며, scalable production deployment를 위해 AgentCore를 사용하는 방법을 다룬다. Complete solution은 [GitHub](https://github.com/aws-samples/sample-langgraph-strands-market-analysis)에 공개되어 있다.

## Strands: Intelligent agent reasoning

Strands Agent는 model-agnostic architecture 위에서 동작하며, 특정 architecture constraint를 강요하지 않고 기존 infrastructure에 맞게 적응한다. Agent는 tool output을 계속 평가하고 intermediate result에 따라 decision을 내리는 agentic reasoning loop를 구현한다. 따라서 sophisticated multi-step analysis workflow를 만들 수 있다. Framework에는 comprehensive session/state management와 여러 conversation manager가 포함되어 있어 context window가 overflow되지 않게 돕는다.

Strands에서는 tool schema와 access pattern을 정의해 external tool interaction을 구성할 수 있다. 이 surveillance agent에서는 hallucination을 피하고 injection attack에 대한 solution의 강건성을 높이기 위해, data discovery와 retrieval을 분리한다. `get_report_list`와 `get_report_schema` 같은 tool로 report를 찾고, `run_report`로 validated parameter를 사용해 SQL query를 만들고 실행한다.

`security_monitor` agent는 다음 tool과 system prompt로 만든다.

```python
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name="us-east-1",
    max_tokens=16000,
    additional_request_fields={
        "thinking": {"type": "adaptive", "budget_tokens": 8000},
    },
    cache_prompt="default",
)

@tool
def get_report_list(agent_name: str) -> str:
    """Load the list of available reports for a specific agent.

    Args:
        agent_name: Name of the agent (e.g. 'security_monitor').

    Returns:
        str: JSON array of report objects with name and description.
    """
    reports_data = load_agent_reports(agent_name)
    return json.dumps(reports_data["reports"], indent=2)

@tool
def get_report_schema(report_name: str, query_intent: str) -> str:
    """Load column definitions for a report so you can build queries.

    Args:
        report_name: Name of the report (e.g. 'TradeActivity').
        query_intent: Description of what data to extract.

    Returns:
        str: JSON object with parameters and column definitions.
    """
    return json.dumps(load_json_report_definition(report_name), indent=2)

@tool
def run_report(
    report_name: str,
    filters: Dict[str, Any],
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Run a predefined report. The tool validates every filter against the
    report's schema and builds a parameterised SQL query. The LLM never writes
    raw SQL, so filter values cannot be injected into the query.

    Args:
        report_name: A report from `get_report_list` (e.g. 'TradeActivity').
        filters: Equality filters keyed by column name, e.g.
            {"symbol": "AAPL", "date": "2024-03-15"}.
        limit: Optional row cap (1..10000).

    Returns:
        dict: {'success': bool, 'data': str (CSV), 'error': str or None}
    """
    schema = load_json_report_definition(report_name)
    allowed_columns = {c["name"] for c in schema["columns"]}

    # Reject any filter field that is not in the report's allowed list of columns.
    unknown = set(filters) - allowed_columns
    if unknown:
        raise ValueError(
            f"Unknown filter field(s) {sorted(unknown)} for {report_name}. "
            f"Allowed: {sorted(allowed_columns)}"
        )

    # Build SQL with named bind parameters.
    where = " AND ".join(f"{field} = :{field}" for field in filters)
    sql = f"SELECT * FROM {schema['reportName']}"
    if where:
        sql += f" WHERE {where}"
    if limit is not None:
        if not isinstance(limit, int) or not 1 <= limit <= 10_000:
            raise ValueError("limit must be an integer in [1, 10000]")
        sql += f" LIMIT {limit}"

    return query_market_data(report_name=report_name, sql=sql, bind=filters)

security_monitor = Agent(
    model=model,
    system_prompt=SECURITY_MONITOR_PROMPT,
    tools=[get_report_list, get_report_schema, run_report],
    name="security_monitor",
)
```

## LangGraph: Macro workflow orchestration

LangGraph는 세 가지 core capability를 통해 multi-agent system을 위한 production-grade orchestration을 제공한다. 이 capability들이 LangGraph를 complex AI workflow에 잘 맞게 만든다.

Graph-based state machine: LangGraph는 agent workflow를 directed graph로 model한다. Node는 agent logic을 포함하는 function을 나타내고, edge는 execution flow를 결정한다. 이 declarative approach는 복잡한 multi-step reasoning을 읽기 쉽고 유지보수 가능한 code로 바꾼다. Graph는 conditional branching, parallel execution, dynamic routing을 지원한다. 이런 capability는 intermediate result에 따라 workflow가 적응해야 하는 real-world scenario에서 중요하다.

Persistent state management: Framework의 checkpoint system은 node execution 이후마다 complete workflow state를 자동 snapshot한다. 이 checkpoint를 사용하면 failure에서 부드럽게 recover하고 human-in-the-loop interaction을 지원할 수 있다. Analyst가 intermediate result를 review해야 하거나 error가 발생하면, system은 정확한 checkpoint에서 restore한다. 그런 다음 이전 work를 잃지 않고 resume한다. 이 stateful architecture는 multi-turn conversation, iterative refinement, 몇 시간 또는 며칠에 걸친 long-running investigation 같은 흔한 pattern을 지원한다.

Production reliability: LangGraph에는 system에서 발생할 수 있는 throttling이나 다른 failure를 처리하기 위한 exponential backoff 기반 retry strategy가 내장되어 있다. 또한 OpenTelemetry를 통한 comprehensive observability를 제공해 대부분의 observability application과 쉽게 통합된다.

이제 specialist Strands agent 사이에서 query를 route하는 orchestration layer를 만든다. 다음 code는 workflow graph를 정의한다. Shared state, 어떤 specialist agent를 invoke할지 선택하는 orchestrator, agent 사이 conditional routing, recovery와 human-in-the-loop review를 위한 checkpoint-backed persistence를 포함한다.

```python
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import END, StateGraph
from langgraph_checkpoint_aws import AgentCoreMemorySaver

class AgentState(TypedDict):
    query_text: str
    session_id: Optional[str]
    agent_task_map: Optional[Dict[str, str]]
    required_agents: Optional[List[str]]
    current_agent_index: Optional[int]
    # Each specialist writes its insights here
    security_monitor_insights: Optional[Dict[str, Any]]
    broker_monitor_insights: Optional[Dict[str, Any]]
    risk_monitor_insights: Optional[Dict[str, Any]]
    intel_analyst_insights: Optional[Dict[str, Any]]
    synthesizer_insights: Optional[str]

SPECIALIST_NODES = {
    "security_monitor": security_monitor_node,
    "broker_monitor": broker_monitor_node,
    "risk_monitor": risk_monitor_node,
    "intel_analyst": intel_analyst_node,
}

def route_analysts(state: AgentState) -> str:
    """Dynamic routing --- walk the required_agents list by index."""
    required = state.get("required_agents", [])
    index = state.get("current_agent_index", 0)
    if not required:
        return END
    if index < len(required):
        return required[index]
    return "synthesizer"

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
for name, node_fn in SPECIALIST_NODES.items():
    workflow.add_node(name, node_fn)
workflow.add_node("synthesizer", synthesizer_node)
workflow.set_entry_point("orchestrator")

# Conditional edges --- the orchestrator and every specialist route through route_analysts, which can hand off to any specialist or the synthesizer.
ALL_TARGETS = {name: name for name in SPECIALIST_NODES} | {
    "synthesizer": "synthesizer",
    END: END,
}
workflow.add_conditional_edges("orchestrator", route_analysts, ALL_TARGETS)
for name in SPECIALIST_NODES:
    workflow.add_conditional_edges(name, route_analysts, ALL_TARGETS)
workflow.add_edge("synthesizer", END)

# AgentCoreMemorySaver checkpoints the state after every node
checkpointer = AgentCoreMemorySaver(MEMORY_ID, region_name=REGION)
graph = workflow.compile(checkpointer=checkpointer)
```

![Market analysis agent의 LangGraph workflow orchestration](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/07/24/ML-19945-1.png)

## 왜 LangGraph와 Strands를 함께 쓰는가

많은 enterprise use case는 strict하고 predefined된 workflow에 grounding되어야 한다. 올바른 step을 실행하는 문제를 LLM의 non-deterministic nature에만 맡기는 것은 risk다. 하지만 workflow 내부의 특정 step에는 LLM의 agile reasoning과 intelligence가 필요하다.

LangGraph와 Strands의 조합은 이 gap을 연결한다. Deterministic orchestration 안에 localized dynamic intelligence를 배치하는 system을 만들 수 있다.

이 architecture pairing이 complex workflow challenge를 푸는 방식은 다음과 같다.

Node-level intelligence: LangGraph는 workflow의 higher-level orchestration을 정의한다. Strands agent는 specific node에 배치된다. Complex workflow 안에서 LLM analysis나 ambiguity navigation이 필요한 곳에서만 autonomous reasoning과 tool use를 적용한다.

Context isolation with nodal agents: Monolithic agent는 instruction을 쉽게 놓친다. Individual Strands agent를 별도 LangGraph node 안에 배치하면 memory를 compartmentalize할 수 있다. 각 agent는 자기만의 hyper-focused context와 tool history를 관리하고, LangGraph는 여러 agent가 독립적으로 update하고 reference할 수 있는 structured overarching session state를 유지한다.

Supercharging orchestration: LangGraph의 core는 low-level routing/orchestration tool이다. 여기에 Strands를 embed하면 comprehensive enterprise agent framework를 graph에 즉시 연결할 수 있다. LangGraph의 robust routing과 함께 Strands의 native Model Context Protocol(MCP) integration, steering control, safety guardrail, evaluation을 얻는다.

구체적으로 각 specialist는 LangGraph node다. Node는 자기 system prompt, tool, isolated context를 가진 fresh Strands agent를 띄운다. Orchestrator가 할당한 task를 실행하고 state update를 반환한다. LangGraph는 이 partial update를 다른 node가 읽는 shared state에 merge한다. 다음은 `security_monitor` node다.

```python
async def security_monitor_node(state: AgentState) -> AgentState:
    """
    Single-day activity analyst agent that assesses price, volume and tick-level trades
    """
    agent = Agent(
        name="security_monitor",
        model=analyst_model,
        system_prompt=SECURITY_MONITOR_PROMPT,
        tools=[get_report_list, get_report_schema, run_report],
        callback_handler=None,
    )

    # Pull this node's task from the shared state the orchestrator populated.
    task = state.get("agent_task_map", {}).get("security_monitor", state["query_text"])

    # Strands runs its own reasoning + tool loop; collect the agent's final text.
    chunks = []
    async for event in agent.stream_async(task):
        if "data" in event:
            chunks.append(event["data"])
    result = "".join(chunks)

    # Return shared state updates
    return {
        "security_monitor_insights": {"task": task, "business_insights": result},
        "current_agent_index": state.get("current_agent_index", 0) + 1,
    }
```

## AWS infrastructure와 AgentCore deployment

Amazon Bedrock AgentCore는 agent를 scale 있게 deploy하고 operate하기 위한 fully managed service를 제공한다. Infrastructure management 부담을 줄이면서 production-grade capability를 제공한다.

Runtime deployment: Amazon Bedrock AgentCore의 capability인 AgentCore runtime은 local agent code를 최소 configuration으로 cloud-native deployment로 바꾼다. Service는 framework-agnostic이고 LangGraph 및 Strands와 바로 동작한다. Long-running investigation을 위한 extended runtime, interactive workflow를 위한 low-latency execution, demand 기반 automatic scaling 등 dynamic agent workload를 위한 purpose-built infrastructure를 제공한다.

AgentCore Python SDK와 starter toolkit을 사용해 LangGraph orchestrator와 Strands agent를 deploy한다. Runtime은 containerization, networking, compute provisioning을 자동 처리한다. AgentCore는 container orchestration, scaling, session management 같은 undifferentiated heavy lifting을 맡는다.

```python
# api.py --- AgentCore runtime entry point
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from src.agents import Workflow

app = BedrockAgentCoreApp()
workflow = Workflow()

@app.entrypoint
async def market_surveillance_workflow(payload):
    """Invoked by AgentCore for each request. Yields streaming chunks."""
    prompt = payload.get("prompt")
    session_id = payload.get("session_id", "default-session")
    actor_id = payload.get("actor_id", "default-actor")
    async for chunk in workflow.stream_query(
        session_id=session_id, prompt=prompt, actor_id=actor_id
    ):
        yield chunk

if __name__ == "__main__":
    app.run()

# Deploy with the AgentCore starter toolkit
from bedrock_agentcore_starter_toolkit import Runtime

runtime = Runtime()
runtime.configure(
    entrypoint="api.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region="us-east-1",
    agent_name="market_surveillance_workflow",
)
result = runtime.launch()
print(f"Agent ARN: {result.agent_arn}")

# Invoke the deployed agent
import boto3, json

client = boto3.client("bedrock-agentcore", region_name="us-east-1")
response = client.invoke_agent_runtime(
    agentRuntimeArn=result.agent_arn,
    qualifier="DEFAULT",
    payload=json.dumps({
        "prompt": "What caused the AAPL price spike at 11:00 AM on March 15, 2024?",
        "session_id": "session-001",
        "actor_id": "analyst-jane",
    }),
)

# AgentCore returns a server-sent-events stream. Parse it:
for raw in response["response"].iter_lines():
    if not raw:
        continue
    line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    if not line.startswith("data: "):
        continue
    try:
        chunk = json.loads(line[6:])
        if isinstance(chunk, str) and chunk.startswith("data: "):
            chunk = json.loads(chunk[6:])
    except json.JSONDecodeError:
        continue  # malformed chunk --- skip, don't crash
    if isinstance(chunk, dict) and chunk.get("type") == "text":
        print(chunk["content"], end="")
```

Memory integration: LangGraph는 Amazon Bedrock AgentCore의 capability인 AgentCore memory와 `langgraph-checkpoint-aws` package를 통해 몇 줄의 code로 통합된다. 이를 통해 short-term checkpoint persistence와 intelligent long-term memory retrieval을 모두 제공한다.

이 예제에서 사용하는 `AgentCoreMemorySaver` class는 user message, AI response, graph execution state, metadata를 포함한 checkpoint object를 처리한다. 각 node가 완료된 뒤 LangGraph는 checkpoint를 AgentCore memory에 자동 저장한다. Amazon DynamoDB table을 관리하거나 custom serialization logic을 구현하지 않고도 stateful conversation과 workflow recovery를 얻을 수 있다.

`AgentCoreMemoryStore` class는 AgentCore가 conversation에서 insight, summary, user preference를 자동 추출하는 intelligent memory capability를 제공한다. Agent는 future interaction에서 이 memory를 search할 수 있으므로 시간이 지날수록 개선되는 personalized experience를 제공할 수 있다. 이는 agent statelessness라는 근본적 문제를 해결한다. 각 interaction이 처음부터 다시 시작하는 대신, 이전 knowledge 위에 쌓인다.

```python
import boto3, time

REGION = "us-east-1"
control_client = boto3.client("bedrock-agentcore-control", region_name=REGION)

response = control_client.create_memory(
    name="MarketSurveillanceMemory",
    description="Memory for market surveillance multi-agent workflow.",
    eventExpiryDuration=90,  # days
)
MEMORY_ID = response["memory"]["id"]
print(f"Memory ID: {MEMORY_ID}")

# Wait for ACTIVE, with a 10-minute deadline. Creation normally takes 1-3 min.
deadline = time.time() + 600
while True:
    status = control_client.get_memory(memoryId=MEMORY_ID)["memory"]["status"]
    if status == "ACTIVE":
        break
    if status == "FAILED" or time.time() >= deadline:
        raise RuntimeError(f"Memory {MEMORY_ID} is {status!r} (expected ACTIVE)")
    time.sleep(10)
```

Graph build 시점에는 다음처럼 checkpointer를 연결한다.

```python
checkpointer = AgentCoreMemorySaver(MEMORY_ID, region_name=REGION)
graph = workflow.compile(checkpointer=checkpointer)
```

Invocation에서는 agent에 `thread_id`와 `actor_id`를 전달한다. 이 값은 user와 session을 식별하는 unique identifier다.

```python
config = {
    "configurable": {
        "thread_id": "surveillance-session-001",
        "actor_id": "analyst-jane",
    }
}

response = await graph.ainvoke(
    {"query_text": "Which brokers were most active?"},
    config=config,
)
```

Observability and operations: AgentCore는 Amazon CloudWatch와 AWS X-Ray integration을 통해 built-in observability를 제공하며, agent execution trace, tool invocation, performance metric을 capture한다. Service는 agent behavior monitoring, bottleneck identification, cost optimization을 위한 dashboard를 제공한다. LangGraph의 OpenTelemetry event와 결합하면 high-level workflow orchestration부터 individual LLM call과 reasoning step까지 comprehensive visibility를 얻을 수 있다.

## 결론

이 글은 LangGraph의 robust workflow orchestration과 Strands의 intelligent agent reasoning capability를 결합하고 AWS infrastructure에 deploy함으로써 production-ready multi-agent AI system을 구축하는 방법을 보여주었다.

이 hybrid architecture는 separation of concerns를 분명히 한다. LangGraph는 macro-level orchestration, 즉 agent coordination, state persistence, workflow recovery를 담당하고, Strands는 individual node 내부의 detailed reasoning engine을 제공한다. 이 분리를 통해 complex business process를 처리하면서도 checkpoint-based recovery와 comprehensive observability로 production reliability를 유지하는 sophisticated system을 만들 수 있다.

이 architecture는 document processing pipeline, customer service automation, compliance monitoring system 같은 다른 complex orchestration scenario에도 확장할 수 있다. Strands의 model-agnostic nature와 LangGraph의 state management를 결합한 pattern은 flexibility와 reliability를 모두 요구하는 enterprise application에 특히 가치가 있다.

Technical implementation detail을 더 깊게 살펴보고 직접 market analysis agent를 만들려면 [GitHub repository](https://github.com/aws-samples/sample-langgraph-strands-market-analysis)를 참고하면 된다.

## Practitioner notes

- 이 architecture의 핵심은 “모든 것을 agent 하나에게 맡기지 않는 것”이다. LangGraph가 deterministic graph/state/checkpoint를 맡고, Strands가 node-local reasoning/tool loop를 맡는다.
- Market surveillance처럼 auditability와 recovery가 중요한 domain에서는 checkpoint persistence가 단순 편의 기능이 아니라 operational control에 가깝다.
- `get_report_list` → `get_report_schema` → `run_report`처럼 discovery와 execution을 분리하고, schema-validated parameterized SQL을 사용한 점은 agentic data access에서 중요한 safety pattern이다.
- AgentCore는 deployment/runtime/memory/observability를 managed layer로 제공하지만, business-level validation, authorization boundary, data governance는 별도 architecture review가 필요하다.
- Sample repository는 `aws-samples/sample-langgraph-strands-market-analysis`이며, 확인 시점 기준 MIT-0 license다.
