from fastapi import APIRouter
from .endpoints.project import router as project_router
from .endpoints.generation import router as generation_router
from .endpoints.status import router as status_router

api_router = APIRouter()
api_router.include_router(project_router, tags=["project"])
api_router.include_router(generation_router, tags=["generation"])
api_router.include_router(status_router, tags=["status"])
