from Agentic_wf.config import LLM

class LLMService:
    def __init__(self, provider: str = None, **kwargs):
        self.llm = LLM.get_llm(provider, **kwargs)
    def invoke(self, prompt: str):
        return self.llm.invoke(prompt)

    async def ainvoke(self, prompt: str):
        return await self.llm.ainvoke(prompt)
        
    def stream(self, prompt: str):
        for chunk in self.llm.stream(prompt):
            yield chunk

    def with_structured_output(self, schema, **kwargs):
        """Expose structured output from the underlying LangChain model."""
        return self.llm.with_structured_output(schema, **kwargs)
