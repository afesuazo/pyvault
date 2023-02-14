from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes.base import api_router
from app.database import PasswordDB


def build_app() -> FastAPI:
    application = FastAPI(title="Password Manager", debug=True, version="1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(SessionMiddleware, secret_key="temp-secret-key")
    application.include_router(api_router)
    return application


app = build_app()


@app.on_event("startup")
async def startup() -> None:
    app.state.DB = PasswordDB()
    await app.state.DB.initiate_db()
