import io
from PyPDF2 import PdfReader

def _extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    """Extract text from a PDF file stream."""
    reader = PdfReader(file_stream)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text)
    return "\n".join(pages)