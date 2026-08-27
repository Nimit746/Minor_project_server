import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from Agentic_wf.core import LLMError
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from Agentic_wf.config.settings import get_settings
load_dotenv()


settings = get_settings()

class LLM:
    @staticmethod
    def GroqLLM(model: str = None, temp: float=0.3):
        try:
            return ChatGroq(
                model=model or settings.groq_default_model,
                temperature=temp,
                api_key=settings.groq_api_key
            )
        except Exception as e:
            raise LLMError("Failed to initiate Groq LLM", model=model, details={"error": str(e)}) from e

    @staticmethod
    def AnthropicLLM(model: str = None, temp: float=0.3):
        try:
            return ChatAnthropic(
                model=model or settings.anthropic_model,
                temperature=temp,
                api_key=settings.anthropic_api_key
            )
        except Exception as e:
            raise LLMError("Failed to initiate Anthropic LLM", model=model, details={"error": str(e)}) from e


    @staticmethod
    def OpenAILLM(model: str = None, temp : float = 0.3):
        return ChatOpenAI(
            model = model or settings.openai_model,
            temperature = temp,
            api_key = settings.openai_api_key
        )


    _PROVIDERS = {
    "groq": GroqLLM,
    "anthropic": AnthropicLLM,
    "openai": OpenAILLM,
    }
    
    @classmethod
    def get_llm(cls, provider: str = None, **kwargs):
        provider = (provider or os.getenv('LLM_PROVIDER', 'groq')).lower()
        method = cls._PROVIDERS.get(provider)
        if method is None:
            raise LLMError(f"Unknown provider: {provider}", details={"available": list(cls._PROVIDERS.keys())})
        return method(**kwargs)