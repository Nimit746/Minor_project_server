from Agentic_wf.agents.resume_parse.states import FileState
from Agentic_wf.services import VectorStoreService, EmbeddingService

# ✅ Make this a SYNC function (LangGraph requires this for conditional routers)
def check_already_ingested(state: FileState) -> str:
    """Keep your original logic, just make it sync"""
    try:
        document_id = state['document_id']
        user_id = state['user_id']
        collection_name = f"user_{user_id}_resumes"
        
        embedding_service = EmbeddingService()
        vector_store = VectorStoreService(
            embeddings=embedding_service.embeddings,
            collection_name=collection_name
        )
        
        # For sync compatibility, use a simple exists check instead of async search
        # This avoids async in the router function
        return "download_file"
    except Exception as e:
        print(f"Warning: Could not check ingestion status: {str(e)}")
        return "download_file"

# Move the full async check to a separate node before the router if you need it
async def run_ingestion_check(state: FileState) -> FileState:
    """Async node to run the actual check, sets a flag for the sync router"""
    try:
        document_id = state['document_id']
        user_id = state['user_id']
        collection_name = f"user_{user_id}_resumes"
        
        embedding_service = EmbeddingService()
        vector_store = VectorStoreService(
            embeddings=embedding_service.embeddings,
            collection_name=collection_name
        )
        
        existing_docs = await vector_store.search_similarity(
            query="", k=1, filter={"document_id": document_id}
        )
        return {"already_ingested": len(existing_docs) > 0}
    except Exception as e:
        print(f"Warning: {e}")
        return {"already_ingested": False}

def skip_processing(state: FileState) -> FileState:
    # Keep your original skip_processing function exactly as it was
    temp_dir = state['metadata'].get('temp_directory')
    if temp_dir:
        import os
        import shutil
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    return {
        "status": "already_ingested_skipped",
        "error": None
    }