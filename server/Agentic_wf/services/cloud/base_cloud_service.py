"""
Base Cloud Service Abstract Class
Defines the interface for all cloud storage providers
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, BinaryIO


class BaseCloudService(ABC):
    """Abstract base class that defines the interface for all cloud storage services."""
    
    @abstractmethod
    def upload_file(self, file_path: str, destination_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to cloud storage.
        
        Args:
            file_path: Local path to the file to upload
            destination_path: Optional path in the cloud where the file should be stored
            
        Returns:
            Dictionary containing upload details including URL and file identifier
        """
        pass
    
    @abstractmethod
    def upload_file_object(self, file_object: BinaryIO, destination_path: str) -> Dict[str, Any]:
        """
        Upload a file-like object to cloud storage.
        
        Args:
            file_object: Binary file object to upload
            destination_path: Path in the cloud where the file should be stored
            
        Returns:
            Dictionary containing upload details including URL and file identifier
        """
        pass
    
    @abstractmethod
    def download_file(self, cloud_file_path: str, local_destination_path: str) -> None:
        """
        Download a file from cloud storage to local filesystem.
        
        Args:
            cloud_file_path: Path/identifier of the file in cloud storage
            local_destination_path: Local path where the file should be saved
        """
        pass
    
    @abstractmethod
    def delete_file(self, cloud_file_path: str) -> bool:
        """
        Delete a file from cloud storage.
        
        Args:
            cloud_file_path: Path/identifier of the file in cloud storage
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_file_url(self, cloud_file_path: str, expiry_seconds: Optional[int] = None) -> str:
        """
        Get a URL for accessing a file from cloud storage.
        
        Args:
            cloud_file_path: Path/identifier of the file in cloud storage
            expiry_seconds: Optional number of seconds until the URL expires (for signed URLs)
            
        Returns:
            URL string for accessing the file
        """
        pass
    
    @abstractmethod
    def file_exists(self, cloud_file_path: str) -> bool:
        """
        Check if a file exists in cloud storage.
        
        Args:
            cloud_file_path: Path/identifier of the file in cloud storage
            
        Returns:
            True if the file exists, False otherwise
        """
        pass