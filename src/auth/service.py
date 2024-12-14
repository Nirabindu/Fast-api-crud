from pydantic import EmailStr
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from .models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash


class UserauthService:
    async def get_user_by_mail(self, email: EmailStr, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        if user is not None:
            return user
        else:
            return None

    async def user_exist(self, email: EmailStr, session: AsyncSession):
        user = await self.get_user_by_mail(email, session)
        return user is not None

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):

        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()
        return new_user
