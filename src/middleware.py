import logging
import time

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import (
    TrustedHostMiddleware,
)
from fastapi.requests import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        """
        request is here incoming request pass to middle ware before the routers
        next: i.e another middleware or path handler or routers
        """
        start_time = time.time()
        # print("before", start_time)
        response = await call_next(request)
        processing_time = time.time() - start_time
        message = f"{request.method} - {request.url.path} -{response.status_code} Before_process={start_time} - After_process={processing_time}"
        # print("process_time", processing_time)
        print(message)
        return response

    # we can not raise httpException in middleware
    # its an example
    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     if not "authorization" in request.headers:
    #         # means user not authenticated
    #         return JSONResponse(
    #             content={
    #                 "message": "Not Authenticated",
    #                 "resolution": "Please Login again ",
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #         )
    #     response = await call_next(request)
    #     return response
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
