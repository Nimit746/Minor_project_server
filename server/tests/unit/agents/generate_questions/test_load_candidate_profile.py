"""
Unit tests for the load_candidate_profile node.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions.nodes import load_candidate_profile


@pytest.mark.asyncio
async def test_load_candidate_profile_basic():
    """Test that load_candidate_profile properly processes basic input data."""
    state = {
        "candidate_id": "test_001",
        "company_name": "Amazon",
        "target_role": "AI Engineer",
        "resume_text": "Skills: Python, Machine Learning, Deep Learning",
        "extracted_skills": [],
        "company_focus": []
    }
    
    result = await load_candidate_profile(state)
    assert result is not None
    assert len(result["extracted_skills"]) > 0
    assert len(result["company_focus"]) > 0
    assert "Python" in result["extracted_skills"]


@pytest.mark.asyncio
async def test_load_candidate_profile_missing_fields():
    """Test that load_candidate_profile handles minimal input gracefully."""
    state = {
        "candidate_id": "test_002",
        "resume_text": "Software engineer with 5 years experience",
        "extracted_skills": [],
        "company_focus": []
    }
    
    result = await load_candidate_profile(state)
    assert result is not None
    # Should still process even with missing optional fields
    assert isinstance(result["extracted_skills"], list)
    assert isinstance(result["company_focus"], list)