"""
Dedicated unit and workflow tests for the Roadmap Generation Agent.
Supports pytest execution and direct Python script execution.
"""
import pytest
import asyncio
from Agentic_wf.agents.roadmap import build_roadmap_graph


@pytest.mark.asyncio
async def test_roadmap_graph_compilation():
    """Verify that the roadmap workflow graph compiles and exports mermaid diagram."""
    app = build_roadmap_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graphs/roadmap_graph.png")
    assert app is not None


@pytest.mark.asyncio
async def test_roadmap_universal_mode():
    """Verify universal roadmap generation when candidate data/weak points are absent."""
    app = build_roadmap_graph()
    initial_state = {
        "candidate_id": "test_candidate_002",
        "target_role": "AI Engineer",
        "available_hours_per_day": 2.0,
        "is_universal": True,
    }
    
    result = await app.ainvoke(initial_state)
    assert result is not None
    assert "roadmap" in result and result["roadmap"] is not None
    
    roadmap = result["roadmap"]
    assert roadmap.get("target_role") == "DevOps Engineer"
    assert len(roadmap.get("sections", [])) > 0


@pytest.mark.asyncio
async def test_roadmap_personalized_mode():
    """Verify personalized roadmap focusing on weak topics."""
    app = build_roadmap_graph()
    initial_state = {
        "candidate_id": "test_candidate_002",
        "target_role": "AI Engineer",
        "available_hours_per_day": 2.5,
        "weak_topics": ["Distributed Locking in Redis", "PostgreSQL Query Optimization"],
        "strengths": ["FastAPI", "Python"],
        "is_universal": False,
    }
    
    result = await app.ainvoke(initial_state)
    assert result is not None
    assert "roadmap" in result and result["roadmap"] is not None
    
    roadmap = result["roadmap"]
    sections = roadmap.get("sections", [])
    assert len(sections) > 0
    # Check that interactive checkpoints exist
    assert any(len(sec.get("checkpoints", [])) > 0 for sec in sections)


async def run_roadmap_agent_manually():
    print("=== Testing Roadmap Generation Agent ===")
    app = build_roadmap_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graphs/roadmap_graph.png")
    print("[SUCCESS] Roadmap graph built and roadmap_graph.png generated.")

    initial_state = {
        "candidate_id": "test_candidate_002",
        "target_role": "Full Stack AI Engineer",
        "available_hours_per_day": 2.5,
        "weak_topics": ["LangGraph State Management", "Vector Database Indexing (HNSW/IVF)"],
        "strengths": ["Python", "FastAPI"],
        "is_universal": False,
    }

    print("\nExecuting Roadmap Workflow...")
    last_state = {}
    async for event in app.astream(initial_state):
        for node_name, state_update in event.items():
            if node_name != "__end__":
                print(f"[Node Completed] {node_name}")
                if isinstance(state_update, dict):
                    last_state.update(state_update)

    roadmap = last_state.get("roadmap", {})
    print("\n--- Roadmap Output ---")
    print(f"Role: {roadmap.get('target_role')}")
    print(f"Total Weeks: {roadmap.get('timeline', {}).get('total_estimated_weeks')}")
    print(f"Sections Count: {len(roadmap.get('sections', []))}")
    print("=== Roadmap Agent Test Finished Successfully ===\n")


if __name__ == "__main__":
    asyncio.run(test_roadmap_personalized_mode())
