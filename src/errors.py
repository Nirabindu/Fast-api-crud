# won customize error class

from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class BaseException(Exception):
    pass


class InvalidTokenException(BaseException):
    pass


class RevokedTokenException(BaseException):
    pass


class AccessTokenRequireException(BaseException):
    pass


class RefreshTokenRequireException(BaseException):
    pass


class UserExistException(BaseException):
    pass


class InsufficientPermissionException(BaseException):
    pass


class BookNotFoundException(BaseException):
    pass


class AccountNotVerified(BaseException):
    """Account not yet verified"""

    pass


def create_exception_handler(
    status_code: int, initial_details: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BaseException):
        return JSONResponse(content=initial_details, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    # define all the errors

    app.add_exception_handler(
        UserExistException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "User with email already Exists",
                "error_code": "user exists",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_details={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went Wrong",
                "error_code": "Server Error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exe):
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
