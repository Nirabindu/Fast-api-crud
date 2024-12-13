from datetime import datetime

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from .models import Book
from .schemas import (
    BookCreateModel,
    BookUpdateModel,
)


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_id: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_id)
        result = await session.exec(statement)
        book = result.first()
        if book is None:
            return None
        return book

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):
        # book pydantic models to python dict
        book_date_dict = book_data.model_dump()
        new_book = Book(**book_date_dict)

        new_book.published_date = datetime.strptime(
            book_date_dict["published_date"], "%Y-%m-%d"
        )

        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_id: str, book_update: BookUpdateModel, session: AsyncSession
    ):
        book_data_dict = book_update.model_dump()
        get_book_data = await self.get_book(book_id, session)
        if get_book_data is None:
            return None

        for k, v in book_data_dict.items():
            setattr(get_book_data, k, v)
        await session.commit()
        return get_book_data

    async def delete_book(self, book_id: str, session: AsyncSession):
        get_book = await self.get_book(book_id, session)
        if get_book is not None:
            await session.delete(get_book)
            await session.commit()
            return True
        else:
            return None
