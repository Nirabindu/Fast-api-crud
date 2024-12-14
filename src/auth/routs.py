from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from src.db.db import get_session

from .schemas import (
    UserCreateModel,
    UserResponseModel,
)
from .service import UserauthService

auth_router = APIRouter(tags=["Auth"])
auth_service = UserauthService()


@auth_router.post("/signup", response_model=UserResponseModel)
async def user_accounts(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    user = await auth_service.user_exist(user_data.email, session)
    if user is True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User email already in used"
        )
    else:
        new_user = await auth_service.create_user(user_data, session)
    return new_user
