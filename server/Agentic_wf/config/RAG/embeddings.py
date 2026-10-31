from functools import lru_cache
from Agentic_wf.config.settings import get_settings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings


settings = get_settings()

@lru_cache(maxsize=1)
def get_embeddings():
    return FastEmbedEmbeddings(
        model_name=settings.embedding_model,   # "BAAI/bge-small-en-v1.5"
        max_length=512,
        batch_size=8,
        threads=1,
    )
