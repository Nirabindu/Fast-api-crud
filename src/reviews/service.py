from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from src.app1.service import BookService
from src.auth.service import UserauthService
from src.db.models import Review

from .schemas import *

book_service = BookService()
auth_service = UserauthService()


class ReviewsService:

    async def add_reviews(
        self,
        user_email: str,
        book_uid: uuid.UUID,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ) -> Review:
        try:
            book = await book_service.get_book(book_uid, session)
            user = await auth_service.get_user_by_mail(user_email, session)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
                )

            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)
            new_review.user_uid = user.uid
            new_review.book_uid = book.uid
            session.add(new_review)
            await session.commit()
            return new_review

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Some things went wrong",
            )
