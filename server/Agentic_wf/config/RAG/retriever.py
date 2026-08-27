from langchain_qdrant import QdrantVectorStore
from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient
from Agentic_wf.config.settings import get_settings
from langchain_core.retrievers import BaseRetriever



settings = get_settings()


class Retriever:

    def __init__(self, embeddings: Embeddings, collection_name: str):
        print(f"🔧 Initializing Retriever for collection: {collection_name}")
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.client = QdrantClient(
            api_key=settings.qdrant_api_key,
            url=settings.qdrant_url,
            check_compatibility=False
        )
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )


    def get_retriever(self, k: int = 5) -> BaseRetriever:
        """Return a LangChain retriever instance with the given k."""
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    async def aretrieve(self, query: str, k: int = 5, filter=None):
        """Async retrieval of similar documents."""
        print(f"🔍 Retrieving documents for query: {query[:50]}...")
        results = await self.vector_store.asimilarity_search(
            query,
            k=k,
            filter=filter
        )
        print(f"✅ Retrieved {len(results)} documents")
        return results