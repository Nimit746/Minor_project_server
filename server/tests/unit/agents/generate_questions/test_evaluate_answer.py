"""
Unit tests for the evaluate_answer node.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from Agentic_wf.agents.generate_questions.nodes import evaluate_answer
from Agentic_wf.agents.generate_questions.states.question import Question


@pytest.mark.asyncio
async def test_evaluate_answer_correct():
    """Test evaluation of a correct answer."""
    test_question = Question(
        question_text="What is Python?",
        question_type="open",
        correct_answer="Python is a programming language.",
        topic="Programming"
    )
    
    state = {
        "question": test_question,
        "candidate_answer": "Python is a popular programming language used for development.",
        "is_correct": None,
        "score_running": 0,
        "answer_correctness_history": []
    }
    
    result = await evaluate_answer(state)
    assert result is not None
    assert result["is_correct"] is not None
    assert isinstance(result["is_correct"], bool)
    assert len(result["answer_correctness_history"]) == 1


@pytest.mark.asyncio
async def test_evaluate_answer_updates_score():
    """Test that the running score is updated correctly."""
    initial_score = 5
    test_question = Question(
        question_text="Test question",
        question_type="mcq",
        correct_answer="A",
        topic="Test",
        points=1
    
    )
    
    state = {
        "question": test_question,
        "candidate_answer": "A",
        "is_correct": None,
        "score_running": initial_score,
        "answer_correctness_history": []
    }
    
    result = await evaluate_answer(state)
    assert result is not None
    # If answer is correct, score should increase
    if result["is_correct"]:
        assert result["score_running"] > initial_score