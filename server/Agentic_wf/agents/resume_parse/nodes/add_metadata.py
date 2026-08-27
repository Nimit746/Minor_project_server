from datetime import datetime
from Agentic_wf.agents.resume_parse.states import FileState


async def add_metadata(state: FileState) -> FileState:
    """
    Enriches document chunks with additional metadata for better filtering and search.
    Runs after chunking but before storing in vector database.
    
    Args:
        state: Current FileState containing chunked documents
        
    Returns:
        Only the updated state fields (LangGraph merges them automatically)
    """
    print("🏷️ NODE: add_metadata - STARTED")

    try:
        chunks = state.get('chunks', [])
        if not chunks:
            raise ValueError("No chunks found to add metadata to. Chunk documents first.")
        
        # Get base metadata from state
        base_metadata = {
            "processing_timestamp": datetime.utcnow().isoformat(),
            "pipeline_version": "1.0",  # Update as you iterate on your pipeline
            "workflow_type": "resume_parsing",
            "environment": "production"  # You could pull this from config
        }
        
        # Enrich each chunk with combined metadata
        for chunk in chunks:
            # Merge base metadata with existing chunk metadata
            chunk.metadata.update({
                **base_metadata,
                # Add any resume-specific extracted metadata here
                # You could add NER results, parsed entities, etc.
                "is_resume": True,
                "content_type": "professional_document"
            })
        
        # Calculate total enriched chunks for metadata
        total_enriched = len(chunks)
        print(f"✅ NODE: add_metadata - COMPLETED")

        # Return ONLY the changed fields
        return {
            "status": "metadata_added",
            "chunks": chunks,  # Return the updated chunks with new metadata
            "metadata": {
                **state['metadata'],
                "chunks_enriched": total_enriched,
                "enrichment_timestamp": base_metadata["processing_timestamp"]
            },
            "error": None
        }
        
    except Exception as e:
        print(f"❌ NODE: add_metadata - Failed")
        
        return {
            "status": "metadata_addition_failed",
            "error": f"Failed to add metadata to chunks: {str(e)}"
        }