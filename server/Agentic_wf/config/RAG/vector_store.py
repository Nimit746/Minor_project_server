import warnings
from qdrant_client.http import models
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_core.embeddings import Embeddings
from Agentic_wf.config.settings import get_settings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

settings = get_settings()

class VectorStore:
    # bge-small-en-v1.5 dimension
    EMBEDDING_DIMENSION = 384


    @staticmethod
    def get_vector_client():
        return QdrantClient(
            api_key=settings.qdrant_api_key,
            url=settings.qdrant_url,
            check_compatibility=False
        )




    def __init__(self, embeddings: Embeddings, collection_name: str):
        print(f"🔧 Initializing direct Qdrant VectorStore for: {collection_name}")
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.client = self.get_vector_client()
        self._ensure_collection_exists()
        self.store = QdrantVectorStore(
            client = self.client,
            collection_name = self.collection_name,
            embedding = self.embeddings
        )




    def _ensure_collection_exists(self):
        try:
            info = self.client.get_collection(self.collection_name)
            count = info.points_count if hasattr(info, 'points_count') else 0
            print(f"ℹ️ Collection ready, current points: {count}")
        except Exception:
            # If collection does not exists then create the collection
            print(f"⚠️ Creating new collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )
            print(f"✅ Collection created successfully")






    async def aadd_documents(self, documents: list[Document]):
        """Direct implementation - no LangChain wrapper issues"""
        print(f"📝 Adding {len(documents)} documents via Langchain wrapper to Qdrant")
        
        ids = await self.store.aadd_documents(documents)
        info = self.client.get_collection(self.collection_name)
        new_count = info.points_count if hasattr(info, 'points_count') else 0
        print(f"✅ SUCCESS! Added {len(ids)} vectors. Total now: {new_count}")
        return ids







    async def asimilarity_search(self, query: str, k=5, filter=None):
        return self.store.asimilarity_search(
            query,
            k=k,
            filter = filter
        )