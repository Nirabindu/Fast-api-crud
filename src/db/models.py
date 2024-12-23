import uuid
from datetime import date, datetime
from typing import Optional

# imports the PostgreSQL dialect for SQLAlchemy. This dialect provides PostgreSQL-specific functionality and types that are not part of the standard SQLAlchemy library.
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import (
    TEXT,
    Column,
    Field,
    Relationship,
    SQLModel,
)


class User(SQLModel, table=True):

    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, nullable=False, unique=True, primary_key=True, default=uuid.uuid4
        )
    )
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    is_verified: bool = Field(default=False)
    # needs to use cause all of my previous user fields should be populated using 'user'
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    # this not gonna working given Integrity errors
    # role: str = Field(default="user")
    # is_active: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # needs to check ones
    # select in loading loads all relates field at onece not calling where is time i.e use join
    books: list["Book"] | None = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: list["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<User {self.username}>"


"""
sql model loads books here use lazy loading but it can problematic in asyn db api

"""


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
    user_uid: uuid.UUID | None = Field(
        default=None, foreign_key="users.uid", ondelete=""
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # avoiding circular Import thats the reason not Importing User from models
    # needs to restructure
    user: User | None = Relationship(back_populates="books")
    reviews: list["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<Book {self.title}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            unique=True,
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    book_uid: uuid.UUID = Field(foreign_key="books.uid")
    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    review_text: str
    ratings: int = Field(le=5, ge=0)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: User | None = Relationship(back_populates="reviews")
    book: Book | None = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for {self.book_uid}> by user {self.user_uid}>"
