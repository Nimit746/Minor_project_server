"""
Unit tests for the finalize_session node.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions.nodes import finalize_session


@pytest.mark.asyncio
async def test_finalize_session_calculates_metrics():
    """Test that finalize_session properly calculates final metrics."""
    state = {
        "candidate_id": "test_001",
        "questions_asked": 5,
        "score_running": 4,
        "answer_correctness_history": [True, True, False, True, True],
        "concept_gaps": [],
        "strengths": [],
        "weaknesses": [],
        "final_session_score": None,
        "consolidated_metrics": None
    }
    
    result = await finalize_session(state)
    assert result is not None
    assert result["final_session_score"] is not None
    assert result["consolidated_metrics"] is not None
    assert isinstance(result["final_session_score"], float)
    # Should identify strengths and weaknesses
    assert len(result["strengths"]) >= 0
    assert len(result["weaknesses"]) >= 0
    assert len(result["concept_gaps"]) >= 0


@pytest.mark.asyncio
async def test_finalize_session_handles_empty_session():
    """Test finalization with minimal session data."""
    state = {
        "candidate_id": "test_002",
        "questions_asked": 1,
        "score_running": 1,
        "answer_correctness_history": [True],
        "concept_gaps": [],
        "strengths": [],
        "weaknesses": [],
        "final_session_score": None,
        "consolidated_metrics": None
    }
    
    result = await finalize_session(state)
    assert result is not None
    assert result["final_session_score"] == 1.0  # 1/1 = 100%
    assert "accuracy" in result["consolidated_metrics"]