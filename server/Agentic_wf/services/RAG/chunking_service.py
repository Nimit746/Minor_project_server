from Agentic_wf.config import Chunking
from langchain_core.documents import Document

class ChunkingService:
    def __init__(self):
        self.splitter = Chunking().doc_splitter()

    def split_documents(self, docs: list[Document]):
        return self.splitter.split_documents(docs)
