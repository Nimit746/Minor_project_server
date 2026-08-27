# C:\Users\gupta.000\Desktop\Minor\server\Agentic_wf\agents\resume_parse\nodes\chunk.py
from langchain_core.documents import Document
from Agentic_wf.services import ChunkingService
from Agentic_wf.agents.resume_parse.states import FileState


async def chunk_documents(state: FileState) -> FileState:
    """
    Splits loaded documents into smaller chunks for embedding and vector storage.
    Uses your existing ChunkingService to handle text splitting.
    
    Args:
        state: Current FileState containing loaded documents
        
    Returns:
        Only the updated state fields (LangGraph merges them automatically)
    """
    print("✂️ NODE: chunk_documents - STARTED")
    try:
        # Get the loaded documents from state
        documents = state.get('documents', [])
        if not documents:
            raise ValueError("No documents found to chunk. Load file first.")
        
        # Initialize your existing chunking service
        chunker = ChunkingService()
        
        # Split documents into chunks using your chunking logic
        chunked_docs: list[Document] = chunker.split_documents(documents)
        
        if not chunked_docs:
            raise ValueError(f"Chunking failed: No chunks created from {len(documents)} documents")
        
        # Add chunk index metadata to each chunk
        for i, chunk in enumerate(chunked_docs):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunked_docs)
        
        # Return ONLY the changed fields (LangGraph handles merging)
        print(f"✅ NODE: chunk_documents - COMPLETED, created {len(chunked_docs)} chunks")
        return {
            "status": "documents_chunked",
            "chunks": chunked_docs,
            "metadata": {
                **state['metadata'],
                "total_chunks_created": len(chunked_docs)
            },
            "error": None
        }
        
    except Exception as e:
        print(f"❌ NODE: chunk_documents - FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "chunking_failed",
            "error": f"Failed to chunk documents: {str(e)}"
        }