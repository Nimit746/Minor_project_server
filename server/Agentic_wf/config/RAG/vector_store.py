import logging
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

logger = logging.getLogger(__name__)

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
        logger.info("Initializing Qdrant VectorStore for collection: %s", collection_name)
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
            logger.info("Collection %s ready, current points: %s", self.collection_name, count)
        except Exception:
            # If collection does not exists then create the collection
            logger.warning("Creating new collection: %s", self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )
            logger.info("Collection %s created successfully", self.collection_name)






    async def aadd_documents(self, documents: list[Document]):
        """Store documents in Qdrant, confirming the persisted point count after the write."""
        before = self._point_count()
        logger.info(
            "Inserting %d documents into collection %s (points before: %s)",
            len(documents), self.collection_name, before,
        )

        ids = await self.store.aadd_documents(documents)

        after = self._point_count()
        logger.info(
            "Inserted %d vectors into collection %s (points after: %s)",
            len(ids), self.collection_name, after,
        )
        return ids

    def _point_count(self) -> int | None:
        """Best-effort persisted point count for the target collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count if hasattr(info, 'points_count') else None
        except Exception:
            logger.warning("Could not read point count for collection %s", self.collection_name)
            return None





    async def asimilarity_search(self, query: str, k=5, filter=None):
        # NOTE: must be awaited — returning the coroutine silently yields no results.
        return await self.store.asimilarity_search(
            query,
            k=k,
            filter = filter
        )