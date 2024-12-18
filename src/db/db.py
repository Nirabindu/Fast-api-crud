# creating async Engine

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, text
from sqlmodel.ext.asyncio.session import (
    AsyncSession,
)

from src.config import Config

# sync
# engine = create_engine(url=Config.DATABASE_URL, echo=True)

# async
engine = AsyncEngine(create_engine(url=Config.DATABASE_URL))


# this function used to open and hold up the connection through out the app
# as long as our app is running
async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        print("Something happen with database connection")


async def get_session() -> AsyncSession:

    Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        yield session
