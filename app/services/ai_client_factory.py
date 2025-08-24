"""
AI Client Factory for creating OpenAI or Azure OpenAI clients
"""
from openai import OpenAI, AzureOpenAI
from typing import Union
from loguru import logger
from sqlalchemy.orm import Session
import httpx
from ..config import get_settings

class AIClientFactory:
    """Factory class for creating AI clients based on provider configuration"""
    
    @staticmethod
    def create_client(db: Session = None) -> Union[OpenAI, AzureOpenAI]:
        """Create and return the appropriate AI client based on configuration"""
        settings = get_settings(db)
        
        if settings.ai_provider.lower() == "azure":
            # Azure OpenAI client
            if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
                raise ValueError("Azure OpenAI API key and endpoint must be configured")
                
            logger.info(f"Creating Azure OpenAI client with endpoint: {settings.azure_openai_endpoint}")
            
            # Create HTTP client with timeout
            http_client = httpx.Client(
                timeout=httpx.Timeout(
                    connect=10.0,  # Connection timeout
                    read=settings.ai_request_timeout,  # Read timeout
                    write=10.0,  # Write timeout
                    pool=5.0  # Pool timeout
                ),
                limits=httpx.Limits(
                    max_connections=20,
                    max_keepalive_connections=5
                )
            )
            
            return AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
                http_client=http_client
            )
        else:
            # Standard OpenAI client
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key must be configured")
                
            logger.info("Creating standard OpenAI client")
            
            # Create HTTP client with timeout
            http_client = httpx.Client(
                timeout=httpx.Timeout(
                    connect=10.0,  # Connection timeout
                    read=settings.ai_request_timeout,  # Read timeout
                    write=10.0,  # Write timeout
                    pool=5.0  # Pool timeout
                ),
                limits=httpx.Limits(
                    max_connections=20,
                    max_keepalive_connections=5
                )
            )
            
            return OpenAI(
                api_key=settings.openai_api_key,
                http_client=http_client
            )
    
    @staticmethod
    def get_chat_model(settings) -> str:
        """Get the appropriate chat model name based on provider"""
        if settings.ai_provider.lower() == "azure":
            return settings.azure_openai_chat_deployment or settings.chat_model
        else:
            return settings.chat_model
    
    @staticmethod
    def get_embeddings_model(settings) -> str:
        """Get the appropriate embeddings model name based on provider"""
        if settings.ai_provider.lower() == "azure":
            return settings.azure_openai_embeddings_deployment or settings.embedding_model
        else:
            return settings.embedding_model
    
    @staticmethod
    def validate_configuration(settings) -> dict:
        """Validate the AI configuration and return status"""
        errors = []
        warnings = []
        
        if settings.ai_provider.lower() == "azure":
            if not settings.azure_openai_api_key:
                errors.append("Azure OpenAI API key is missing")
            if not settings.azure_openai_endpoint:
                errors.append("Azure OpenAI endpoint is missing")
            if not settings.azure_openai_chat_deployment:
                warnings.append("Azure OpenAI chat deployment name is missing")
            if not settings.azure_openai_embeddings_deployment:
                warnings.append("Azure OpenAI embeddings deployment name is missing")
        else:
            if not settings.openai_api_key:
                errors.append("OpenAI API key is missing")
        
        return {
            "provider": settings.ai_provider,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }