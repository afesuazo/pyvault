from fastapi import APIRouter

from app.api.routes import dashboard

api_router = APIRouter()

api_router.include_router(dashboard.router, tags=["dashboard"], prefix="/dashboard")
