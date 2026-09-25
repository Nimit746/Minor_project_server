import io
from Agentic_wf.agents.generate_questions.utils.pdf_extractor import _extract_text_from_pdf
from Agentic_wf.agents.generate_questions.utils.docx_extractor import _extract_text_from_docx

def _extract_resume_text(
    file_stream: io.BytesIO,
    file_url: str,
) -> str:
    """Determine the file type and extract its text."""
    url_without_query = file_url.split("?", 1)[0].lower()
    if url_without_query.endswith(".pdf"):
        return _extract_text_from_pdf(file_stream)
    if url_without_query.endswith(".docx"):
        return _extract_text_from_docx(file_stream)
    raise ValueError(
        "Unsupported file type. Please provide a PDF or DOCX resume."
    )