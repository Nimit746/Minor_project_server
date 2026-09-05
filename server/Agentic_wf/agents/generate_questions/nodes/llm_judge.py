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
        # More robust matching - handle any extra text the LLM might return
        return "true" in result or "correct" in result or "yes" in result
    except Exception as e:
        print(f"LLM judge failed: {e}")
        return False  # Default to incorrect on failure

# Fixed sandbox test function that actually works for testing
# In production, this would be replaced with real sandbox execution
async def run_sandbox_tests(candidate_answer: str, question) -> bool:
    """Run sandboxed tests for coding questions (Stage 6)."""
    # For development/testing: if the candidate's answer matches the correct answer,
    # mark it as correct (simulating passing sandbox tests)
    if hasattr(question, 'correct_answer') and question.correct_answer:
        is_correct = candidate_answer.strip() == question.correct_answer.strip()
        if is_correct:
            print("Sandbox tests passed! - coding answer marked as correct")
        else:
            print("Sandbox tests failed - coding answer marked as incorrect")
        return is_correct
    print("No correct answer found - marking coding answer as incorrect")
    return False