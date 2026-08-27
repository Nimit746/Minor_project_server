from pydantic import Field
from typing import Annotated, Dict, Optional, TypedDict


class FileState(TypedDict):
    event_id: str

    document_id: str
    user_id: str

    file_url: str
    filename: str

    status: str

    documents: list[object]
    metadata: Dict[str, object]
    chunks: list[object]

    error: Optional[str]
    