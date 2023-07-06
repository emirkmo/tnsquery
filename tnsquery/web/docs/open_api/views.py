from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tnsquery.web.docs.open_api.injections import get_injected_swagger_ui_html

router = APIRouter()


@router.get("/api/docs", include_in_schema=False, response_class=HTMLResponse)
async def custom_swagger_ui_html(
    html: HTMLResponse = Depends(get_injected_swagger_ui_html),
) -> HTMLResponse:
    return html
