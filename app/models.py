from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ChatHistory(Base):
    """
    Legacy model (preserved for backward compatibility).
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), index=True, nullable=False)
    content_type = Column(String(50), nullable=False)
    user_prompt = Column(Text, nullable=False)
    generated_response = Column(Text, nullable=False)
    tone = Column(String(50), nullable=False)
    audience = Column(String(50), nullable=False)
    length = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=5, minutes=30), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content_type": self.content_type,
            "user_prompt": self.user_prompt,
            "generated_response": self.generated_response,
            "tone": self.tone,
            "audience": self.audience,
            "length": self.length,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatSession(Base):
    """
    Represents a full conversation session.
    """
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=5, minutes=30), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=5, minutes=30), onupdate=lambda: datetime.now(timezone.utc) + timedelta(hours=5, minutes=30), nullable=False)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.id")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ChatMessage(Base):
    """
    Represents a single message in a session.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Metadata used for generation settings
    content_type = Column(String(50), nullable=True)
    tone = Column(String(50), nullable=True)
    audience = Column(String(50), nullable=True)
    length = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=5, minutes=30), nullable=False)

    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "content_type": self.content_type,
            "tone": self.tone,
            "audience": self.audience,
            "length": self.length,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
