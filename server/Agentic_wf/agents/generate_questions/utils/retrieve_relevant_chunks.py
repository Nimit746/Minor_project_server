import logging

from Agentic_wf.config import get_embeddings, resume_collection_name
from Agentic_wf.services.RAG.retriever_service import RetrieverService

logger = logging.getLogger(__name__)


async def retrieve_relevant_chunks(
    topic: str, user_id: str | None = None, k: int = 3
) -> list[str]:
    """Retrieve relevant chunks from the candidate's per-user resume collection.

    Must use the SAME collection the ingestion pipeline writes to
    (`resume_collection_name(user_id)`), otherwise retrieval silently returns
    nothing even though the embeddings were stored successfully.
    """
    if not user_id:
        logger.warning("retrieve_relevant_chunks: no user_id provided, skipping RAG retrieval")
        return []

    collection_name = resume_collection_name(user_id)
    try:
        retriever = RetrieverService(get_embeddings(), collection_name)
        docs = await retriever.retrieve_documents(topic, k=k)
        logger.info(
            "retrieve_relevant_chunks: collection=%s topic=%r retrieved=%d",
            collection_name, topic, len(docs) if docs else 0,
        )
        return [doc.page_content for doc in docs] if docs else []
    except Exception:
        logger.exception(
            "retrieve_relevant_chunks: retrieval failed for collection=%s", collection_name
        )
        return []
