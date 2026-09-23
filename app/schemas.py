from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ContentType(str, Enum):
    EMAIL = "EMAIL"
    REPORT = "REPORT"
    TECHNICAL_EXPLANATION = "TECHNICAL EXPLANATION"
    GENERAL_CONTENT = "GENERAL CONTENT"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            val_upper = value.strip().upper()
            for member in cls:
                if member.value.upper() == val_upper:
                    return member
        return None


class ToneType(str, Enum):
    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    ACADEMIC = "Academic"
    SIMPLE = "Simple"
    FORMAL = "Formal"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            val_lower = value.strip().lower()
            for member in cls:
                if member.value.lower() == val_lower:
                    return member
        return None


class AudienceType(str, Enum):
    BEGINNER = "Beginner"
    STUDENT = "Student"
    PROFESSIONAL = "Professional"
    TECHNICAL_EXPERT = "Technical Expert"
    GENERAL_AUDIENCE = "General Audience"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            val_lower = value.strip().lower()
            for member in cls:
                if member.value.lower() == val_lower:
                    return member
        return None


class LengthType(str, Enum):
    SHORT = "Short"
    MEDIUM = "Medium"
    DETAILED = "Detailed"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            val_lower = value.strip().lower()
            for member in cls:
                if member.value.lower() == val_lower:
                    return member
        return None


class GenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, description="The user's generation instruction/query")
    content_type: ContentType = Field(default=ContentType.GENERAL_CONTENT, description="Type of content to generate")
    tone: ToneType = Field(default=ToneType.PROFESSIONAL, description="Desired communication tone")
    audience: AudienceType = Field(default=AudienceType.GENERAL_AUDIENCE, description="Target reading audience")
    length: LengthType = Field(default=LengthType.MEDIUM, description="Desired output length")
    session_id: Optional[str] = Field(default="default-session", description="Unique session identifier")

    @field_validator("user_prompt")
    @classmethod
    def validate_user_prompt(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Prompt cannot be empty or contain only whitespace.")
        return stripped


class RegenerateRequest(GenerateRequest):
    previous_response: Optional[str] = Field(default=None, description="Previous output to regenerate from if applicable")


class TransformRequest(BaseModel):
    previous_response: str = Field(..., min_length=1, description="The previous response to transform")
    user_prompt: Optional[str] = Field(default="", description="Original user prompt")
    content_type: ContentType = Field(default=ContentType.GENERAL_CONTENT)
    tone: ToneType = Field(default=ToneType.PROFESSIONAL)
    audience: AudienceType = Field(default=AudienceType.GENERAL_AUDIENCE)
    length: LengthType = Field(default=LengthType.MEDIUM)
    session_id: Optional[str] = Field(default="default-session")

    @field_validator("previous_response")
    @classmethod
    def validate_previous_response(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Previous response to transform cannot be empty.")
        return stripped


class GenerateResponse(BaseModel):
    id: Optional[int] = None
    session_id: str
    content_type: str
    user_prompt: str
    generated_response: str
    tone: str
    audience: str
    length: str
    created_at: str
    model: str


class HistoryItemResponse(BaseModel):
    id: int
    session_id: str
    content_type: str
    user_prompt: str
    generated_response: str
    tone: str
    audience: str
    length: str
    created_at: str


class HistoryListResponse(BaseModel):
    total: int
    items: List[HistoryItemResponse]


class GroqStatusResponse(BaseModel):
    provider: str
    configured: bool
    model: str
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
