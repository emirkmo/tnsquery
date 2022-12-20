from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles

# from tnsquery.db.base import Base # noqa: E800
# from tnsquery.db.dependencies import get_db_session # noqa: E800
from tnsquery.web.api.router import api_router
from tnsquery.web.frontend.router import frontend_router
from tnsquery.web.lifetime import register_shutdown_event, register_startup_event


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="tnsquery",
        description="Python API for limited metadata queries of Supernovae/Transients from the Transient Name Server.",
        version=metadata.version("tnsquery"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)
    # create_db_tables(app) # noqa: E800
    # create_db_tables(app) # noqa: E800

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    app.include_router(router=frontend_router)
    app.mount(
        "/static", StaticFiles(directory="tnsquery/static", html=True), name="static"
    )
    return app
