from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from src.app1.service import BookService
from src.auth.dependencies import (
    AccessTokenBearer,
)
from src.db.db import get_session

from .schemas import *

app1_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


# all the views related app1 will be write here
@app1_router.get("/", response_model=list[Book])
async def get_details(
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
) -> list[Book]:
    print("getting user details", user_details)
    book = await book_service.get_all_books(session)
    return book


@app1_router.get("/{book_id}", response_model=Book)
async def get_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
):
    get_book = await book_service.get_book(book_id, session)
    if get_book:
        return get_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details="Book Not Found"
        )


@app1_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
) -> dict:
    book = await book_service.create_book(book_data, session)
    return book


@app1_router.patch("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book_(
    book_id: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
):
    book_update = await book_service.update_book(book_id, book_update_data, session)
    if book_update:
        return book_update
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details="Book Not Found"
        )


@app1_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_(book_id: str, session: AsyncSession = Depends(get_session)):
    delete_book = await book_service.delete_book(book_id, session)
    if delete_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
        )
    else:
        return None
