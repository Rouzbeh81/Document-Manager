"""
Initialize default settings in the database
"""
from sqlalchemy.orm import Session
from ..models import Settings as SettingsModel
from ..config import Settings as DefaultSettings
from typing import Dict, Any

def initialize_default_settings(db: Session) -> Dict[str, Any]:
    """
    Initialize default settings in the database if they don't exist.
    Returns a dict of settings that were created.
    """
    # Define critical settings that must exist
    critical_settings = {
        'staging_folder': DefaultSettings().staging_folder,
        'data_folder': DefaultSettings().data_folder,
        'storage_folder': DefaultSettings().storage_folder,
        'logs_folder': DefaultSettings().logs_folder,
    }
    
    # Add other important settings
    other_settings = {
        'ai_provider': DefaultSettings().ai_provider,
        'embedding_model': DefaultSettings().embedding_model,
        'chat_model': DefaultSettings().chat_model,
        'analysis_model': DefaultSettings().analysis_model,
        'chroma_host': DefaultSettings().chroma_host,
        'chroma_port': str(DefaultSettings().chroma_port),
        'chroma_collection_name': DefaultSettings().chroma_collection_name,
        'tesseract_path': DefaultSettings().tesseract_path,
        'poppler_path': DefaultSettings().poppler_path,
        'max_file_size': DefaultSettings().max_file_size,
        'allowed_extensions': DefaultSettings().allowed_extensions,
        'log_level': DefaultSettings().log_level,
        'ai_text_limit': str(DefaultSettings().ai_text_limit),
        'ai_context_limit': str(DefaultSettings().ai_context_limit),
    }
    
    all_settings = {**critical_settings, **other_settings}
    created_settings = {}
    
    for key, default_value in all_settings.items():
        # Check if setting exists
        existing = db.query(SettingsModel).filter(SettingsModel.key == key).first()
        
        if not existing:
            # Create new setting with default value
            new_setting = SettingsModel(key=key, value=str(default_value))
            db.add(new_setting)
            created_settings[key] = default_value
    
    # Commit all new settings
    if created_settings:
        db.commit()
    
    return created_settings

def ensure_critical_settings(db: Session) -> bool:
    """
    Ensure all critical settings exist in the database.
    Returns True if all critical settings exist, False otherwise.
    """
    critical_keys = ['staging_folder', 'data_folder', 'storage_folder']
    
    for key in critical_keys:
        setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
        if not setting:
            return False
    
    return True