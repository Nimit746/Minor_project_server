"""
Cloudflare R2 Service Implementation
Provides cloud storage operations using Cloudflare R2
"""
import os
from typing import Any, Dict, Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError

from Agentic_wf.services.cloud.base_cloud_service import BaseCloudService
from Agentic_wf.config import get_cloud_settings


class R2Service(BaseCloudService):
    """Cloudflare R2 implementation of the base cloud service."""
    
    def __init__(self):
        """Initialize R2 client from settings."""
        settings = get_cloud_settings()
        if not all([settings.r2_api_key, settings.r2_api_secret, settings.r2_cloud_name]):
            raise ValueError("R2 configuration is incomplete. Please check your environment variables.")
        
        # R2 uses S3-compatible API
        self.r2_client = boto3.client(
            's3',
            aws_access_key_id=settings.r2_api_key,
            aws_secret_access_key=settings.r2_api_secret,
            endpoint_url='https://' + os.getenv('CLOUD_R2_ACCOUNT_ID') + '.r2.cloudflarestorage.com'
        )
        self.bucket_name = settings.r2_cloud_name
        self.public_domain = os.getenv('CLOUD_R2_PUBLIC_DOMAIN')
    
    def upload_file(self, file_path: str, destination_path: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to R2."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        r2_path = destination_path or os.path.basename(file_path)
        self.r2_client.upload_file(file_path, self.bucket_name, r2_path)
        
        url = self._build_file_url(r2_path)
        return {
            'url': url,
            'key': r2_path,
            'bucket': self.bucket_name,
            'provider': 'r2'
        }
    
    def upload_file_object(self, file_object: BinaryIO, destination_path: str) -> Dict[str, Any]:
        """Upload a file-like object to R2."""
        self.r2_client.upload_fileobj(file_object, self.bucket_name, destination_path)
        
        url = self._build_file_url(destination_path)
        return {
            'url': url,
            'key': destination_path,
            'bucket': self.bucket_name,
            'provider': 'r2'
        }
    
    def download_file(self, cloud_file_path: str, local_destination_path: str) -> None:
        """Download a file from R2 to local filesystem."""
        os.makedirs(os.path.dirname(local_destination_path), exist_ok=True)
        self.r2_client.download_file(self.bucket_name, cloud_file_path, local_destination_path)
    
    def delete_file(self, cloud_file_path: str) -> bool:
        """Delete a file from R2."""
        try:
            self.r2_client.delete_object(Bucket=self.bucket_name, Key=cloud_file_path)
            return True
        except ClientError:
            return False
    
    def get_file_url(self, cloud_file_path: str, expiry_seconds: Optional[int] = None) -> str:
        """Get a URL for a file in R2, optionally signed."""
        if expiry_seconds:
            return self.r2_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': cloud_file_path},
                ExpiresIn=expiry_seconds
            )
        return self._build_file_url(cloud_file_path)
    
    def file_exists(self, cloud_file_path: str) -> bool:
        """Check if a file exists in R2."""
        try:
            self.r2_client.head_object(Bucket=self.bucket_name, Key=cloud_file_path)
            return True
        except ClientError:
            return False
    
    def _build_file_url(self, cloud_file_path: str) -> str:
        """Build the public URL for a file in R2."""
        if self.public_domain:
            return f"https://{self.public_domain}/{cloud_file_path}"
        return f"https://{self.bucket_name}.{os.getenv('CLOUD_R2_ACCOUNT_ID')}.r2.cloudflarestorage.com/{cloud_file_path}"