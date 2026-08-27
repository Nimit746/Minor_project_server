# C:\Users\gupta.000\Desktop\Minor\server\Agentic_wf\agents\resume_parse\nodes\store.py
import os
import shutil
from Agentic_wf.agents.resume_parse.states import FileState
from Agentic_wf.services import VectorStoreService, EmbeddingService


async def store_in_vector_db(state: FileState) -> FileState:
    """
    Stores document chunks in the vector database with their embeddings.
    Automatically cleans up temporary files after processing (success or failure).
    
    Args:
        state: Current FileState containing chunked, metadata-enriched documents
        
    Returns:
        Only the updated state fields (LangGraph merges them automatically)
    """
    print("💾 NODE: store_in_vector_db - STARTED")
    temp_dir = state['metadata'].get('temp_directory')  # Get temp dir from download node
    chunks = []
    try:
        chunks = state.get('chunks', [])
        print(f"📊 Found {len(chunks)} chunks to store")
        
        if not chunks:
            raise ValueError("No document chunks found to store in vector database")
        
        # Initialize your existing services
        embedding_service = EmbeddingService()
        vector_store = VectorStoreService(
            embeddings=embedding_service.embeddings, 
            collection_name=f"user_{state['user_id']}_resumes"  # Isolated collection per user
        )
        
        # Store chunks in vector database (handles embedding generation automatically)
        await vector_store.add_docs(chunks)
        
        # Clean up temporary files after successful storage
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            temp_cleanup_success = True
        else:
            temp_cleanup_success = False
        
        # Return ONLY the changed fields
        print(f"✅ NODE: store_in_vector_db - COMPLETED, stored {len(chunks)} chunks")
        return {
            "status": "stored_in_vector_db",
            "metadata": {
                **state['metadata'],
                "chunks_stored": len(chunks),
                "temp_cleanup_success": temp_cleanup_success
            },
            "error": None
        }
        
    except Exception as e:
        print(f"❌ NODE: store_in_vector_db - FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        # Always clean up temp files even if storage fails (prevents disk bloat)
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Best-effort cleanup if something goes wrong
        
        # Report the failure
        return {
            "status": "storage_failed",
            "error": f"Failed to store in vector database: {str(e)}"
        }