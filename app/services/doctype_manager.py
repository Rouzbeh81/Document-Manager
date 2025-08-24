from sqlalchemy.orm import Session
from ..models import DocType
from loguru import logger

def ensure_default_document_types(db: Session):
    """Ensure default document types exist in database"""
    
    default_types = [
        "rechnung",
        "anschreiben", 
        "angebot",
        "anmeldung",
        "bescheinigung",
        "entgeltabrechnung",
        "kündigung",
        "vertrag",
        "bericht",
        "quittung",
        "mahnung",
        "gutschrift",
        "bestellung",
        "lieferschein",
        "protokoll",
        "sonstiges"
    ]
    
    try:
        # Check which types already exist
        existing_types = db.query(DocType).all()
        existing_names = {dt.name.lower() for dt in existing_types}
        
        # Add missing default types
        for doc_type in default_types:
            if doc_type.lower() not in existing_names:
                new_type = DocType(
                    name=doc_type,
                    description=f"Standard document type: {doc_type}"
                )
                db.add(new_type)
                logger.info(f"Added default document type: {doc_type}")
        
        db.commit()
        logger.info("Default document types ensured in database")
        
    except Exception as e:
        logger.error(f"Failed to ensure default document types: {e}")
        db.rollback()
        raise

def add_document_type_if_not_exists(db: Session, type_name: str, description: str = None) -> DocType:
    """Add a new document type if it doesn't exist"""
    
    try:
        # Check if type already exists (case insensitive)
        existing_type = db.query(DocType).filter(
            DocType.name.ilike(type_name)
        ).first()
        
        if existing_type:
            return existing_type
        
        # Create new type
        new_type = DocType(
            name=type_name.lower(),
            description=description or f"Document type: {type_name}"
        )
        db.add(new_type)
        db.commit()
        
        logger.info(f"Added new document type: {type_name}")
        return new_type
        
    except Exception as e:
        logger.error(f"Failed to add document type {type_name}: {e}")
        db.rollback()
        raise