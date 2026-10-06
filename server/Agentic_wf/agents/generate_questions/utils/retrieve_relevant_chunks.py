from Agentic_wf.config import get_embeddings, Retriever as ConfigRetriever

async def retrieve_relevant_chunks(topic: str, k: int = 3) -> list[str]:
    """Retrieve relevant chunks from vector DB for the given topic."""
    try:
        embeddings = get_embeddings()
        retriever = ConfigRetriever(embeddings, "default_collection")
        docs = await retriever.aretrieve(topic, k=k)
        if docs:
            return [doc.page_content for doc in docs]
        return []
    except Exception:
        return []