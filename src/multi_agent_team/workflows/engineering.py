import uuid
from langgraph.graph import END, START, StateGraph
from ..agents.orchestrator import create_orchestrator
from ..schemas.state import EngineeringState

_orchestrator = create_orchestrator()

def orchestrator_node(state: EngineeringState):
    result = _orchestrator.invoke({"messages": [{"role": "user", "content": f"Analyze this engineering objective and produce an initial plan:\n\n{state.get('objective', '')}"}]})
    messages = result.get("messages", [])
    return {"status": "PLANNING", "final_response": messages[-1].content if messages else "No response."}

def build_graph():
    graph = StateGraph(EngineeringState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", END)
    return graph.compile()

def run(objective: str):
    return build_graph().invoke({"task_id": str(uuid.uuid4()), "objective": objective, "status": "NEW"})
