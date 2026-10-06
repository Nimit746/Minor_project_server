"""
Dedicated unit and workflow tests for the Resume Ingestion/Parse Agent.
Supports pytest execution and direct Python script execution.
"""
import pytest
import asyncio
from Agentic_wf.agents.resume_parse import build_ingestion_graph


@pytest.mark.asyncio
async def test_resume_parse_graph_compilation():
    """Verify that the Resume Ingestion workflow compiles."""
    app = build_ingestion_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graphs/resume_parse_graph.png")
    assert app is not None


async def run_resume_parse_manually():
    print("=== Testing Resume Parse Agent ===")
    app = build_ingestion_graph()
    app.get_graph().draw_mermaid_png(output_file_path="graphs/resume_parse_graph.png")
    print("[SUCCESS] Resume parse graph built and resume_parse_graph.png generated.")
    print("=== Resume Parse Agent Test Finished Successfully ===\n")


if __name__ == "__main__":
    asyncio.run(run_resume_parse_manually())
