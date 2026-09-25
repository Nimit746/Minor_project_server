from typing import Any
import httpx
from langchain_core.tools import tool
from Agentic_wf.config import LLM
from Agentic_wf.agents.generate_questions.states import ResumeAnalysis
from Agentic_wf.agents.generate_questions.prompts import build_resume_analyzer_prompt
from Agentic_wf.agents.generate_questions.utils import (
    _download_file,
    _extract_resume_text,
    extract_skills_heuristic,
)


async def _analyze_with_llm(resume_text: str) -> ResumeAnalysis:
    """Analyze resume text using the configured LLM."""
    llm = LLM.get_llm(
        "groq",
        temp=0.1,
    )
    # Limit the amount of text sent to the LLM.
    # This can be increased later depending on the model/context window.
    resume_text_for_llm = resume_text[:12000]
    prompt = build_resume_analyzer_prompt(resume_text_for_llm)
    # Ask LangChain to enforce the Pydantic schema.
    structured_llm = llm.with_structured_output(ResumeAnalysis)
    result = await structured_llm.ainvoke(prompt)
    if isinstance(result, ResumeAnalysis):
        return result
    # Defensive handling in case the configured LLM wrapper
    # returns a dictionary instead of a Pydantic object.
    if isinstance(result, dict):
        return ResumeAnalysis.model_validate(result)
    raise ValueError(
        f"Unexpected structured LLM response type: {type(result).__name__}"
    )


@tool
async def analyze_resume(file_url: str) -> dict[str, Any]:
    """
    Download and analyze a candidate resume.

    The resume must be a publicly accessible PDF or DOCX file.

    The tool:
    1. Downloads the resume.
    2. Extracts its text.
    3. Uses an LLM to identify technical skills, primary language,
       experience level, project domains, and interview topics.
    4. Falls back to heuristic skill extraction if the LLM fails.

    Args:
        file_url: Public URL of the candidate's PDF or DOCX resume.

    Returns:
        Dictionary containing:
        - skills
        - primary_language
        - experience_level
        - project_domains
        - recommended_topics
        Or an error dictionary if the file cannot be downloaded or parsed.
    """
    if not file_url or not file_url.strip():
        return {
            "error": "A resume file URL is required."
        }
    file_url = file_url.strip()

    # -----------------------------------------------------------------------
    # Download
    # -----------------------------------------------------------------------
    try:
        file_stream = await _download_file(file_url)
    except httpx.HTTPStatusError as exc:
        return {
            "error": (
                f"Failed to download resume. "
                f"HTTP status: {exc.response.status_code}"
            )
        }
    except httpx.RequestError as exc:
        return {
            "error": f"Failed to download resume: {str(exc)}"
        }
    except Exception as exc:
        return {
            "error": f"Unexpected download error: {str(exc)}"
        }

    # -----------------------------------------------------------------------
    # Extract text
    # -----------------------------------------------------------------------
    try:
        resume_text = _extract_resume_text(
            file_stream=file_stream,
            file_url=file_url,
        )
    except ValueError as exc:
        return {
            "error": str(exc)
        }
    except Exception as exc:
        return {
            "error": f"Failed to parse resume: {str(exc)}"
        }

    # -----------------------------------------------------------------------
    # Validate extracted text
    # -----------------------------------------------------------------------
    resume_text = resume_text.strip()
    if len(resume_text) < 20:
        return {
            "skills": [],
            "primary_language": None,
            "experience_level": None,
            "project_domains": [],
            "recommended_topics": [],
        }

    # -----------------------------------------------------------------------
    # LLM analysis
    # -----------------------------------------------------------------------
    try:
        analysis = await _analyze_with_llm(resume_text)
        return analysis.model_dump()

    # -----------------------------------------------------------------------
    # Fallback
    # -----------------------------------------------------------------------
    except Exception:
        skills = extract_skills_heuristic(resume_text)
        return {
            "skills": skills,
            "primary_language": None,
            "experience_level": None,
            "project_domains": [],
            "recommended_topics": [],
        }