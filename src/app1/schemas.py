import uuid
from datetime import date, datetime

from pydantic import BaseModel

from src.reviews.schemas import ReviewModel

# from src.auth.schemas import UserResponseModel


class Book(BaseModel):
    """This class is example of Model Schema."""

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookCreateModel(BaseModel):

    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    """something."""

    title: str
    author: str
    publisher: str
    page_count: int
    language: str


# to avoid circular Import needs to use inside ""
# class BookResponseModel(Book):
#     user: "UserResponseModel"


class BookDetailsModel(Book):
    reviews: list[ReviewModel] = []
