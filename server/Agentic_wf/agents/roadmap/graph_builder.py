from langgraph.graph import StateGraph, START, END
from Agentic_wf.agents.roadmap.states import Roadmap
from Agentic_wf.agents.roadmap.nodes import (
    get_candidate_data,
    analyze_topics,
    create_sections,
    create_sections_data,
    compile_roadmap,
)


def build_roadmap_graph():
    """
    Builds and compiles the Roadmap Generation agent workflow.
    Workflow sequence:
    START -> get_candidate_data -> analyze_topics -> create_sections -> generate_sections_data -> compile_roadmap -> END
    """
    graph = StateGraph(Roadmap)

    # Add Nodes
    graph.add_node("get_candidate_data", get_candidate_data)
    graph.add_node("analyze_topics", analyze_topics)
    graph.add_node("create_sections", create_sections)
    graph.add_node("generate_sections_data", create_sections_data)
    graph.add_node("compile_roadmap", compile_roadmap)

    # Add Sequential Edges
    graph.add_edge(START, "get_candidate_data")
    graph.add_edge("get_candidate_data", "analyze_topics")
    graph.add_edge("analyze_topics", "create_sections")
    graph.add_edge("create_sections", "generate_sections_data")
    graph.add_edge("generate_sections_data", "compile_roadmap")
    graph.add_edge("compile_roadmap", END)

    workflow = graph.compile()
    return workflow