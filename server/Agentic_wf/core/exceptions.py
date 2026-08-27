class AgenticWorkflowError(Exception):

    """Base exception for the agentic workflow layer.

    All custom exceptions in this module inherit from this class,
    allowing callers to catch any workflow-related error with a
    single except clause if needed.
    """

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


    def __str__(self) -> str:
        if self.details:
            return f'{self.message} | details={self.details}'
        return self.message



class LLMError(AgenticWorkflowError):
    """Raised when an LLM operations fails (API error, timeout, bad response)."""

    def __init__(self, message: str, *, query: str | None = None, details: dict | None = None):
        super().__init__(message, details=details)
        self.query = query



class ResumeParseError(AgenticWorkflowError):
    """Raised when resume parsing fails (unreadable file, bad format, extraction failure)."""

    def __init__(self, message: str, *, file_name: str | None= None, details: dict | None = None):
        super().__init__(message, details=details)
        self.file_name = file_name



class RetrievalError(AgenticWorkflowError):
    """Raised when retrieval (vector search / RAG lookup) fails"""

    def __init__(self, message: str, *, query: str | None = None, details: dict | None = None):
        super().__init__(message, details = details)
        self.query = query


class QuestionGenerationError(AgenticWorkflowError):
    """Raised when question generation fails"""

    def __init__(self, message: str, *, topic: str | None = None, details: dict | None = None):
        super().__init__(message, details=details)
        self.topic = topic


class EvaluationError(AgenticWorkflowError):
    """Raised when answer evaluation fails"""

    def __init__(self, message: str, *, question_id: str | None = None, details: dict | None = None):
        super().__init__(message, details=details)
        self.question_id = question_id



class LoadError(AgenticWorkflowError):
    """Raised when the file is not loaded properly"""
    
    def __init__(self, message: str, *, file_path: str | None = None, details: dict | None = None):
        super().__init__(message, details=details)
        self.file_path = file_path



class FileDownloadError(AgenticWorkflowError):
    """
    Exception raised when a file download operation from cloud storage fails.

    This exception is used to handle various download failures including:
    - Network issues preventing file retrieval
    - File not found in cloud storage
    - Empty or corrupted downloaded files
    - Permission errors accessing cloud storage
    """

    def __init__(self, message: str = 'Failed to download file from the cloud storage'):
        """
        Initialize the exception with a message.
        Args:
            message: Detailed error message describing the download failure.
        """
        super().__init__(message)
        self.message = message
