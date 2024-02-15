from fastapi import APIRouter, Depends

from app.api.routes import auth, dashboard
from app.dependencies.auth import get_current_user

api_router = APIRouter()

api_router.include_router(dashboard.router, tags=["dashboard"], prefix="/dashboard")
api_router.include_router(auth.router, tags=["auth"], prefix="/auth")
