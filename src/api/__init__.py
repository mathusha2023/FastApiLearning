from fastapi import APIRouter
from src.api.cats import router as cats_router
from src.api.cats_images import router as cats_images_router

main_router = APIRouter(prefix="/api")
main_router.include_router(cats_router)
main_router.include_router(cats_images_router)
