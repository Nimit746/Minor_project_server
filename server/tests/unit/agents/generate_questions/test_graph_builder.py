"""
Unit tests for the question generation graph builder.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions import build_question_generator_graph


def test_graph_compilation():
    """Test that the question generator graph compiles successfully."""
    app = build_question_generator_graph()
    assert app is not None
    # Verify we can get graph visualization
    graph_data = app.get_graph().draw_mermaid()
    assert graph_data is not None
    assert "load_candidate_profile" in graph_data
    assert "controller" in graph_data
    assert "generate_question" in graph_data
    assert "interrupt_for_answer" in graph_data
    assert "evaluate_answer" in graph_data
    assert "finalize_session" in graph_data


def test_graph_structure():
    """Test that the graph has the correct nodes and edges."""
    app = build_question_generator_graph()
    graph = app.get_graph()
    
    # Check that all expected nodes exist
    nodes = list(graph.nodes.keys())
    expected_nodes = [
        "__start__", "load_candidate_profile", "controller", 
        "generate_question", "interrupt_for_answer", "evaluate_answer",
        "finalize_session", "__end__"
    ]
    
    for node in expected_nodes:
        assert node in nodes, f"Node {node} missing from graph"