import os
from Agentic_wf.services import LoaderService
from langchain_core.documents import Document
from Agentic_wf.agents.resume_parse.states import FileState


async def load_file(state: FileState) -> FileState:
    """
    Loads the downloaded file from temporary storage into LangChain documents.
    Uses the LoaderService to handle different file types (PDF, DOCX, etc.)
    
    Args:
        state: Current FileState containing local_temp_path in metadata
        
    Returns:
        Only the updated state fields (LangGraph merges them automatically)
    """
    print("📂 NODE: load_file - STARTED")

    try:
        # Get the temporary file path from metadata (created by download_file node)
        local_temp_path = state['metadata'].get('local_temp_path')
        if not local_temp_path or not os.path.exists(local_temp_path):
            raise FileNotFoundError(f"Temporary file not found: {local_temp_path}")
        
        # Initialize your existing loader service
        loader_service = LoaderService()
        
        # Load the file using the appropriate loader based on file type
        raw_loader = loader_service.load(local_temp_path)
        raw_docs: list[Document] = raw_loader.load()
        
        if not raw_docs:
            raise ValueError(f"No content could be loaded from file: {local_temp_path}")
        
        # Add consistent metadata to all documents for vector store filtering
        for doc in raw_docs:
            doc.metadata.update({
                "document_id": state['document_id'],
                "user_id": state['user_id'],
                "event_id": state['event_id'],
                "filename": state['filename'],
                "source": local_temp_path
            })
        print(f"✅ NODE: load_file - COMPLETED, loaded {len(raw_docs)} documents")

        # Return ONLY the changed fields (LangGraph merges these into state)
        return {
            "status": "file_loaded",
            "documents": raw_docs,
            "error": None
        }
        
    # Update the except block in load_file.py
    except Exception as e:
        print(f"❌ NODE: load_file - Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        # If anything fails, return only error-related fields
        return {
            "status": "load_failed",
            "error": f"Failed to load file: {str(e)}"
        }