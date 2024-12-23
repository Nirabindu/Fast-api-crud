# import uuid
# from datetime import date, datetime

# import sqlalchemy.dialects.postgresql as pg
# from sqlmodel import (
#     Column,
#     Field,
#     Relationship,
#     SQLModel,
# )

# from src.app1.models import Book


# class User(SQLModel, table=True):

#     __tablename__ = "users"
#     uid: uuid.UUID = Field(
#         sa_column=Column(
#             pg.UUID, nullable=False, unique=True, primary_key=True, default=uuid.uuid4
#         )
#     )
#     username: str
#     email: str
#     password_hash: str = Field(exclude=True)
#     first_name: str
#     last_name: str
#     is_verified: bool = Field(default=False)
#     # needs to use cause all of my previous user fields should be populated using 'user'
#     role: str = Field(
#         sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
#     )
#     # this not gonna working given Integrity errors
#     # role: str = Field(default="user")
#     # is_active: bool = Field(default=False)
#     created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
#     updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
#     # needs to check ones
#     # select in loading loads all relates field at onece not calling where is time i.e use join
#     books: list[Book] | None = Relationship(
#         back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
#     )

#     def __repr__(self):
#         return f"<User {self.username}>"


# """
# sql model loads books here use lazy loading but it can problematic in asyn db api

# """
