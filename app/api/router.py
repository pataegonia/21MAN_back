from fastapi import APIRouter

from app.api.routes import auth, health, merge, pull_request, repositories, search, tags, users, notifications

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(repositories.router)
api_router.include_router(search.router)
api_router.include_router(notifications.router)
api_router.include_router(health.router)
api_router.include_router(merge.router)
api_router.include_router(pull_request.router)
api_router.include_router(tags.router)
