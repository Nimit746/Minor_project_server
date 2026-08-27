# C:\Users\gupta.000\Desktop\Minor\server\Agentic_wf\services\RAG\vector_store_service.py
from Agentic_wf.config import VectorStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class VectorStoreService:
    def __init__(self, embeddings: Embeddings, collection_name: str):
        self.vector_storage = VectorStore(embeddings, collection_name)

    async def add_docs(self, documents: list[Document]):
        return await self.vector_storage.aadd_documents(documents)

    async def search_similarity(self, query: str, k: int = 5, filter: dict = None):
        return await self.vector_storage.asimilarity_search(query, k, filter)