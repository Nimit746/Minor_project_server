"""
Dedicated unit and workflow tests for the Question Generator Agent.
Supports pytest execution and direct Python script execution.
"""
import pytest
import asyncio
from langgraph.graph import END
from langgraph.types import Command
from Agentic_wf.agents.generate_questions import build_question_generator_graph


@pytest.mark.asyncio
async def test_question_generator_compilation():
    """Verify that the Question Generator agent workflow compiles."""
    app = build_question_generator_graph()
    # app.get_graph().draw_mermaid_png(output_file_path="graphs/question_generator_graph.png")
    assert app is not None


@pytest.mark.asyncio
async def test_question_generator_initialization():
    """Verify that the question generator initializes properly with valid inputs."""
    app = build_question_generator_graph()
    initial_state = {
        "candidate_id": "test_candidate_001",
        "company_name": "Amazon",
        "target_role": "AI Engineer",
        "resume_text": """
        Nimit - AI Engineer
        Skills: Python, FastAPI, Distributed Systems, PostgreSQL, Docker, Redis, Kubernetes, LangGraph, PyTorch
        Experience: 2 years building high-throughput microservices and REST APIs in Python.
        """
    }
    
    # Invoke the graph until the first interrupt
    config = {"configurable": {"thread_id": "test_session_001"}}
    await app.ainvoke(initial_state, config=config)
    
    snapshot = app.get_state(config)
    assert snapshot is not None
    assert "interrupt_for_answer" in snapshot.next or snapshot.tasks[0].interrupts is not None
    
    # Verify initial state fields are properly populated
    values = snapshot.values
    assert values["candidate_id"] == "test_candidate_001"
    assert values["company_name"] == "Amazon"
    assert values["target_role"] == "AI Engineer"
    assert len(values["extracted_skills"]) > 0
    assert len(values["company_focus"]) > 0


@pytest.mark.asyncio
async def test_question_generator_single_question_flow():
    """Verify that a single question-answer cycle works correctly."""
    app = build_question_generator_graph()
    initial_state = {
        "candidate_id": "test_candidate_002",
        "company_name": "Microsoft",
        "target_role": "ML Engineer",
        "resume_text": """
        Alex - ML Engineer
        Skills: Python, TensorFlow, PyTorch, Scikit-learn, Computer Vision, NLP
        Experience: 3 years working on deep learning models and ML pipelines.
        """
    }
    
    config = {"configurable": {"thread_id": "test_single_question_001"}}
    await app.ainvoke(initial_state, config=config)
    
    # Get the question that was generated
    snapshot = app.get_state(config)
    assert snapshot.tasks[0].interrupts is not None
    q_val = snapshot.tasks[0].interrupts[0].value
    assert q_val.get("question_text") is not None
    assert q_val.get("question_type") is not None
    
    # Submit an answer
    await app.ainvoke(Command(resume="Sample answer about machine learning concepts"), config=config)
    
    # Get the updated state after evaluation
    snapshot = app.get_state(config)
    values = snapshot.values
    assert values["questions_asked"] == 1
    assert values["candidate_answer"] is not None
    assert values["is_correct"] is not None
    assert len(values["question_history"]) == 1
    assert len(values["answer_history"]) == 1
    assert len(values["answer_correctness_history"]) == 1


@pytest.mark.asyncio
async def test_question_generator_session_finalization():
    """Verify that the session properly finalizes after completion."""
    app = build_question_generator_graph()
    initial_state = {
        "candidate_id": "test_candidate_003",
        "company_name": "Google",
        "target_role": "Senior AI Engineer",
        "resume_text": """
        Sam - Senior AI Engineer
        Skills: Python, Distributed Systems, ML, LangGraph, LLMs, RAG Systems
        Experience: 5 years building large-scale AI systems.
        """
    }
    
    config = {"configurable": {"thread_id": "test_finalization_001"}}
    
    # Run through a few question cycles
    await app.ainvoke(initial_state, config=config)
    
    # Simulate answering 3 questions
    for i in range(3):
        snapshot = app.get_state(config)
        if snapshot.next == (END,):
            break
        if snapshot.tasks and snapshot.tasks[0].interrupts:
            await app.ainvoke(Command(resume=f"Test answer {i+1}"), config=config)
    
    # Get final state
    snapshot = app.get_state(config)
    if snapshot.next == (END,):
        values = snapshot.values
        assert values["final_session_score"] is not None
        assert values["consolidated_metrics"] is not None
        assert len(values["question_history"]) > 0
        print(f"[Test Passed] Session finalized with score: {values['final_session_score']}")


async def run_question_generator_manually():
    print("=== Testing Question Generator Agent ===")
    app = build_question_generator_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graphs/question_generator_graph.png")
    print("[SUCCESS] Question generator graph built and question_generator_graph.png generated.")

    initial_state = {
        "candidate_id": "test_candidate_002",
        "company_name": "Amazon",
        "target_role": "AI Engineer",
        "resume_text": """
        Nimit - AI Engineer
        Skills: Python, FastAPI, Distributed Systems, PostgreSQL, Docker, Redis, Kubernetes, LangGraph, PyTorch
        Experience: 2 years building high-throughput microservices and REST APIs in Python.
        """
    }
    config = {"configurable": {"thread_id": "test_session_isolated_001"}}

    print("\nExecuting Question Generator session until interrupt...")
    async for event in app.astream(initial_state, config=config):
        for node_name, state_update in event.items():
            if node_name != "__end__":
                print(f"[Node Completed] {node_name}")

    snapshot = app.get_state(config)
    print(f"\n[State] Paused at: {snapshot.next}")

    question_number = 1
    while snapshot.tasks and snapshot.tasks[0].interrupts:
        current_state = snapshot.values
        q_val = snapshot.tasks[0].interrupts[0].value
        print("\n" + "="*60)
        print(f"\n📝 Question #{question_number} ({q_val.get('question_type').upper()}):")
        print(f"\n{q_val.get('question_text')}\n")
        
        # Display options if it's an MCQ
        if q_val.get('options') and q_val.get('question_type') == "mcq":
            print("Options:")
            for i, option in enumerate(q_val.get('options'), 0):
                # Convert to A, B, C, D format
                option_letter = chr(ord('A') + i)
                print(f"  {option_letter}. {option}")
        
        # Prompt user for their answer
        print("\n" + "-"*60)
        user_answer = input("Enter your answer: ").strip()
        
        print(f"\nSubmitting your answer: {user_answer}...")
        async for event in app.astream(Command(resume=user_answer), config=config):
            for node_name, state_update in event.items():
                if node_name != "__end__":
                    print(f"[Resumed Node] {node_name}")
                    
        question_number += 1
        # Small delay before checking for next question
        await asyncio.sleep(0.5)
        snapshot = app.get_state(config)

    # Print final metrics
    final_state = snapshot.values
    print("\n" + "="*60)
    print("\n=== Session Complete! Final Metrics ===")
    print(f"Total Questions Asked: {final_state.get('questions_asked', 0)}")
    print(f"Final Score: {final_state.get('final_session_score', 'N/A')}")
    print(f"Concept Gaps Identified: {', '.join(final_state.get('concept_gaps', []))}")
    print("=== Question Generator Agent Test Finished Successfully ===\n")


if __name__ == "__main__":
    asyncio.run(run_question_generator_manually())
    
    
    
    
# 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