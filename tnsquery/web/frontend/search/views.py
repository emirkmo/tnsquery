import warnings
from dataclasses import asdict
from enum import auto
from typing import Any, Awaitable, Callable, Collection, Literal, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_400_BAD_REQUEST

from tnsquery.db.dao.transient_dao import TransientDAO
from tnsquery.db.models.transient_model import Transient
from tnsquery.services.tns import StrEnum
from tnsquery.web.api.transient.views import (
    get_transient,
    get_transients,
    list_all_transients,
)

# from tnsquery.web.frontend.templates import TemplateResponse, Templates, templates

router = APIRouter()

templates = Jinja2Templates(directory="tnsquery/templates")


async def display_transients(
    request: Request,
    transients: list[Transient],
):
    """Return template transient HTML"""
    items = [asdict(transient) for transient in transients]
    context = {"request": request, "items": items}
    return templates.TemplateResponse("simple_table.html", context)


class Names(StrEnum):
    EMPTY = auto()
    SINGLE = auto()
    MULTIPLE = auto()


TransientAwaitable: TypeAlias = Callable[..., Awaitable[Transient | list[Transient]]]
CoroutineAndArgs: TypeAlias = tuple[TransientAwaitable, Collection[str]]

ENDPOINT_MAPPING: dict[Names, CoroutineAndArgs] = {
    Names.EMPTY: (list_all_transients, ("limit", "offset", "dao")),
    Names.SINGLE: (get_transient, ("name", "dao")),
    Names.MULTIPLE: (get_transients, ("names", "limit", "offset", "dao")),
}


async def parse_name_string(name: str) -> tuple[Names, list[str]]:
    if name == "":
        return Names.EMPTY, [""]
    stripped_name = "".join(name.split())
    names = stripped_name.split(",")
    if len(names) == 1:
        return Names.SINGLE, names
    elif len(names) > 1:
        return Names.MULTIPLE, names
    raise ValueError(
        f"Unable to determine type of Names, {name}. Name was not properly defined"
    )


async def _get_name_endpoint_and_args(name: Names) -> CoroutineAndArgs:
    endpoint, args = ENDPOINT_MAPPING[name]
    return endpoint, args


def _resolve_kwargs(
    names: list[str], kwargs: dict[str, Any], args: Collection[str]
) -> dict[str, Any]:

    if "name" in args:
        kwargs["name"] = names[0]
    elif "names" in args:
        kwargs["names"] = names

    return {key: value for key, value in kwargs.items() if key in args}


async def call_name_endpoint_with_kwargs(
    name: str, **kwargs: Any
) -> Transient | list[Transient]:
    name_type, names = await parse_name_string(name)
    awaitable, args = await _get_name_endpoint_and_args(name_type)
    used_kwargs = _resolve_kwargs(names, kwargs, args)
    transients = await awaitable(**used_kwargs)
    return transients


@router.get("/search", response_class=HTMLResponse, tags=["frontend"])
async def search(
    request: Request,
    name: str = "",
    subtype: str = "",
    limit: int = 10,
    offset: int = 0,
    dao: TransientDAO = Depends(),
):
    """
    :param: name = name
    :param: subtype = subtype
    Same as GET transient but used for searching via GET queries.
    Returns the matching transient. Will intellignetly strip
    leading SN/AT designations (SN2020XXY -> 2020XXY)

    Returns the data for a given transient as a simple HTML table instead of JSON."""

    kwargs = {
        "subtype": subtype,
        "limit": limit,
        "offset": offset,
        "dao": dao,
    }

    transients = await call_name_endpoint_with_kwargs(name, **kwargs)
    if not isinstance(transients, list):
        transients = [transients]

    if subtype != "":
        warnings.warn(f"Subtype was {subtype}, but subtypes are not implemented yet")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Supernova with name {name} not found. Other queries are not implemented yet.",
        )
    return await display_transients(request, transients)

    # if name == "":
    #     transients = await list_all_transients(limit=limit, offset=offset, dao=dao)
    #     return await display_transients(request, transients)

    # stripped_name = "".join(name.split())
    # names = stripped_name.split(",")
    # if len(names) == 1:
    #     transients = [await get_transient(names[0], dao=dao)]
    #     return await display_transients(request, transients)

    # transients = await get_transients(
    #     names=names,
    #     limit=limit,
    #     offset=offset,
    #     dao=dao,
    # )

    # return await display_transients(request, transients)
