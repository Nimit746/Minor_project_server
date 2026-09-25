import io
import docx

def _extract_text_from_docx(file_stream: io.BytesIO) -> str:
    """Extract text from a DOCX file stream."""
    document = docx.Document(file_stream)
    paragraphs = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)