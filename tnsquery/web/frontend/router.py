from fastapi import APIRouter

from tnsquery.web.frontend import search

frontend_router = APIRouter()
frontend_router.include_router(search.router)
