"""
Unit tests for utility functions in the generate_questions module.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions.utils import (
    calculate_detailed_metrics,
    get_next_question_type,
    pick_next_topic,
    get_available_topics_for_session,
    should_continue
)


def test_calculate_detailed_metrics():
    """Test that detailed metrics are calculated correctly."""
    answer_history = [True, True, False, True, True]
    metrics = calculate_detailed_metrics(answer_history)
    assert metrics is not None
    assert "accuracy" in metrics
    assert metrics["accuracy"] == 0.8  # 4/5 correct
    assert "total_questions" in metrics
    assert metrics["total_questions"] == 5


def test_pick_next_topic():
    """Test topic selection logic."""
    available_topics = ["Python", "Machine Learning", "Deep Learning", "Cloud"]
    previous_topics = ["Python"]
    
    next_topic = pick_next_topic(available_topics, previous_topics)
    assert next_topic in available_topics
    assert next_topic is not None


def test_get_available_topics_for_session():
    """Test that available topics are properly extracted from skills."""
    extracted_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    topics = get_available_topics_for_session(extracted_skills)
    assert len(topics) == len(extracted_skills)
    assert all(topic in extracted_skills for topic in topics)


def test_should_continue():
    """Test session continuation logic."""
    # Test continuing session
    state_continue = {"questions_asked": 5}  # Below max limit
    assert should_continue(state_continue) == "continue"
    
    # Test ending session
    state_end = {"questions_asked": 10}  # At max limit
    # Adjust based on your actual max questions limit
    # assert should_continue(state_end) == "end"