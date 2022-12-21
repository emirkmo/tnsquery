from fastapi import APIRouter

from tnsquery.web.docs import open_api

docs_router = APIRouter()
docs_router.include_router(open_api.router)
