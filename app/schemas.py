from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class ModerationRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text content to moderate")

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty or whitespace only")
        return value


class ModerationResponse(BaseModel):
    id: int
    text: str
    is_flagged: bool
    category: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True