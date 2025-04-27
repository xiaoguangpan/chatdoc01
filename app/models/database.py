from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./db/app_data.db")
SQLITE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLITE_URL)
Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=True)
    creation_time = Column(DateTime, default=datetime.utcnow)
    
    documents = relationship("Document", back_populates="project")

class Document(Base):
    __tablename__ = "documents"
    
    doc_base_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    original_filename = Column(String, nullable=False)
    creation_time = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    version_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_base_id = Column(Integer, ForeignKey("documents.doc_base_id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    stored_filename = Column(String, nullable=False)
    stored_filepath = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="processing")
    error_message = Column(String, nullable=True)
    is_latest = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    document = relationship("Document", back_populates="versions")
    chat_sessions = relationship("ChatSession", back_populates="document_version")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("document_versions.version_id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    last_update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    document_version = relationship("DocumentVersion", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="chat_session")

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.session_id"), nullable=False)
    sender = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    retrieved_chunk_html_ids = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    chat_session = relationship("ChatSession", back_populates="messages")

class Setting(Base):
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

def init_db():
    Base.metadata.create_all(engine) 