"""
Cloud Service Factory
Creates and returns the appropriate cloud service instance based on configuration
"""
from typing import Dict, Type
from Agentic_wf.config import get_cloud_settings
from Agentic_wf.services.cloud.base_cloud_service import BaseCloudService
from Agentic_wf.services.cloud.cloudinary_service import CloudinaryService
from Agentic_wf.services.cloud.s3_service import S3Service
from Agentic_wf.services.cloud.r2_service import R2Service


# Registry of available cloud services
_cloud_service_registry: Dict[str, Type[BaseCloudService]] = {
    'cloudinary': CloudinaryService,
    's3': S3Service,
    'r2': R2Service
}

# Singleton instance of the current cloud service
_cloud_service_instance: BaseCloudService = None


def get_cloud_service() -> BaseCloudService:
    """
    Get the configured cloud service instance.
    Creates the instance if it doesn't exist yet (singleton pattern).
    
    Returns:
        An instance of BaseCloudService matching the configured provider
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    global _cloud_service_instance
    
    if _cloud_service_instance is None:
        settings = get_cloud_settings()
        provider = settings.provider
        
        if provider not in _cloud_service_registry:
            raise ValueError(f"Unsupported cloud provider: {provider}. Available providers: {list(_cloud_service_registry.keys())}")
        
        service_class = _cloud_service_registry[provider]
        _cloud_service_instance = service_class()
    
    return _cloud_service_instance


def register_cloud_service(provider_name: str, service_class: Type[BaseCloudService]) -> None:
    """
    Register a new cloud service provider.
    This allows extending the factory with custom cloud providers.
    
    Args:
        provider_name: Name of the cloud provider
        service_class: Class implementing the BaseCloudService interface
    """
    _cloud_service_registry[provider_name] = service_class
    # Reset instance to allow picking up new service
    global _cloud_service_instance
    _cloud_service_instance = None