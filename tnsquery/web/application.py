from importlib import metadata

import bs4
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles

# from tnsquery.db.base import Base # noqa: E800
# from tnsquery.db.dependencies import get_db_session # noqa: E800
from tnsquery.web.api.router import api_router
from tnsquery.web.frontend.router import frontend_router
from tnsquery.web.lifetime import register_shutdown_event, register_startup_event

NAVBAR = """
<head>
<style>
:root {
  --nav-element-spacing-vertical: 1rem;
  --nav-element-spacing-horizontal: 0.5rem;
  --nav-link-spacing-vertical: 0.5rem;
  --nav-link-spacing-horizontal: 0.5rem;
}
/**
 * Nav
 */
:where(nav li)::before {
  float: left;
  content: "​";
}

nav,
nav ul {
  display: flex;
}

nav {
  justify-content: space-between;
}
nav ol,
nav ul {
  align-items: center;
  margin-bottom: 0;
  padding: 0;
  list-style: none;
}
nav ol:first-of-type,
nav ul:first-of-type {
  margin-left: calc(var(--nav-element-spacing-horizontal) * -1);
}
nav ol:last-of-type,
nav ul:last-of-type {
  margin-right: calc(var(--nav-element-spacing-horizontal) * -1);
}
nav li {
  display: inline-block;
  margin: 0;
  padding: var(--nav-element-spacing-vertical) var(--nav-element-spacing-horizontal);
}
nav li > * {
  --spacing: 0;
}
nav :where(a, [role=link]) {
  display: inline-block;
  margin: calc(var(--nav-link-spacing-vertical) * -1) calc(var(--nav-link-spacing-horizontal) * -1);
  padding: var(--nav-link-spacing-vertical) var(--nav-link-spacing-horizontal);
  border-radius: var(--border-radius);
  text-decoration: none;
}
nav :where(a, [role=link]):is([aria-current], :hover, :active, :focus) {
  text-decoration: none;
}
nav[aria-label=breadcrumb] {
  align-items: center;
  justify-content: start;
}
nav[aria-label=breadcrumb] ul li:not(:first-child) {
  -webkit-margin-start: var(--nav-link-spacing-horizontal);
  margin-inline-start: var(--nav-link-spacing-horizontal);
}
nav[aria-label=breadcrumb] ul li:not(:last-child) ::after {
  position: absolute;
  width: calc(var(--nav-link-spacing-horizontal) * 2);
  -webkit-margin-start: calc(var(--nav-link-spacing-horizontal) / 2);
  margin-inline-start: calc(var(--nav-link-spacing-horizontal) / 2);
  content: "/";
  color: var(--muted-color);
  text-align: center;
}
nav[aria-label=breadcrumb] a[aria-current] {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  pointer-events: none;
}
</style>
<nav>
    <ul>
      <li><strong><a href="/static">TNSQUERY</strong></a></li>
    </ul>
    <ul>
      <li><a href="/api/docs#">Docs</a></li>
      <li><a href="/search">Search</a></li>
      <li><a href="https://github.com/emirkmo/tnsquery"">GitHub</a></li>
    </ul>
</nav>
"""

app = FastAPI(
    title="tnsquery",
    description="Python API for limited metadata queries of Supernovae/Transients"
    "from the Transient Name Server.   \n"
    '<a href="/" class="nostyle"><b>[Return to TNSQuery HomePage]<b></a>',
    version=metadata.version("tnsquery"),
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    default_response_class=UJSONResponse,
    # docs_url="/api/docs",
)
register_startup_event(app)
register_shutdown_event(app)
# Adds startup and shutdown events.

# create_db_tables(app) # noqa: E800
# create_db_tables(app) # noqa: E800

# Main router for the API.

app.include_router(router=api_router, prefix="/api")
app.include_router(router=frontend_router)

app.mount("/openapi", StaticFiles(directory="tnsquery/openapi"), name="openapi")


@app.get("/api/docs", include_in_schema=False, response_class=HTMLResponse)
async def custom_swagger_ui_html() -> HTMLResponse:
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="TNSQuery - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        # swagger_js_url=app. #"/openapi/swagger-ui-bundle.js",
        swagger_css_url="/openapi/dark.css",
        # swagger_ui_parameters=app.swagger_ui_parameters,
        swagger_favicon_url="/static/favicon.ico",
    )
    bs = bs4.BeautifulSoup(html.body, "html.parser")
    # print(bs.prettify())
    html.body = html.body.replace(
        bytes("<head>", encoding="utf-8"), bytes(NAVBAR, encoding="utf-8")
    )
    html.raw_headers[0] = (
        bytes("Content-Length", "utf-8"),
        bytes(str(len(html.body)), "utf-8"),
    )
    # html.body = htmlbody
    # print([c for c in bs.children])
    return html


app.mount("/static", StaticFiles(directory="tnsquery/static", html=True), name="static")
app.mount("/", StaticFiles(directory="tnsquery/static", html=True), name="root")


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """

    return app
