from pydantic import EmailStr
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from .models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash


class UserauthService:
    async def get_user_by_mail(
        self, email: EmailStr, session: AsyncSession
    ) -> User | None:
        """This method used to get user by email

        Args:
            email (EmailStr): user-provided email
            session (AsyncSession): Database Session

        Returns:
            user | None: returns user if present i.e return None
        """
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exist(self, email: EmailStr, session: AsyncSession) -> bool:
        """This methods used to verify is user exist in dataBase or not

        Args:
            email (EmailStr): user-provided Email.
            session (AsyncSession): Database Session.

        Returns:
            _type_: bool
        """
        user = await self.get_user_by_mail(email, session)
        return user is not None

    async def create_user(
        self, user_data: UserCreateModel, session: AsyncSession
    ) -> User:
        """This Method used to create user into database

        Args:
            user_data (UserCreateModel): user-provided data
            session (AsyncSession): database session

        Returns:
            User: return newly created User
        """

        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        return new_user
