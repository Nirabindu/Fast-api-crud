from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_task import send_mail
from src.config import Config
from src.db.db import get_session
from src.db.redis import add_jit_to_blacklist
from src.errors import UserExistException
from src.mail import create_message, mail

from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from .schemas import (
    EmailModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserCreateModel,
    UserLoginModel,
    UserResponseModel,
)
from .service import UserauthService
from .utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    generate_password_hash,
    verify_password,
)

auth_router = APIRouter(tags=["Auth"])
auth_service = UserauthService()
role_checker = RoleChecker(["admin", "user"])

# hours
REFRESH_TOKEN_EXPIRE = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.email_addresses
    html = "<h1>welcome to the app</h1>"
    subject = "welcome to our app"
    # calling celery task
    send_mail.delay(emails, subject, html)
    message = create_message(recipients=emails, subject="welcome subjects", body=html)

    await mail.send_message(message)
    return {"message": "email send Successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def user_accounts(
    user_data: UserCreateModel,
    bg_task: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
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
        raise UserExistException()

    new_user = await auth_service.create_user(user_data, session)
    token = create_url_safe_token({"email": user_data.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html_msg = f"""
    <h1>Verify Email</h1>
    <p>Please click this <a href=f"{link}">Link</a> to verify it's you</p>

    """
    message = create_message(
        recipients=[user_data.email], subject="Verify your Email", body=html_msg
    )
    # used here back ground task
    # await mail.send_message(message)
    bg_task.add_task(mail.send_message, message)
    return {
        "message": "Account Created! check your emails to verify it's you ",
        "user": new_user,
    }


@auth_router.get("/verify/email-token/{token}")
async def verify_user_email(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await auth_service.get_user_by_mail(user_email, session)
        if not user:
            # rais usernot found
            pass
        await auth_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account Verified Successfully"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"message": "Error occurs during verification "},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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
                user_data={"email": user.email, "uid": str(user.uid), "role": user.role}
            )
            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "uid": str(user.uid),
                    "role": user.role,
                },
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
    # fromtimestamp(exp_time) will convert timestamp to actual datetime 1638364800 ->  2021-12-04 00:00:00
    if datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_access_token(token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expire Token"
    )


@auth_router.get("/me", response_model=UserResponseModel)
async def get_current_user_(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jit_to_blacklist(jti)
    return JSONResponse(
        content={"message": "Logout Successfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-request")
async def password_reset(email_data: PasswordResetRequestModel):
    email = email_data["email"]
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    send_mail.delay([email], subject, html_message)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    password: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = password.new_password
    confirm_new_password = password.confirm_new_password

    if new_password != confirm_new_password:
        raise HTTPException(
            detail="Both Password Should Be Matched!!",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await auth_service.get_user_by_mail(user_email)

        if not user:
            # raise HTTPException
            pass
        password_hash = generate_password_hash(new_password)
        await auth_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
