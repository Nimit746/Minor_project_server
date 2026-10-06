"""
Integration tests for the complete question generation workflow.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import pytest
from langgraph.types import Command
from Agentic_wf.agents.generate_questions import build_question_generator_graph


@pytest.mark.asyncio
async def test_full_question_generation_workflow():
    """Test the complete workflow from initialization to finalization."""
    app = build_question_generator_graph()
    initial_state = {
        "candidate_id": "integration_test_001",
        "company_name": "Microsoft",
        "target_role": "ML Engineer",
        "resume_text": """
        Alex - ML Engineer
        Skills: Python, TensorFlow, PyTorch, Scikit-learn, Computer Vision, NLP
        Experience: 3 years working on deep learning models and ML pipelines.
        """
    }
    
    config = {"configurable": {"thread_id": "integration_thread_001"}}
    
    # Start the workflow - convert dict to SessionState
    from Agentic_wf.agents.generate_questions.states.session_state import SessionState
    session_state = SessionState(**initial_state)
    await app.ainvoke(session_state, config=config)
    
    # We should hit the first interrupt
    snapshot = app.get_state(config)
    assert snapshot.tasks and snapshot.tasks[0].interrupts
    
    # Answer a few questions - always send the correct answer
    num_questions_to_answer = 3
    for i in range(num_questions_to_answer):
        # Extract the correct answer from the current question
        current_snapshot = app.get_state(config)
        if current_snapshot.tasks and current_snapshot.tasks[0].interrupts:
            # Get the current question's correct answer from state
            question = current_snapshot.values.get("question", {})
            correct_answer = question.get("correct_answer", f"Test answer {i+1}")
            # Submit the CORRECT answer instead of a generic one
            await app.ainvoke(Command(resume=correct_answer), config=config)
        else:
            # If no interrupt, we're done
            break
        
        # Verify the answer was marked correct
        after_snapshot = app.get_state(config)
        assert after_snapshot.values["is_correct"] is not None
        # For MCQs with exact matches, this should always be True
        if question.get("question_type") == "mcq":
            assert after_snapshot.values["is_correct"] is True, f"Correct answer '{correct_answer}' was marked incorrect!"
    
    # Get final state
    final_snapshot = app.get_state(config)
    if final_snapshot.next == ("__end__",):
        values = final_snapshot.values
        assert values["final_session_score"] is not None
        assert values["consolidated_metrics"] is not None
        assert values["questions_asked"] > 0
        print(f"Integration test passed! Final score: {values['final_session_score']}")


@pytest.mark.asyncio
async def test_workflow_state_persistence():
    """Test that state is properly persisted throughout the workflow."""
    app = build_question_generator_graph()
    initial_state = {
        "candidate_id": "persistence_test_001",
        "company_name": "Google",
        "target_role": "Senior AI Engineer",
        "resume_text": "Test resume with Python and ML skills"
    }
    
    config = {"configurable": {"thread_id": "persistence_thread_001"}}
    
    # First step
    await app.ainvoke(initial_state, config=config)
    snapshot1 = app.get_state(config)
    assert snapshot1.values["candidate_id"] == "persistence_test_001"
    
    # Answer first question
    await app.ainvoke(Command(resume="Sample answer"), config=config)
    snapshot2 = app.get_state(config)
    # State should persist
    assert snapshot2.values["candidate_id"] == "persistence_test_001"
    # The field might be named differently based on your implementation
    assert "candidate_answer" in snapshot2.values