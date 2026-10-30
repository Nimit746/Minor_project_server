import logging

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from Agentic_wf.config.settings import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    EMBEDDING_DIMENSION = 384  # BAAI/bge-small-en-v1.5
    _client: QdrantClient | None = None

    @classmethod
    def get_vector_client(cls) -> QdrantClient:
        """One shared client built from QDRANT_URL / QDRANT_API_KEY."""
        if cls._client is None:
            s = get_settings()
            logger.info("Connecting to Qdrant at %s (api_key set: %s)",
                        s.qdrant_url, bool(s.qdrant_api_key))
            cls._client = QdrantClient(
                url=s.qdrant_url,
                api_key=s.qdrant_api_key,
                check_compatibility=False,
                timeout=30,
            )
        return cls._client

    def __init__(self, embeddings: Embeddings, collection_name: str):
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.client = self.get_vector_client()
        self._ensure_collection_exists()
        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    def _ensure_collection_exists(self) -> None:
        # No blanket except: auth / URL / network errors surface as themselves.
        if self.client.collection_exists(self.collection_name):
            return

        logger.warning("Creating Qdrant collection: %s", self.collection_name)
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE,
                ),
            )
        except UnexpectedResponse as e:
            if e.status_code != 409:  # 409 = created concurrently, fine
                raise

        # Payload indexes for filtering (langchain-qdrant stores metadata under "metadata.")
        for field in ("metadata.document_id", "metadata.user_id"):
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        logger.info("Collection %s created", self.collection_name)

    @classmethod
    def document_exists(cls, collection_name: str, document_id: str) -> bool:
        """True if any chunk of this document is stored. Never creates the collection."""
        client = cls.get_vector_client()
        if not client.collection_exists(collection_name):
            return False
        result = client.count(
            collection_name=collection_name,
            count_filter=models.Filter(must=[
                models.FieldCondition(
                    key="metadata.document_id",
                    match=models.MatchValue(value=document_id),
                )
            ]),
            exact=True,
        )
        return result.count > 0

    async def aadd_documents(self, documents: list[Document]):
        ids = await self.store.aadd_documents(documents)
        info = self.client.get_collection(self.collection_name)
        logger.info("Added %d vectors to %s (total points: %s)",
                    len(ids), self.collection_name, info.points_count)
        return ids

    async def asimilarity_search(self, query: str, k: int = 5, filter=None):
        return await self.store.asimilarity_search(query, k=k, filter=filter)