from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from src.auth.dependencies import (
    AccessTokenBearer,
    RoleChecker,
    get_current_user,
)
from src.db.db import get_session
from src.db.models import User

from .schemas import *
from .service import ReviewsService

reviews_router = APIRouter(tags=["reviews"])
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
review_service = ReviewsService()


@reviews_router.post("/book/{book_uid}", dependencies=[Depends(role_checker)])
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    new_review = await review_service.add_reviews(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )
    return new_review
