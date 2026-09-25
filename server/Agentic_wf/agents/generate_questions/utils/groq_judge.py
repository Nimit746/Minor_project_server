from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

class Judge(BaseModel):
    score: int = Field(description="The score from 0-10 for the user's answer.")
    critique: str = Field(description="The critique of the user's answer.")

async def groq_judge(question: str, answer: str) -> Judge:
    """
    Uses a structured output LLM to judge the user's answer.
    """
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    structured_llm = llm.with_structured_output(Judge)
    
    system = """You are a fair and honest judge of a user's answer to a question.
    Score the user's answer on a scale of 0-10, where 0 is a completely incorrect answer and 10 is a perfect answer.
    Provide a critique of the user's answer, explaining your score."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Question: {question}\n\nAnswer: {answer}"),
    ])
    
    chain = prompt | structured_llm
    return await chain.ainvoke({"question": question, "answer": answer})