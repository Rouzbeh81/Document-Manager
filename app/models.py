from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from passlib.context import CryptContext

from .database import Base

# Association table for many-to-many relationship between documents and tags
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', String, ForeignKey('documents.id'), primary_key=True),
    Column('tag_id', String, ForeignKey('tags.id'), primary_key=True)
)

# Association table for document relationships (main doc to sub docs)
document_relations = Table(
    'document_relations',
    Base.metadata,
    Column('parent_document_id', String, ForeignKey('documents.id'), primary_key=True),
    Column('child_document_id', String, ForeignKey('documents.id'), primary_key=True)
)

class Correspondent(Base):
    __tablename__ = "correspondents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="correspondent")

class DocType(Base):
    __tablename__ = "doctypes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="doctype")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    color = Column(String, nullable=True)  # For UI representation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", secondary=document_tags, back_populates="tags")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_hash = Column(String, unique=True, nullable=False, index=True)
    file_path = Column(String, nullable=False)  # Path in storage
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Document metadata
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)  # OCR result
    document_date = Column(DateTime, nullable=True)  # Date from document content
    
    # Extended fields as requested
    is_tax_relevant = Column(Boolean, default=False, nullable=False)
    reminder_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)  # User notes for the document
    
    # View tracking
    view_count = Column(Integer, default=0, nullable=False)
    last_viewed = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    correspondent_id = Column(String, ForeignKey("correspondents.id"), nullable=True)
    doctype_id = Column(String, ForeignKey("doctypes.id"), nullable=True)
    
    # System metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing status
    ocr_status = Column(String, default="pending")  # pending, processing, completed, failed
    ai_status = Column(String, default="pending")   # pending, processing, completed, failed
    vector_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Approval status
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    correspondent = relationship("Correspondent", back_populates="documents")
    doctype = relationship("DocType", back_populates="documents")
    tags = relationship("Tag", secondary=document_tags, back_populates="documents")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    
    # Self-referential relationship for main/sub documents
    children = relationship(
        "Document",
        secondary=document_relations,
        primaryjoin=id == document_relations.c.parent_document_id,
        secondaryjoin=id == document_relations.c.child_document_id,
        backref="parents"
    )

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    operation = Column(String, nullable=False)  # ocr, ai_extraction, etc.
    status = Column(String, nullable=False)     # success, error, warning
    message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_admin:
            return True
        
        for role in self.roles:
            if role.permissions:
                import json
                try:
                    perms = json.loads(role.permissions)
                    if permission in perms:
                        return True
                except (json.JSONDecodeError, TypeError):
                    continue
        return False

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # login, logout, create_document, etc.
    resource_type = Column(String, nullable=True)  # document, user, settings, etc.
    resource_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with additional details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
