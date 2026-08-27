# c:\Users\gupta.000\Desktop\Minor\server\test_imports.py
# Test script to check for circular imports
import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports for circular dependencies...")

try:
    # Test config imports first
    from Agentic_wf.config import (
        get_settings,
        get_cloud_settings,
        get_embeddings,
        LLM,
        VectorStore,
        Chunking,
        Loader
    )
    print("✅ All config imports successful")
    
    # Test services imports
    from Agentic_wf.services import (
        LLMService,
        EmbeddingService,
        VectorStoreService,
        ChunkingService,
        LoaderService,
        Ingestion
    )
    print("✅ All services imports successful")
    
    # Test that we can instantiate things
    settings = get_settings()
    cloud_settings = get_cloud_settings()
    embeddings = get_embeddings()
    llm = LLM.get_llm()
    
    print("✅ All config instances created successfully")
    
    print("\n🎉 No circular imports detected! All imports work correctly.")
    
except ImportError as e:
    print(f"\n❌ Import error detected: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\n⚠️  Other error (might be missing env vars, but no circular imports): {e}")
    print("   This is expected if .env variables aren't configured, but circular imports would have failed earlier.")