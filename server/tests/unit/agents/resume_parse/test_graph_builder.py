"""
Unit tests for resume parse graph builder.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.resume_parse import build_resume_parse_graph


def test_graph_compilation():
    """Test that the resume parse graph compiles successfully."""
    app = build_resume_parse_graph()
    assert app is not None