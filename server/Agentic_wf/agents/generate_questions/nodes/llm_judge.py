from Agentic_wf.config.llm import LLM

OPEN_ENDED_JUDGE_PROMPT = """You are an answer evaluator. Given a candidate's answer and a rubric, determine if the answer is correct.

Return ONLY "True" if the answer meets the rubric's requirements, otherwise "False". No other text.

Rubric: {rubric}
Candidate's answer: {candidate_answer}"""

async def groq_judge(candidate_answer: str, rubric: str) -> bool:
    """Use Groq to evaluate open-ended answers (Stage 6)."""
    llm = LLM.get_llm("groq", temp=0.0)  # Use low temperature for consistent evaluation
    
    messages = [
        {"role": "user", "content": OPEN_ENDED_JUDGE_PROMPT.format(
            rubric=rubric,
            candidate_answer=candidate_answer
        )}
    ]
    
    try:
        response = await llm.ainvoke(messages)
        result = response.content.strip().lower()
        return result == "true"
    except Exception as e:
        print(f"LLM judge failed: {e}")
        return False  # Default to incorrect on failure

# Placeholder for sandbox test execution (would be implemented in a real system)
async def run_sandbox_tests(candidate_answer: str, question) -> bool:
    """Run sandboxed tests for coding questions (Stage 6)."""
    # In a real implementation, this would execute the code in a secure sandbox
    # For now, return False as a placeholder
    print("Sandbox execution not implemented - marking coding answer as incorrect")
    return False