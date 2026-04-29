from langgraph.graph import END, START, StateGraph

from app.graph.nodes import build_prompt, mask_pii, normalize_input, run_llm, validate_output
from app.graph.state import CallGraphState


def build_workflow():
    graph = StateGraph(CallGraphState)
    graph.add_node("normalize_input", normalize_input)
    graph.add_node("mask_pii", mask_pii)
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("run_llm", run_llm)
    graph.add_node("validate_output", validate_output)

    graph.add_edge(START, "normalize_input")
    graph.add_edge("normalize_input", "mask_pii")
    graph.add_edge("mask_pii", "build_prompt")
    graph.add_edge("build_prompt", "run_llm")
    graph.add_edge("run_llm", "validate_output")
    graph.add_edge("validate_output", END)
    return graph.compile()
