from typing import Any

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.db import get_session
from src.db.models import User
from src.db.redis import token_in_blacklist
from src.errors import (
    AccessTokenRequireException,
    InsufficientPermissionException,
    InvalidTokenException,
    RefreshTokenRequireException,
    RevokedTokenException,
    UserExistException,
)

from .service import UserauthService
from .utils import decode_token

user_service = UserauthService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        # this line will give Bearer as key and token
        creds = await super().__call__(request)

        # to fetch only tokens
        token = creds.credentials
        # getting information from token by decoded them or return None if not
        token_data = decode_token(token)
        # so token valid return True(if) and not convert it to False and if will not execute
        if not self.token_valid(token):

            raise InvalidTokenException()

            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN,
            #     detail={
            #         "error": "This Token is Invalid or Expire",
            #         "resolution": "Please Login Again",
            #     },
            # )

        if await token_in_blacklist(token_data["jti"]):

            raise RevokedTokenException()
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN,
            #     detail={
            #         "error": "This Token is Invalid or revoked",
            #         "resolution": "Please Login Again",
            #     },
            # )

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:

        token_data = decode_token(token)
        # if token_data:
        #     return True
        # return False
        return token_data is not None

    # def verify_token_data(self, token_data):
    #     raise NotImplementedError("Please override this methods")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        """
        if refresh token provided as access token it also verified but that not the access token
        so token_data(get_user_information) and for refresh token it will became true and it will not work

        """
        if token_data and token_data["refresh"]:
            raise AccessTokenRequireException()
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN,
            #     detail="Please Provide valid access Token",
            # )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN,
            #     detail="Please Provide valid refresh Token",
            # )
            raise RefreshTokenRequireException()


# current logged in user
# dependency only work with route
async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer()),
):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_mail(user_email, session)
    return user


class RoleChecker:

    def __init__(self, roles: list[str]) -> None:
        self.roles = roles

    # used class as function invoke class() instead objects
    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:

        if not current_user.is_verified:
            # raise an Exception
            pass
        if current_user.role in self.roles:
            return True
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail={"error": "Operation Not Permitted"},
        # )
        raise InsufficientPermissionException()
