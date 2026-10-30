import logging
import os
import shutil

from Agentic_wf.agents.resume_parse.states import FileState
from Agentic_wf.config import VectorStore, get_embeddings, resume_collection_name

logger = logging.getLogger(__name__)


async def store_in_vector_db(state: FileState) -> FileState:
    temp_dir = state["metadata"].get("temp_directory")
    chunks = state.get("chunks", [])
    document_id = state.get("document_id")

    try:
        if not chunks:
            raise ValueError("No document chunks found to store in vector database")

        collection_name = resume_collection_name(state["user_id"])
        vector_store = VectorStore(get_embeddings(), collection_name)  # creates collection if missing
        await vector_store.aadd_documents(chunks)

        cleaned = False
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            cleaned = True

        logger.info("stored resume=%s collection=%s chunks=%d",
                    document_id, collection_name, len(chunks))
        return {
            "status": "stored_in_vector_db",
            "metadata": {
                **state["metadata"],
                "chunks_stored": len(chunks),
                "collection_name": collection_name,
                "temp_cleanup_success": cleaned,
            },
            "error": None,
        }

    except Exception as e:
        logger.exception("store_in_vector_db FAILED resume=%s", document_id)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return {"status": "storage_failed", "error": f"Failed to store in vector database: {e}"}