import uuid
from langgraph.graph import END, START, StateGraph
from ..agents.orchestrator import create_orchestrator
from ..schemas.state import EngineeringState

_orchestrator = create_orchestrator()

def orchestrator_node(state: EngineeringState):
    try:
        result = _orchestrator.invoke({"messages": [{"role": "user", "content": f"Analyze this engineering objective and produce an initial plan:\n\n{state.get('objective', '')}"}]})
        messages = result.get("messages", [])
        return {"status": "PLANNING", "final_response": messages[-1].content if messages else "No response."}
    except Exception as exc:
        err_msg = str(exc)
        failure_reason = "Model endpoint error or timeout when calling model provider"
        suggested_resolution = "Verify NVIDIA_API_KEY validity, endpoint availability, or retry request."
        if "500" in err_msg or "Internal Server Error" in err_msg:
            failure_reason = "NVIDIA AI Endpoints returned HTTP 500 Internal Server Error"
        elif "Timeout" in err_msg or "ReadTimeout" in err_msg:
            failure_reason = "HTTP ReadTimeout when waiting for model provider response"
        fallback_msg = f"[System Warning] Orchestrator model invocation failed: {failure_reason}. {suggested_resolution}"
        return {"status": "ERROR_FALLBACK", "final_response": fallback_msg, "error": err_msg}

def build_graph():
    graph = StateGraph(EngineeringState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", END)
    return graph.compile()

def run(objective: str):
    return build_graph().invoke({"task_id": str(uuid.uuid4()), "objective": objective, "status": "NEW"})
