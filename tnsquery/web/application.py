from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles

from tnsquery.settings import settings
from tnsquery.web.api.router import api_router
from tnsquery.web.docs.open_api.title import custom_title
from tnsquery.web.docs.router import docs_router
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
        description="Python API for limited metadata queries of Supernovae/Transients from the Transient Name Server."
        + custom_title,
        version=metadata.version("tnsquery"),
        redoc_url=settings.redoc_url,
        openapi_url=settings.open_api_url,
        default_response_class=UJSONResponse,
    )
    # Startup and Shutdown events
    register_startup_event(app)
    register_shutdown_event(app)

    # API & Frontend Routes
    app.include_router(router=api_router, prefix="/api")
    app.include_router(router=frontend_router)

    # Open API
    app.mount("/openapi", StaticFiles(directory="tnsquery/openapi"), name="openapi")
    app.include_router(router=docs_router)

    # Static HTML serving on root (must be last)!
    app.mount(
        "/static", StaticFiles(directory="tnsquery/static", html=True), name="static"
    )
    app.mount("/", StaticFiles(directory="tnsquery/static", html=True), name="root")

    return app
