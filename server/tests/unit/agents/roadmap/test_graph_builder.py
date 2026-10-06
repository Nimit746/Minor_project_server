"""
Unit tests for roadmap graph builder.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.roadmap import build_roadmap_graph


def test_graph_compilation():
    """Test that the roadmap graph compiles successfully."""
    app = build_roadmap_graph()
    assert app is not None