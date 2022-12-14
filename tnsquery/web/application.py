from importlib import metadata

from fastapi import FastAPI, Depends
from fastapi.responses import UJSONResponse
from tnsquery.db.dependencies import get_db_session

from tnsquery.web.api.router import api_router
from tnsquery.web.lifetime import register_shutdown_event, register_startup_event, create_db_tables
from tnsquery.db.base import Base


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="tnsquery",
        description="Python API for limited queries of the Transient Name Server to obtain Supernova/Transient metadata ",
        version=metadata.version("tnsquery"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)
    # create_db_tables(app)
    # create_db_tables(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
