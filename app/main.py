import logging

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.base import api_router
from app.database import PasswordDB

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:3000",
    "https://localhost:3000",
]


def build_app() -> FastAPI:
    application = FastAPI(title="Password Manager", debug=True, version="1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application


app = build_app()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.on_event("startup")
async def startup() -> None:
    app.state.DB = PasswordDB()
    await app.state.DB.initiate_db()

# TODO: Add shutdown event to close db connection
