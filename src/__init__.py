# instead of doing Entry point main we can do by main project  inside __init__
from contextlib import asynccontextmanager

from debug_toolbar.middleware import (
    DebugToolbarMiddleware,
)
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.app1.routs import app1_router
from src.auth.routes import auth_router
from src.reviews.routes import reviews_router

from .db.db import init_db
from .errors import register_all_errors
from .middleware import register_middleware


# starting and ending life span
@asynccontextmanager
# This decorator creates an asynchronous context manager.
# It allows you to define logic that runs before and after the yield statement.
async def life_span(app: FastAPI):
    """Here i wants do the logic like one end will execute while server has started one will execute while server has ended"""
    # life_span event not needed now we are gonna using alembic Instead
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
    debug=False,
    # lifespan=life_span,
)

register_all_errors(app)
register_middleware(app)
app.add_middleware(
    DebugToolbarMiddleware,
    # panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
)
# registering router
app.include_router(app1_router, prefix=f"/api/{version}/app1")
app.include_router(auth_router, prefix=f"/api/{version}/user_auth")
app.include_router(reviews_router, prefix=f"/api/{version}/reviews")
