from Agentic_wf.config import LLM

class LLMService:
    
    def __init__(self, provider: str = None, **kwargs):
        self.llm = LLM.get_llm(provider, **kwargs)
    
    def invoke(self, prompt: str):
        return self.llm.invoke(prompt)

    def stream(self, prompt: str):
        for chunk in self.llm.stream(prompt):
            yield chunk
