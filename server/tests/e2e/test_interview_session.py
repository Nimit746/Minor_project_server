"""
End-to-end test for a complete interview session.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from langgraph.types import Command
from Agentic_wf.agents.generate_questions import build_question_generator_graph


@pytest.mark.asyncio
async def test_complete_interview_session():
    """Test a complete end-to-end interview session from start to finish."""
    app = build_question_generator_graph()
    
    # Full candidate profile
    candidate_data = {
        "candidate_id": "e2e_candidate_001",
        "company_name": "Netflix",
        "target_role": "Senior Machine Learning Engineer",
        "resume_text": """
        Jane Doe - Senior ML Engineer
        Skills: Python, PyTorch, TensorFlow, Distributed Systems, MLOps, LLMs, RAG
        Experience: 6 years building large-scale ML systems and recommendation engines.
        Previous work at Amazon on personalization systems.
        """
    }
    
    config = {"configurable": {"thread_id": "e2e_session_001"}}
    
    print("Starting end-to-end interview session test...")
    
    # Start the interview
    await app.ainvoke(candidate_data, config=config)
    
    # Simulate a complete interview
    questions_answered = 0
    max_questions = 10
    
    while questions_answered < max_questions:
        snapshot = app.get_state(config)
        
        # Check if session is complete
        if snapshot.next == ("__end__",):
            break
            
        # Check if we need to answer a question
        if snapshot.tasks and snapshot.tasks[0].interrupts:
            questions_answered += 1
            q_val = snapshot.tasks[0].interrupts[0].value
            print(f"Processing question #{questions_answered}: {q_val.get('question_text')[:50]}...")
            
            # Submit a simulated good answer
            await app.ainvoke(
                Command(resume="This is a comprehensive answer demonstrating understanding of the topic."),
                config=config
            )
    
    # Verify session completed successfully
    final_snapshot = app.get_state(config)
    assert final_snapshot.next == ("__end__",), "Session did not complete successfully"
    
    final_values = final_snapshot.values
    print(f"\nInterview session completed!")
    print(f"Total questions asked: {final_values['questions_asked']}")
    print(f"Final score: {final_values['final_session_score']}")
    print(f"Concept gaps identified: {final_values['concept_gaps']}")
    
    # Verify all metrics are present
    assert final_values["final_session_score"] is not None
    assert final_values["consolidated_metrics"] is not None
    assert "accuracy" in final_values["consolidated_metrics"]
    assert len(final_values["question_history"]) == final_values["questions_asked"]
    assert len(final_values["answer_history"]) == final_values["questions_asked"]