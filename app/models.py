from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class ChatHistory(Base):
    """
    SQLAlchemy model representing a saved chat generation record.
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

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
