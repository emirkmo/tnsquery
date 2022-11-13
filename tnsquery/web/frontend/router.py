from fastapi.routing import APIRouter
from fastapi import Depends

from tnsquery.db.dependencies import get_db_session
from tnsquery.web.api import transient

api_router = APIRouter()
api_router.include_router(transient.router)
