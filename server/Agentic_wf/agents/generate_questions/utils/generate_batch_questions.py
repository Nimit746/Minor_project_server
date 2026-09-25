import uuid
import json
import asyncio
from typing import List
from Agentic_wf.config import LLM
from Agentic_wf.agents.generate_questions.states import Question
from Agentic_wf.agents.generate_questions.prompts import (
    question_generation_prompt,
    rag_question_generation_prompt,
)
from Agentic_wf.agents.generate_questions.utils.clean_llm_json_response import clean_llm_json_response
from Agentic_wf.agents.generate_questions.utils.get_safe_batch_size import get_safe_batch_size

async def generate_batch_questions(
    topic: str,
    difficulty: str,
    retrieved_chunks: list[str] = None,
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None,
    batch_size: int = None,  # Auto-determined if not specified
    question_type: str = "mcq"
) -> List[Question]:
    """
    Generate multiple questions in a single LLM call to optimize token usage.
    Caches all generated questions for future use.
    Now supports both MCQ and subjective (open-ended) questions with improved reliability.
    """
    # Use safe batch size if not explicitly provided
    if batch_size is None:
        batch_size = get_safe_batch_size(question_type)
    
    llm = LLM.get_llm("groq")

    # Create messages using the latest imported prompt functions
    if retrieved_chunks:
        prompt_value = rag_question_generation_prompt(
            topic=topic,
            difficulty=difficulty,
            retrieved_chunks=retrieved_chunks,
            company_name=company_name,
            target_role=target_role,
            candidate_skills=candidate_skills,
            question_type=question_type
        )
    else:
        prompt_value = question_generation_prompt(
            topic=topic,
            difficulty=difficulty,
            company_name=company_name,
            target_role=target_role,
            candidate_skills=candidate_skills,
            question_type=question_type
        )

    # The prompt functions return a ChatPromptValue, which has a `messages` attribute
    # containing the list of BaseMessage objects we need.
    messages = prompt_value.messages
    
    # Get the base system prompt and modify it to request a JSON array of questions
    base_system_prompt = messages[0].content
    
    # Enhanced batch system prompt with strict JSON requirements
    batch_system_prompt = base_system_prompt.replace(
        "You must return ONLY a valid JSON object",
        f"You must return ONLY a valid JSON array of {batch_size} JSON objects. NO extra text, NO markdown, NO repetition."
    )
    
    # Add strict JSON schema enforcement based on question type
    if question_type == "open_ended" or question_type == "coding":
        batch_system_prompt += """
        CRITICAL JSON RULES FOR OPEN-ENDED/CODING QUESTIONS:
        - ONLY include these fields: "id", "topic", "difficulty", "question_type", "question_text", "rubric"
        - NEVER include an "options" array or "correct_answer" field
        - The rubric must be a concise string (not an array)
        """
    else:  # MCQ questions
        batch_system_prompt += """
        CRITICAL JSON RULES FOR MCQ QUESTIONS:
        - ONLY include these fields: "id", "topic", "difficulty", "question_type", "question_text", "options", "correct_answer"
        - NEVER include a "rubric" field
        - The options array must have exactly 4 strings
        """
    
    # Ultra-strict additional instruction to prevent hallucinations
    additional_instruction = f"""
    Generate EXACTLY {batch_size} unique {question_type} questions.
    - All JSON objects must be properly separated by commas
    - No trailing commas
    - No repeated text
    - The entire JSON array must be properly closed
    """
    
    # Update the system message to use the batch version with strict rules
    messages[0].content = batch_system_prompt
    # Add the strict additional instruction to the user message
    messages[1].content += additional_instruction

    # Enhanced retry logic with better backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Generating batch attempt {attempt+1}/{max_retries}, batch_size={batch_size}, type={question_type}")
            response = await llm.ainvoke(messages)
            response_text = response.content.strip()
            # print(f"Raw LLM response length: {len(response_text)}")
            
            # Apply robust JSON cleaning
            cleaned_response = clean_llm_json_response(response_text)
            print(f"Cleaned JSON: {cleaned_response[:500]}...")  # Log first 500 chars for debugging
            
            if not cleaned_response:
                raise ValueError("Empty cleaned JSON response")
            
            # Parse JSON array with improved error handling
            questions_data = json.loads(cleaned_response)

            # Handle case where model returns a single dict instead of a list
            if isinstance(questions_data, dict):
                questions_data = [questions_data]
            
            # Validate we got the expected number of questions
            if len(questions_data) < batch_size:
                print(f"Warning: Only got {len(questions_data)} questions, expected {batch_size}")

            # Validate and convert to Question objects with error handling for each question
            questions = []
            for i, q_data in enumerate(questions_data):
                try:
                    # Ensure all questions have an ID
                    if not q_data.get("id"):
                        q_data["id"] = str(uuid.uuid4())
                    # For open-ended questions, ensure options is None
                    if question_type in ["open_ended", "coding"]:
                        q_data["options"] = None
                        q_data["correct_answer"] = None
                    # For MCQs, ensure rubric is None
                    else:
                        q_data["rubric"] = None
                    questions.append(Question(**q_data))
                except Exception as q_err:
                    print(f"Skipping invalid question {i}: {q_err}")
                    continue

            if questions:
                print(f"Successfully generated {len(questions)} valid questions")
                return questions
            else:
                raise ValueError("No valid questions could be parsed from response")

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {str(e)}")
            if attempt == max_retries - 1:
                print(f"All attempts failed. Returning empty list. Error: {e}")
                return []
            # Exponential backoff
            await asyncio.sleep(1.5 * (attempt + 1))