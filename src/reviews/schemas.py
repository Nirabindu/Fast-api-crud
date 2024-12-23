import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    uid: uuid.UUID
    book_uid: uuid.UUID
    user_uid: uuid.UUID
    review_text: str
    ratings: int = Field(ge=0, le=5)
    created_at: datetime
    updated_at: datetime


class ReviewCreateModel(BaseModel):
    review_text: str
    ratings: int = Field(ge=0, le=5)
