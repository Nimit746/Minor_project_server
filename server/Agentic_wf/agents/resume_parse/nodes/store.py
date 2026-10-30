# C:\Users\gupta.000\Desktop\Minor\server\Agentic_wf\agents\resume_parse\nodes\store.py
import logging
import os
import shutil
from Agentic_wf.agents.resume_parse.states import FileState
from Agentic_wf.config import resume_collection_name
from Agentic_wf.services import VectorStoreService, EmbeddingService

logger = logging.getLogger(__name__)


async def store_in_vector_db(state: FileState) -> FileState:
    """
    Stores document chunks in the vector database with their embeddings.
    Automatically cleans up temporary files after processing (success or failure).

    Args:
        state: Current FileState containing chunked, metadata-enriched documents

    Returns:
        Only the updated state fields (LangGraph merges them automatically)
    """
    temp_dir = state['metadata'].get('temp_directory')  # Get temp dir from download node
    chunks = []
    document_id = state.get('document_id')
    try:
        chunks = state.get('chunks', [])
        logger.info("store_in_vector_db: START resume=%s chunks=%d", document_id, len(chunks))

        if not chunks:
            raise ValueError("No document chunks found to store in vector database")

        # Initialize your existing services
        collection_name = resume_collection_name(state['user_id'])
        embedding_service = EmbeddingService()
        vector_store = VectorStoreService(
            embeddings=embedding_service.embeddings,
            collection_name=collection_name  # Isolated collection per user
        )
        logger.info(
            "store_in_vector_db: embedding_service ready, collection=%s resume=%s",
            collection_name, document_id,
        )

        # Store chunks in vector database (handles embedding generation automatically)
        await vector_store.add_docs(chunks)

        # Clean up temporary files after successful storage
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            temp_cleanup_success = True
        else:
            temp_cleanup_success = False

        # Return ONLY the changed fields
        logger.info(
            "store_in_vector_db: COMPLETED resume=%s collection=%s stored=%d",
            document_id, collection_name, len(chunks),
        )
        return {
            "status": "stored_in_vector_db",
            "metadata": {
                **state['metadata'],
                "chunks_stored": len(chunks),
                "collection_name": collection_name,
                "temp_cleanup_success": temp_cleanup_success
            },
            "error": None
        }

    except Exception as e:
        logger.exception(
            "store_in_vector_db: FAILED resume=%s chunks=%d error=%s",
            document_id, len(chunks), e,
        )
        # Always clean up temp files even if storage fails (prevents disk bloat)
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                logger.warning("store_in_vector_db: temp cleanup failed for %s", temp_dir)

        # Report the failure
        return {
            "status": "storage_failed",
            "error": f"Failed to store in vector database: {str(e)}"
        }