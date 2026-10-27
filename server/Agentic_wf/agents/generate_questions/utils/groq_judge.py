
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from Agentic_wf.services import LLMService


class Judge(BaseModel):
    score: int = Field(
        ge=0,
        le=10,
        description="Score from 0 to 10 for the user's answer."
    )
    critique: str = Field(
        description="Explain the answer's strengths, weaknesses, and score."
    )


async def groq_judge(question: str, answer: str) -> Judge:
    """Evaluate a candidate's answer using structured LLM output."""

    llm = LLMService(
        provider="groq",
        model="openai/gpt-oss-20b",
        temp=0.0,
    )

    structured_llm = llm.with_structured_output(Judge)

    system = """
    You are a fair and objective technical interview evaluator.

    Evaluate the candidate's answer against the question.

    Scoring:
    - 0: Completely incorrect, irrelevant, or no meaningful answer.
    - 1-3: Major conceptual errors or very limited understanding.
    - 4-6: Partially correct, with notable omissions or inaccuracies.
    - 7-8: Correct and reasonably complete, with minor omissions.
    - 9: Excellent, accurate, and thorough.
    - 10: Fully correct, comprehensive, and precise.

    Do not award points for confident wording without technical correctness.
    Do not penalize the candidate for minor wording or grammar mistakes.
    Keep the critique concise and explain the main reason for the score.
    Return only the fields required by the output schema.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Question: {question}\n\nAnswer: {answer}"),
    ])

    chain = prompt | structured_llm

    return await chain.ainvoke({
        "question": question,
        "answer": answer,
    })
