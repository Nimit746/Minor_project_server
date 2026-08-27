from Agentic_wf.config import get_embeddings


class EmbeddingService:

    def __init__(self):
        self.embeddings = get_embeddings()


    async def embed_query(self, text: str) -> list[float]:
        """Embed a query text into a vector."""
        return await self.embeddings.aembed_query(text)

    async  def embed_docs(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents into the vectors"""
        return await self.embeddings.aembed_documents(texts)
