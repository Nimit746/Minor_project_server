"""
Cloudinary Service Implementation
Provides cloud storage operations using Cloudinary
"""
import os
from typing import Any, Dict, Optional, BinaryIO
import cloudinary
import cloudinary.uploader
import cloudinary.api

from Agentic_wf.services.cloud.base_cloud_service import BaseCloudService
from Agentic_wf.config import get_cloud_settings


class CloudinaryService(BaseCloudService):
    """Cloudinary implementation of the base cloud service."""
    
    def __init__(self):
        """Initialize Cloudinary configuration from settings."""
        settings = get_cloud_settings()
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret
        )
    
    def upload_file(self, file_path: str, destination_path: Optional[str] = None, context: Optional[str] = None, notification_url: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to Cloudinary with optional context and webhook notification."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        upload_options = {}
        if destination_path:
            upload_options['public_id'] = destination_path
        if context:  # Cloudinary context works without preconfiguring fields
            upload_options['context'] = context
        if notification_url:
            upload_options['notification_url'] = notification_url
    
        result = cloudinary.uploader.upload(file_path, **upload_options)
        # Add these lines after line 45 (right after result = cloudinary.uploader.upload(...))
        return {
                'url': result.get('secure_url'),
                'public_id': result.get('public_id'),
                'format': result.get('format'),
                'size': result.get('bytes'),
                'provider': 'cloudinary'
            }
    
    def upload_file_object(self, file_object: BinaryIO, destination_path: str) -> Dict[str, Any]:
        """Upload a file-like object to Cloudinary."""
        result = cloudinary.uploader.upload(file_object, public_id=destination_path)
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'format': result.get('format'),
            'size': result.get('bytes'),
            'provider': 'cloudinary'
        }
    
    def download_file(self, cloud_file_path: str, local_destination_path: str) -> None:
        """Download a file from Cloudinary to local filesystem."""
        url = self.get_file_url(cloud_file_path)
        import requests
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(local_destination_path), exist_ok=True)
        with open(local_destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def delete_file(self, cloud_file_path: str) -> bool:
        """Delete a file from Cloudinary."""
        result = cloudinary.uploader.destroy(cloud_file_path)
        return result.get('result') == 'ok'
    
    def get_file_url(self, cloud_file_path: str, expiry_seconds: Optional[int] = None) -> str:
        """Get a URL for a file in Cloudinary, optionally signed."""
        if expiry_seconds:
            return cloudinary.utils.cloudinary_url(cloud_file_path, sign_url=True, expires_at=int(os.time()) + expiry_seconds)[0]
        return cloudinary.utils.cloudinary_url(cloud_file_path)[0]
    
    def file_exists(self, cloud_file_path: str) -> bool:
        """Check if a file exists in Cloudinary."""
        try:
            cloudinary.api.resource(cloud_file_path)
            return True
        except cloudinary.api.NotFound:
            return False