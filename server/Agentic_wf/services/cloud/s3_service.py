"""
AWS S3 Service Implementation
Provides cloud storage operations using Amazon S3
"""
import os
from typing import Any, Dict, Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError

from Agentic_wf.services.cloud.base_cloud_service import BaseCloudService
from Agentic_wf.config import get_cloud_settings


class S3Service(BaseCloudService):
    """AWS S3 implementation of the base cloud service."""
    
    def __init__(self):
        """Initialize S3 client from settings."""
        settings = get_cloud_settings()
        if not all([settings.s3_api_key, settings.s3_api_secret, settings.s3_cloud_name]):
            raise ValueError("S3 configuration is incomplete. Please check your environment variables.")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.s3_api_key,
            aws_secret_access_key=settings.s3_api_secret
        )
        self.bucket_name = settings.s3_cloud_name
    
    def upload_file(self, file_path: str, destination_path: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to S3."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        s3_path = destination_path or os.path.basename(file_path)
        self.s3_client.upload_file(file_path, self.bucket_name, s3_path)
        
        url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_path}"
        return {
            'url': url,
            'key': s3_path,
            'bucket': self.bucket_name,
            'provider': 's3'
        }
    
    def upload_file_object(self, file_object: BinaryIO, destination_path: str) -> Dict[str, Any]:
        """Upload a file-like object to S3."""
        self.s3_client.upload_fileobj(file_object, self.bucket_name, destination_path)
        
        url = f"https://{self.bucket_name}.s3.amazonaws.com/{destination_path}"
        return {
            'url': url,
            'key': destination_path,
            'bucket': self.bucket_name,
            'provider': 's3'
        }
    
    def download_file(self, cloud_file_path: str, local_destination_path: str) -> None:
        """Download a file from S3 to local filesystem."""
        os.makedirs(os.path.dirname(local_destination_path), exist_ok=True)
        self.s3_client.download_file(self.bucket_name, cloud_file_path, local_destination_path)
    
    def delete_file(self, cloud_file_path: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=cloud_file_path)
            return True
        except ClientError:
            return False
    
    def get_file_url(self, cloud_file_path: str, expiry_seconds: Optional[int] = None) -> str:
        """Get a URL for a file in S3, optionally signed."""
        if expiry_seconds:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': cloud_file_path},
                ExpiresIn=expiry_seconds
            )
        return f"https://{self.bucket_name}.s3.amazonaws.com/{cloud_file_path}"
    
    def file_exists(self, cloud_file_path: str) -> bool:
        """Check if a file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=cloud_file_path)
            return True
        except ClientError:
            return False