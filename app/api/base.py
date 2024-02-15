from fastapi import APIRouter

from app.api.routes import auth, dashboard

api_router = APIRouter()

api_router.include_router(dashboard.router, tags=["dashboard"], prefix="/dashboard")
api_router.include_router(auth.router, tags=["auth"], prefix="/auth")
