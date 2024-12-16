from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from src.db.db import get_session

from .dependencies import RefreshTokenBearer
from .schemas import (
    UserCreateModel,
    UserLoginModel,
    UserResponseModel,
)
from .service import UserauthService
from .utils import (
    create_access_token,
    verify_password,
)

auth_router = APIRouter(tags=["Auth"])
auth_service = UserauthService()
REFRESH_TOKEN_EXPIRE = True


@auth_router.post(
    "/signup", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED
)
async def user_accounts(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
) -> UserResponseModel:
    """This Function Used to register a user

    Args:
        user_data(UserCreateModel): user provided information including name, email, password and etc
        session (AsyncSession): database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: Raise an error only if user already exist in DataBase

    Returns:
        UserResponseModel: return specific fields[username,email,first_name, last_name] from User Model
    """

    user = await auth_service.user_exist(user_data.email, session)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User email already in used"
        )

    new_user = await auth_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    """This function used to Authenticate user with email and password

    Args:
        login_data (UserLoginModel): user-provided data including email and password
        session (AsyncSession): database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: Raise if Invalid Email or Pass word Provided

    Returns:
       JsonResponse: returning user Information including email, uid, name and access and refresh Token
    """
    email = login_data.email
    password = login_data.password
    # checking for user
    user = await auth_service.get_user_by_mail(email, session)
    if user:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "uid": str(user.uid)}
            )
            refresh_token = create_access_token(
                user_data={"email": user.email, "uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRE),
            )
            return JSONResponse(
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "uid": str(user.uid),
                        "email": user.email,
                        "username": user.username,
                    },
                }
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid email or Password",
    )


@auth_router.get("/refresh_token")
# needs to pass access token at header
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_time = token_details["exp"]
    if datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_access_token(token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expire Token"
    )
