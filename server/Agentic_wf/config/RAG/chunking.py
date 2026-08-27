from Agentic_wf.config.settings import get_settings
from langchain_text_splitters import RecursiveCharacterTextSplitter




settings = get_settings()
class Chunking:

    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap


    def doc_splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap
        )
