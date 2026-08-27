from langchain_huggingface import HuggingFaceEmbeddings
from Agentic_wf.config.settings import get_settings


settings = get_settings()

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name = settings.embedding_model,
        model_kwargs={
            'token': settings.hf_token
        }
    )

