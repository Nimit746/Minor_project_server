from Agentic_wf.config import Retriever
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever


class RetrieverService:
    def __init__(self, embeddings: Embeddings, collection_name: str):
        self.retriever_config = Retriever(embeddings, collection_name)

    def get_langchain_retriever(self, k: int = 5) -> BaseRetriever:
        """Get the LangChain BaseRetriever instance for use in chains."""
        return self.retriever_config.get_retriever(k=k)

    async def retrieve_documents(self, query: str, k: int = 5, filter: dict = None):
        """Directly retrieve documents for a given query."""
        return await self.retriever_config.aretrieve(query, k, filter)