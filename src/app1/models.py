import uuid
from datetime import date, datetime

# mports the PostgreSQL dialect for SQLAlchemy. This dialect provides PostgreSQL-specific functionality and types that are not part of the standard SQLAlchemy library.
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, SQLModel


class Book(SQLModel, table=True):

    __tablename__ = "books"

    # Column is used to define a database column in SQLAlchemy. This is where you define the database schema for the uid field. as we are using sa_columns here so Column needs to use if we use SqlAlchamy columns instead SQLModel Directly
    # you use Field to specify additional arguments for database columns or validation in models.
    # sa_column=Column(...): Allows the SQLAlchemy column to be associated with a Pydantic field.
    # so sa_columns convert sqlalchemy type to pydantic type
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, unique=True, primary_key=True, default=uuid.uuid4
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Book {self.title}>"
