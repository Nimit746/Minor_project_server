from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils import should_continue
from Agentic_wf.agents.generate_questions.nodes import load_candidate_profile, generate_question, interrupt_for_answer, evaluate_answer, controller, finalize_session


def build_question_generator_graph():
    """Build the question generation workflow graph (Stage 8 complete implementation)."""
    # Initialize memory saver for checkpointing
    memory = MemorySaver()
    
    # Initialize state graph with our SessionState schema
    workflow = StateGraph(SessionState)
    
    # Add all nodes (added finalize_session for Stage 8)
    workflow.add_node("load_candidate_profile", load_candidate_profile)
    workflow.add_node("controller", controller)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("interrupt_for_answer", interrupt_for_answer)
    workflow.add_node("evaluate_answer", evaluate_answer)
    workflow.add_node("finalize_session", finalize_session)
    
    # Add core flow edges:
    # START -> load_candidate_profile -> controller
    # generate_question -> interrupt_for_answer -> evaluate_answer -> controller
    workflow.add_edge(START, "load_candidate_profile")
    workflow.add_edge("load_candidate_profile", "controller")
    workflow.add_edge("generate_question", "interrupt_for_answer")
    workflow.add_edge("interrupt_for_answer", "evaluate_answer")
    workflow.add_edge("evaluate_answer", "controller")
    
    # Add conditional edges from controller to determine if we continue or end
    workflow.add_conditional_edges(
        "controller",
        should_continue,
        {
            "continue": "generate_question",  # Loop back to ask another question
            "end": "finalize_session"  # Route to finalization before ending
        }
    )
    
    # Add edge from finalization to END
    workflow.add_edge("finalize_session", END)
    
    # Compile the graph with checkpointer
    app = workflow.compile(checkpointer=memory)
    return app