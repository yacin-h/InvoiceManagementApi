from fastapi import APIRouter

from app.api.routers import login, signup, users


api_routers = APIRouter()
api_routers.include_router(login.router)
api_routers.include_router(signup.router)
api_routers.include_router(users.router)