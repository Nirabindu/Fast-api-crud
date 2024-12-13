# instead of doing Entry point main we can do by main project  inside __init__

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app1.routes import app1_router

from .db.db import init_db


# starting and ending life span
@asynccontextmanager
# This decorator creates an asynchronous context manager.
# It allows you to define logic that runs before and after the yield statement.
async def life_span(app: FastAPI):
    """Here i wants do the logic like one end will execute while server has started one will execute while server has ended"""
    print(f"Server is Starting")
    # calling init_db for connection
    await init_db()
    # holding the db connection open db connection for entire app at onces
    yield
    print(f"Server has been Stop")


version = "v1"
app = FastAPI(
    title="FastApi app",
    description="Learning Fast Api",
    version=version,
    lifespan=life_span,
)

# registering router
app.include_router(app1_router, prefix=f"/api/{version}/app1")
