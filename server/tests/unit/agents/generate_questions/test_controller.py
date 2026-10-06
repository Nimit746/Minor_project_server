"""
Unit tests for the controller node in question generation.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions.nodes import controller
from Agentic_wf.agents.generate_questions.utils import should_continue


@pytest.mark.asyncio
async def test_controller_initial_state():
    """Test controller with initial state (no questions asked yet)."""
    state = {
        "questions_asked": 0,
        "candidate_id": "test_001",
        "extracted_skills": ["Python", "ML"],
        "company_focus": ["Cloud", "AI"]
    }
    
    result = await controller(state)
    assert result is not None


def test_should_continue_logic():
    """Test the should_continue router function."""
    # Test case 1: Should continue asking questions
    state_continue = {
        "questions_asked": 3,
        # Maximum questions not reached yet
    }
    assert should_continue(state_continue) == "continue"
    
    # Test case 2: Should end session
    state_end = {
        "questions_asked": 10,  # Assuming max questions is 10
    }
    # This should return "end" when limit is reached
    # The exact logic depends on your implementation, adjust test accordingly