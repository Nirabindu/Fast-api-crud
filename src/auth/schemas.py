from pydantic import BaseModel, EmailStr, Field


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
