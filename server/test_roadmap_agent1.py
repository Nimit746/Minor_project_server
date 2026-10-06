"""
Test script to run the Roadmap Generation Agent.
Verifies graph compilation, draws mermaid graph image,
and executes personalized and universal roadmap tests.
"""
import asyncio
from Agentic_wf.agents.roadmap import build_roadmap_graph


async def test_roadmap_agent():
    # Build the graph
    app = build_roadmap_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graphs/roadmap_graph.png")
    print("[SUCCESS] Graph built and roadmap_graph.png saved successfully!")

    # Test state with candidate background and identified weak points
    initial_state = {
        "candidate_id": "test_candidate_001",
        "target_role": "Full Stack AI Engineer",
        "available_hours_per_day": 2.5,
        "weak_topics": ["LangGraph State Management", "Vector Database Indexing (HNSW/IVF)"],
        "strengths": ["Python", "FastAPI"],
        "is_universal": False,
    }

    print("\n--- Starting Roadmap Generation Workflow ---")
    
    last_state = {}
    # Stream node execution
    async for event in app.astream(initial_state):
        for node_name, state_update in event.items():
            if node_name != "__end__":
                print(f"\n[Node Completed] {node_name}")
                if isinstance(state_update, dict):
                    last_state.update(state_update)
                    if "is_universal" in state_update:
                        print(f"   Is Universal Mode: {state_update.get('is_universal')}")
                    if "learning_profile" in state_update and state_update["learning_profile"]:
                        print(f"   Learning Profile Strategy: {state_update['learning_profile'].get('strategy')}")
                    if "prioritized_topics" in state_update and state_update["prioritized_topics"]:
                        print(f"   Prioritized Topics Count: {len(state_update['prioritized_topics'])}")
                    if "sections" in state_update and state_update["sections"]:
                        print(f"   Sections Generated: {len(state_update['sections'])}")
                    if "roadmap" in state_update and state_update["roadmap"]:
                        roadmap = state_update["roadmap"]
                        print(f"   Roadmap Target Role: {roadmap.get('target_role')}")
                        print(f"   Total Estimated Weeks: {roadmap.get('timeline', {}).get('total_estimated_weeks')}")

    # Inspect final roadmap from streamed execution
    roadmap = last_state.get("roadmap", {})
    
    print("\n[Generated Roadmap Overview]")
    print(f"Target Role: {roadmap.get('target_role')}")
    print(f"Is Universal: {roadmap.get('is_universal')}")
    print(f"Total Weeks: {roadmap.get('timeline', {}).get('total_estimated_weeks')}")
    print(f"Weak Points Targeted: {roadmap.get('weak_points_targeted')}")
    
    print("\n[Roadmap Sections, Checkpoints & Resources]")
    for sec in roadmap.get("sections", []):
        print(f"\n* {sec.get('title')} ({sec.get('estimated_hours')} hrs) [Tag: {sec.get('focus_tag')}]")
        print(f"  Focus Type: {sec.get('focus_type')}")
        print(f"  Topics: {sec.get('topics')}")
        checkpoints = sec.get("checkpoints", [])
        if checkpoints:
            print(f"  Interactive Checkpoints ({len(checkpoints)}):")
            for chk in checkpoints:
                print(f"    [ ] {chk.get('task')} (~{chk.get('estimated_minutes')} mins)")
        resources = sec.get("resources", [])
        print(f"  Curated Resources ({len(resources)} found):")
        for res in resources[:2]:
            print(f"    - [{res.get('type')}] {res.get('title')} -> {res.get('url')}")

    print("\n[COMPLETE] Roadmap Generation Session Completed!")


if __name__ == "__main__":
    asyncio.run(test_roadmap_agent())
