"""
Unit tests for the generate_question node.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions.nodes import generate_question


@pytest.mark.asyncio
async def test_generate_question_creates_valid_question():
    """Test that generate_question creates a properly formatted question."""
    state = {
        "candidate_id": "test_001",
        "target_role": "AI Engineer",
        "current_topic": "Python",
        "current_difficulty": 2,
        "extracted_skills": ["Python", "Machine Learning"],
        "question": None
    }
    
    result = await generate_question(state)
    assert result is not None
    assert result["question"] is not None
    assert hasattr(result["question"], "question_text")
    assert hasattr(result["question"], "question_type")
    assert result["question"].question_text is not None
    assert len(result["question"].question_text) > 0


@pytest.mark.asyncio
async def test_generate_question_different_difficulties():
    """Test question generation with different difficulty levels."""
    for difficulty in [1, 3, 5]:
        state = {
            "candidate_id": f"test_diff_{difficulty}",
            "target_role": "ML Engineer",
            "current_topic": "Machine Learning",
            "current_difficulty": difficulty,
            "extracted_skills": ["Python", "TensorFlow"],
            "question": None
        }
        
        result = await generate_question(state)
        assert result is not None
        assert result["question"] is not None