from pydantic import BaseModel, EmailStr, Field

from src.app1.schemas import Book, BookDetailsModel


class UserCreateModel(BaseModel):
    username: str = Field(max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(max_length=10)
    last_name: str = Field(max_length=5)


class UserResponseModel(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    books: list[BookDetailsModel] = []
    # reviews: list = [ReviewModel]


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class EmailModel(BaseModel):
    email_addresses: list[EmailStr]


class PasswordResetRequestModel(BaseModel):
    email: EmailStr


class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)
