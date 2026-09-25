import re

def extract_skills_heuristic(resume_text: str) -> list[str]:
    """
    Fallback keyword matching for common programming languages, frameworks,
    tools, databases, and technical concepts.
    """
    common_skills = [
        "python", "javascript", "typescript", "java", "c++", "c#", "golang", "rust",
        "react", "next.js", "node.js", "fastapi", "django", "flask", "docker",
        "kubernetes", "aws", "gcp", "azure", "mongodb", "postgresql", "mysql",
        "redis", "data structures", "algorithms", "system design", "machine learning",
        "deep learning", "natural language processing", "nlp", "large language models",
        "llm", "generative ai", "rest api", "graphql", "microservices", "sql", "git",
        "github", "tensorflow", "pytorch", "scikit-learn",
    ]
    text_lower = resume_text.lower()
    found_skills = []
    for skill in common_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    # Remove duplicates while preserving order
    unique_skills = list(dict.fromkeys(found_skills))
    return [skill.title() for skill in unique_skills]