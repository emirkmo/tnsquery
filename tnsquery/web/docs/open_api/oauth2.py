import inspect

from fastapi import FastAPI

OAUTH2_REDIRECT_URL: str = (
    inspect.signature(FastAPI.__init__)  # noqa:WPS609
    .parameters["swagger_ui_oauth2_redirect_url"]
    .default
)
