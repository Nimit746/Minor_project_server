import asyncio
import logging

from Agentic_wf.config import VectorStore, get_embeddings, resume_collection_name

logger = logging.getLogger(__name__)


async def retrieve_relevant_chunks(
    topic: str, user_id: str | None = None, k: int = 3
) -> list[str]:
    if not user_id:
        logger.warning("retrieve_relevant_chunks: no user_id, skipping RAG")
        return []

    collection = resume_collection_name(user_id)
    try:
        client = VectorStore.get_vector_client()
        if not await asyncio.to_thread(client.collection_exists, collection):
            logger.warning("collection %s does not exist yet", collection)
            return []
        store = VectorStore(get_embeddings(), collection)
        docs = await store.asimilarity_search(topic, k=k)
        return [d.page_content for d in docs]
    except Exception:
        logger.exception("retrieval failed for collection=%s", collection)
        return []