from fastapi import APIRouter, Depends, Security, status
from fastapi.exceptions import HTTPException

from tnsquery.auth import get_api_key
from tnsquery.db.dao.transient_dao import TransientDAO
from tnsquery.db.models.transient_model import Transient

from .common_logic import (
    fetch_and_record_tns_transient,
    fetch_transient,
    fetch_transients,
    window_transients,
)

router = APIRouter()

TRANSIENTS_PAGE_LIMIT = 50


@router.get("/transients/{name}", response_model=Transient, tags=["transients"])
async def get_transient(
    name: str,
    force_tns: bool = False,
    dao: TransientDAO = Depends(),
) -> Transient:
    """
    Get transient data. If transient is not in the database or if force_tns
    is True, it will be fetched from TNS (even if it is in the database).

    Returns the data for a given transient.
    """
    if force_tns:
        return await fetch_and_record_tns_transient(name, dao)
    return await fetch_transient(name, dao)


@router.get("/search", response_model=Transient, tags=["transients"])
async def search_transient(
    name: str,
    dao: TransientDAO = Depends(),
) -> Transient:
    """
    Same as GET transient but used for searching via GET queries.
    Returns the matching transient. Will intellignetly strip
    leading SN/AT designations (SN2020XXY -> 2020XXY)

    Returns the data for a given transient as a simple HTML table instead of JSON."""
    return await fetch_transient(name, dao)


@router.get(
    "/transients", response_model=list[Transient], tags=["transients"]
)  # include_in_schema=False
async def list_all_transients(
    limit: int = 10,
    offset: int = 0,
    dao: TransientDAO = Depends(),
) -> list[Transient]:
    return await window_transients(limit, offset, dao)


@router.post("/transients", response_model=list[Transient], tags=["transients"])
async def get_transients(
    names: list[str],
    limit: int = 10,
    offset: int = 0,
    dao: TransientDAO = Depends(),
) -> list[Transient]:
    """
    Get transient data as a list. If transient is not in the database
    it will be fetched from TNS.

    Returns all transients in current db or list of transients.
    """
    limit = min(limit, TRANSIENTS_PAGE_LIMIT)

    if _names_means_want_all(names):
        return await window_transients(limit, offset, dao)

    transients = await fetch_transients(names, dao=dao, limit=limit, offset=offset)
    return transients


test = get_transients


def _names_means_want_all(names: list[str]) -> bool:
    names_has_default_strings = len({"all", "string"} | set(names)) > 1
    want_all = len(names) == 1 and names_has_default_strings
    get_all = len(names) == 0 or want_all
    return get_all  # noqa: WPS


@router.patch("/transients/{name}/redshift", response_model=Transient, tags=["auth"])
async def update_redshift(
    name: str,
    redshift: float,
    dao: TransientDAO = Depends(),
    api_key: str = Security(get_api_key),
) -> Transient:
    """
    Update transient redshift"""

    stored_at = await dao.get_transient(name)
    if not stored_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Transient {name} not found."
        )
    await dao.update_param(stored_at, "redshift", redshift)
    return stored_at.as_transient()


@router.patch("/transients/{name}/ebv", response_model=Transient, tags=["auth"])
async def update_ebv(
    name: str,
    ebv: float,
    dao: TransientDAO = Depends(),
    api_key: str = Security(get_api_key),
) -> Transient:
    """
    Update transient ebv"""

    stored_at = await dao.get_transient(name)
    if not stored_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Transient {name} not found."
        )

    await dao.update_param(stored_at, "ebv", ebv)

    return stored_at.as_transient()
