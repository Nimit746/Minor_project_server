"""
Test script to run the adaptive interview question generation agent.
Verifies resume parsing, company context injection, difficulty adaptation,
and session finalization.
"""
import asyncio
from langgraph.types import Command
from Agentic_wf.agents.generate_questions import build_question_generator_graph


async def test_agent():
    # Build the graph
    app = build_question_generator_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    print("[SUCCESS] Graph built successfully!")
    
    # Initialize state with candidate background, resume, and target company
    initial_state = {
        "candidate_id": "test_candidate_001",
        "company_name": "Google",
        "target_role": "AI Engineer",
        "resume_text": """
        John Doe - AI Engineer
        Skills: Python, FastAPI, Distributed Systems, PostgreSQL, Docker, Redis, Kubernetes, Langgraph, Langchain, Tensorflow, PyTorch, Scikit-learn, matplotlib, pandas, numpy
        Experience: 2 years building high-throughput microservices and REST APIs in Python.
        Projects: Real-time chat system with WebSockets and Redis Pub/Sub, URL shortener with rate limiting.
        """
    }
    
    config = {"configurable": {"thread_id": "test_session_001"}}
    
    print("\n--- Starting interview practice session ---")
    
    # First stream will run until interrupt_for_answer node
    async for event in app.astream(initial_state, config=config):
        for node_name, state_update in event.items():
            if node_name != "__end__":
                print(f"\n[Node Completed] {node_name}")
                if isinstance(state_update, dict):
                    if "current_topic" in state_update:
                        print(f"   Topic: {state_update.get('current_topic')}")
                    if "current_difficulty" in state_update:
                        print(f"   Difficulty: {state_update.get('current_difficulty')}")
                    if "extracted_skills" in state_update and state_update["extracted_skills"]:
                        print(f"   Extracted Skills: {state_update['extracted_skills']}")
                    if "company_focus" in state_update and state_update["company_focus"]:
                        print(f"   Company Focus: {state_update['company_focus']}")
                    if "question" in state_update and state_update["question"]:
                        q = state_update["question"]
                        q_text = getattr(q, 'question_text', '') or (q.get('question_text', '') if isinstance(q, dict) else '')
                        print(f"   Generated Question: {q_text[:120]}...")
                        options = getattr(q, 'options', []) or (q.get('options', []) if isinstance(q, dict) else [])
                        print(f"   Options: {options}")

    # Inspect interrupted state and answer the question
    snapshot = app.get_state(config)
    print(f"\n[State] Graph paused at: {snapshot.next}")
    
    if snapshot.tasks and snapshot.tasks[0].interrupts:
        interrupt_val = snapshot.tasks[0].interrupts[0].value
        print(f"   Question waiting for answer: {interrupt_val.get('question_text')}")
        
        # Simulate candidate answering Option A
        print("\n--- Submitting candidate answer: Option A ---")
        async for event in app.astream(Command(resume="Option A"), config=config):
            for node_name, state_update in event.items():
                if node_name != "__end__":
                    print(f"\n[Resumed Node] {node_name}")
                    if isinstance(state_update, dict):
                        if "is_correct" in state_update:
                            print(f"   Is Correct: {state_update.get('is_correct')}")
                        if "score_running" in state_update:
                            print(f"   Running Score: {state_update.get('score_running')}/{state_update.get('questions_asked')}")
                        if "final_session_score" in state_update:
                            print(f"   Final Session Score: {state_update.get('final_session_score')}")

    print("\n[COMPLETE] Practice Test Session Completed!")



if __name__ == "__main__":
    asyncio.run(test_agent())
