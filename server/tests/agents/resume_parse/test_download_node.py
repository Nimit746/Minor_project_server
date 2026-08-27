import os
import shutil
import pytest
from unittest.mock import Mock, patch
# Import from your project structure (works when tests are in server/tests/)
from Agentic_wf.agents.resume_parse.nodes.download_file_node import download_file
from Agentic_wf.core.exceptions import FileDownloadError


@pytest.fixture
def valid_input_state():
    """Fixture providing a valid input state for testing."""
    return {
        "event_id": "test_event_123",
        "document_id": "doc_456",
        "user_id": "user_789",
        "file_url": "https://res.cloudinary.com/your-cloud/test_resume.pdf",
        "filename": "test_resume.pdf",
        "status": "initialized",
        "documents": [],
        "metadata": {
            "upload_timestamp": "2026-08-16",
            "file_type": "pdf"
        },
        "chunks": [],
        "error": None
    }


@pytest.mark.asyncio
async def test_download_file_success(valid_input_state):
    """Test successful file download and state update."""
    # Mock the cloud service
    mock_cloud_service = Mock()
    
    # Track if download_file was called with correct args
    def mock_download(cloud_path, local_path):
        # Create a dummy file to simulate successful download
        with open(local_path, 'wb') as f:
            f.write(b"Test PDF content")
    
    mock_cloud_service.download_file = mock_download
    
    # Patch the correct import path
    with patch('Agentic_wf.agents.resume_parse.nodes.download_file_node.CloudinaryService', return_value=mock_cloud_service):
        # Execute the download node
        result = await download_file(valid_input_state)
        
        # Verify only expected fields are returned (LangGraph pattern)
        assert set(result.keys()) == {"status", "metadata", "error"}
        assert result["status"] == "file_downloaded"
        assert result["error"] is None
        
        # Verify metadata was properly merged
        assert "upload_timestamp" in result["metadata"]  # Original metadata preserved
        assert "file_type" in result["metadata"]        # Original metadata preserved
        assert "local_temp_path" in result["metadata"]  # New field added
        assert "temp_directory" in result["metadata"]   # New field added
        assert result["metadata"]["file_size_bytes"] == 16  # Size of our test content
        
        # Verify temp file was created and can be cleaned up
        temp_dir = result["metadata"]["temp_directory"]
        assert os.path.exists(temp_dir)
        assert os.path.exists(result["metadata"]["local_temp_path"])
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_download_file_not_found(valid_input_state):
    """Test handling when downloaded file doesn't exist."""
    mock_cloud_service = Mock()
    mock_cloud_service.download_file = lambda x, y: None  # Don't create the file
    
    with patch('Agentic_wf.agents.resume_parse.nodes.download_file_node.CloudinaryService', return_value=mock_cloud_service):
        result = await download_file(valid_input_state)
        
        assert result["status"] == "download_failed"
        assert "does not exist" in result["error"]


@pytest.mark.asyncio
async def test_download_file_empty(valid_input_state):
    """Test handling when downloaded file is empty (0 bytes)."""
    mock_cloud_service = Mock()
    
    def mock_download(cloud_path, local_path):
        # Create an empty file
        open(local_path, 'a').close()
    
    mock_cloud_service.download_file = mock_download
    
    with patch('Agentic_wf.agents.resume_parse.nodes.download_file_node.CloudinaryService', return_value=mock_cloud_service):
        result = await download_file(valid_input_state)
        
        assert result["status"] == "download_failed"
        assert "empty" in result["error"]
        
        # Cleanup temp dir
        if "temp_directory" in result.get("metadata", {}):
            temp_dir = result["metadata"]["temp_directory"]
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_cloud_path_extraction_direct_cloud_path(valid_input_state):
    """Test cloud path extraction works with direct cloud paths (not URLs)."""
    # Override file_url to be a direct cloud path
    valid_input_state["file_url"] = "resumes/test_resume"  # Direct cloud public_id
    
    mock_cloud_service = Mock()
    called_cloud_path = None
    
    def mock_download(cloud_path, local_path):
        nonlocal called_cloud_path
        called_cloud_path = cloud_path
        with open(local_path, 'wb') as f:
            f.write(b"Test content")
    
    mock_cloud_service.download_file = mock_download
    
    with patch('Agentic_wf.agents.resume_parse.nodes.download_file_node.CloudinaryService', return_value=mock_cloud_service):
        await download_file(valid_input_state)
        assert called_cloud_path == "resumes/test_resume"  # Cloud path preserved


@pytest.mark.asyncio
async def test_exception_handling(valid_input_state):
    """Test general exception handling in the node."""
    mock_cloud_service = Mock()
    mock_cloud_service.download_file = Mock(side_effect=Exception("Network error"))
    
    with patch('Agentic_wf.agents.resume_parse.nodes.download_file_node.CloudinaryService', return_value=mock_cloud_service):
        result = await download_file(valid_input_state)
        
        assert result["status"] == "download_failed"
        assert "Network error" in result["error"]