# C:\Users\gupta.000\Desktop\Minor\server\Agentic_wf\agents\resume_parse\nodes\download_file_node.py
import os
import tempfile
from Agentic_wf.core import FileDownloadError
from Agentic_wf.services.cloud import CloudinaryService
from Agentic_wf.agents.resume_parse.states import FileState


async def download_file(state: FileState) -> FileState:
    """
    Downloads a file from cloud storage to a temporary location for processing.
    Works in all environments including production by using system temp directories.
    
    Args:
        state: Current FileState containing file_url and filename
        
    Returns:
        Updated FileState with local_temp_path added to metadata
    """
    print("🔽 NODE: download_file - STARTED")
    print(f"📋 File URL from state: {state['file_url']}")
    print(f"📋 Filename: {state['filename']}")
    print(f"📋 Document ID: {state['document_id']}")

    try:
        cloud_service = CloudinaryService()
        filename = state['filename']
        document_id = state['document_id']
        
        # The correct public_id is "resumes/{document_id}" which is what we used for upload
        # This matches the destination_path from upload.py: f"resumes/{document_id}"
        cloud_path = f"resumes/{document_id}"
        print(f"☁️ Using cloud path (public_id): {cloud_path}")

        tempdir = tempfile.mkdtemp(prefix=f'resume_{document_id}_')
        print(f"📂 Created temp directory: {tempdir}")
        
        local_file_path = os.path.join(tempdir, filename)
        print(f"📄 Local file path will be: {local_file_path}")

        print(f"⬇️ Attempting Cloudinary download...")
        cloud_service.download_file(cloud_path, local_file_path)
        print(f"✅ Cloudinary download completed")

        if not os.path.exists(local_file_path):
            print(f"❌ File does not exist after download: {local_file_path}")
            raise FileDownloadError(f'File Download failed: {local_file_path} does not exist')

        file_size = os.path.getsize(local_file_path)
        print(f"📊 Downloaded file size: {file_size} bytes")
        
        if file_size == 0:
            raise FileDownloadError(f'Downloaded file is empty: {local_file_path}')

        print("✅ NODE: download_file - COMPLETED, temp path created")
        return {
            "status": "file_downloaded",
            "metadata": {
                **state['metadata'],
                "local_temp_path": local_file_path,
                "temp_directory": tempdir,
                "file_size_bytes": file_size
            },
            "error": None
        }
    except Exception as e:
        print(f"❌ NODE: download_file - FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "download_failed",
            "error": f"Failed to download file: {str(e)}"
        }