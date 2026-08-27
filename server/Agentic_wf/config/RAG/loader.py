import os
import tempfile
import requests
from pathlib import Path
from urllib.parse import urlparse
from Agentic_wf.core import LoadError
from Agentic_wf.config.settings import get_settings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

settings = get_settings()

class Loader:
    @staticmethod
    def _download_remote_file(url: str) -> str:
        """Download a remote file (like Cloudinary) to a temporary local file"""
        temp_dir = tempfile.gettempdir()
        filename = os.path.basename(urlparse(url).path)
        temp_path = os.path.join(temp_dir, filename)
        
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return temp_path

    @staticmethod
    def load(file_path: str):
        # Handle URLs first
        parsed = urlparse(file_path)
        is_url = all([parsed.scheme, parsed.netloc])
        
        # Convert URL to local temp file if needed
        local_path = Loader._download_remote_file(file_path) if is_url else file_path
        
        # Now load the local file
        ext = Path(local_path).suffix.lower()
        try:
            if '.pdf' == ext:
                return PyPDFLoader(local_path)
            elif '.docx' == ext:
                return Docx2txtLoader(local_path)
            elif '.txt' == ext:
                return TextLoader(local_path)
        except Exception as e:
            raise LoadError(f'Failed to load file {file_path}', file_path=file_path, details={'error': str(e)})