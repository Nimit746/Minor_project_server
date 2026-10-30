import asyncio
import os
import shutil

from Agentic_wf.agents.resume_parse.states import FileState
from Agentic_wf.config import VectorStore, resume_collection_name


def check_already_ingested(state: FileState) -> str:
    """Sync router: reads the flag set by run_ingestion_check."""
    # Rename "skip_processing" to match the edge name in your graph.
    return "skip_processing" if state.get("already_ingested") else "download_file"


async def run_ingestion_check(state: FileState) -> FileState:
    try:
        collection = resume_collection_name(state["user_id"])
        exists = await asyncio.to_thread(
            VectorStore.document_exists, collection, state["document_id"]
        )
        return {"already_ingested": exists}
    except Exception:
        # On failure, re-ingest rather than skip
        return {"already_ingested": False}


def skip_processing(state: FileState) -> FileState:
    temp_dir = state["metadata"].get("temp_directory")
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    return {"status": "already_ingested_skipped", "error": None}