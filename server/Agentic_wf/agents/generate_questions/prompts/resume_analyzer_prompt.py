from langchain_core.prompts import ChatPromptTemplate

# Chat prompt template for resume analysis
RESUME_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a technical resume parser and evaluator.
Analyze the resume text provided below and extract the candidate's technical attributes.

Rules:
1. Extract only information that is supported by the resume.
2. Do not invent skills, experience, projects, or technologies.
3. "skills" should contain programming languages, frameworks, libraries, databases, cloud technologies, tools, and technical concepts explicitly present in the resume.
4. "primary_language" must contain exactly ONE primary programming language. If it cannot be determined reliably, return null.
5. "experience_level" must be exactly one of:
- "entry"
- "mid"
- "senior"
If it cannot be determined reliably, return null.
6. "project_domains" should describe the major technical domains represented by the candidate's projects.
7. "recommended_topics" should contain technical topics that would be useful for interviewing this candidate based on their resume.
8. Do not include explanations outside the structured response.
""",
        ),
        ("human", "Resume Text:\n{resume_text}"),
    ]
)

def build_resume_analyzer_prompt(resume_text: str):
    """Build the user prompt for resume analysis."""
    return RESUME_EXTRACTION_PROMPT.format_prompt(
        resume_text=resume_text
    )