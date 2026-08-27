from Agentic_wf.services.RAG.chunking_service import ChunkingService
from Agentic_wf.services.RAG.embeddings_service import EmbeddingService
from Agentic_wf.services.RAG.vector_store_service import VectorStoreService
from Agentic_wf.services.RAG.loader_service import LoaderService
from langchain_core.documents import Document

class Ingestion:

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.loader = LoaderService()
        self.chunker = ChunkingService()
        self.embed = EmbeddingService()
        self.vector_store = VectorStoreService(self.embed.embeddings, self.collection_name) # Give collection name and embeddings

    async def ingest(self, file_name: str):
        try:
            raw_loader = self.loader.load(file_name)
            raw_docs: list[Document] = raw_loader.load()

            chunker_docs = self.chunker.split_documents(raw_docs)

            await self.vector_store.add_docs(chunker_docs)

            success_msg = (
                f'Successfully ingested {len(chunker_docs)} document chunks.'
            )

        except Exception as e:
            error_msg = f"Ingestion failed for {file_name}: {str(e)}"
            raise RuntimeError(error_msg) from e


