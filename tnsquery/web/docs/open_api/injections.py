from typing import Awaitable, Callable, TypeAlias

import bs4
from fastapi import Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from tnsquery.settings import settings
from tnsquery.web.docs.open_api.navbar import get_navbar
from tnsquery.web.docs.open_api.oauth2 import OAUTH2_REDIRECT_URL
from tnsquery.web.docs.open_api.title import get_openapi_title

AsyncIngestor: TypeAlias = Callable[[HTMLResponse], Awaitable[HTMLResponse]]


async def custom_swagger_ui_html() -> HTMLResponse:
    html = get_swagger_ui_html(
        openapi_url=settings.open_api_url,
        title="TNSQuery - Swagger UI",
        oauth2_redirect_url=OAUTH2_REDIRECT_URL,
        swagger_css_url=settings.swagger_css_url,
        swagger_favicon_url=settings.favicon_url,
    )
    return html


async def inject_navbar(
    html: HTMLResponse,
    navbar: str = get_navbar(),
) -> HTMLResponse:
    return await _inject_html(html, unique_query="<head>", injection=navbar)


async def inject_title(
    html: HTMLResponse,
    title: str = get_openapi_title(),
) -> HTMLResponse:
    query = '<div class="renderedMarkdown">'
    return await _inject_html(html, unique_query=query, injection=title)


async def _inject_html(
    html: HTMLResponse,
    unique_query: str,
    injection: str,
) -> HTMLResponse:
    if not injection.startswith(unique_query):
        injection = unique_query + injection

    html.body = html.body.replace(
        bytes(unique_query, encoding="utf-8"),
        bytes(injection, encoding="utf-8"),
    )
    html.raw_headers[0] = (
        bytes("Content-Length", "utf-8"),
        bytes(str(len(html.body)), "utf-8"),
    )
    return html


async def get_injected_swagger_ui_html(
    html: HTMLResponse = Depends(custom_swagger_ui_html),
) -> HTMLResponse:
    html = await inject_navbar(html)  # html = await inject_title(html)
    return html
