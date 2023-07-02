from fastapi import APIRouter, Depends, Security, status
from fastapi.exceptions import HTTPException

from tnsquery.auth import get_api_key
from tnsquery.db.dao.monitoring_dao import TransientLogDAO
from tnsquery.db.dao.transient_dao import TransientDAO
from tnsquery.db.models.transient_model import Transient
from tnsquery.db.dependencies import get_db_session

from .common_logic import (
    fetch_and_record_tns_transient,
    fetch_transient,
    fetch_transients,
    window_transients,
)

router = APIRouter()

TRANSIENTS_PAGE_LIMIT = 50


@router.get(
    "/transients/{name}",
    response_model=Transient,
    tags=["transients"],
    dependencies=[
        Depends(get_db_session),
        Depends(TransientDAO),
        Depends(TransientLogDAO),
    ],
)
async def get_transient(
    name: str,
    force_tns: bool = False,
    transient_dao: TransientDAO = Depends(),
    monitoring_dao: TransientLogDAO = Depends(),
) -> Transient:
    """
    Get transient data. If transient is not in the database or if force_tns
    is True, it will be fetched from TNS (even if it is in the database).

    Returns the data for a given transient.
    """
    if force_tns:
        return await fetch_and_record_tns_transient(name, transient_dao, monitoring_dao)
    return await fetch_transient(name, transient_dao, monitoring_dao)


@router.get("/search", response_model=Transient, tags=["transients"])
async def search_transient(
    name: str,
    transient_dao: TransientDAO = Depends(),
    monitoring_dao: TransientLogDAO = Depends(),
) -> Transient:
    """
    Same as GET transient but used for searching via GET queries.
    Returns the matching transient. Will intellignetly strip
    leading SN/AT designations (SN2020XXY -> 2020XXY)

    Returns the data for a given transient as a simple HTML table instead of JSON."""
    return await fetch_transient(name, transient_dao, monitoring_dao)


@router.get(
    "/transients", response_model=list[Transient], tags=["transients"]
)  # include_in_schema=False
async def list_all_transients(
    limit: int = 10,
    offset: int = 0,
    transient_dao: TransientDAO = Depends(),
) -> list[Transient]:
    return await window_transients(transient_dao, limit, offset)


@router.post("/transients", response_model=list[Transient], tags=["transients"])
async def get_transients(
    names: list[str],
    limit: int = 10,
    offset: int = 0,
    transient_dao: TransientDAO = Depends(),
    monitoring_dao: TransientLogDAO = Depends(),
) -> list[Transient]:
    """
    Get transient data as a list. If transient is not in the database
    it will be fetched from TNS.

    Returns all transients in current db or list of transients.
    """
    limit = min(limit, TRANSIENTS_PAGE_LIMIT)

    if _names_means_want_all(names):
        return await window_transients(transient_dao, limit, offset)

    transients = await fetch_transients(
        names,
        transient_dao=transient_dao,
        monitoring_dao=monitoring_dao,
        limit=limit,
        offset=offset,
    )
    return transients


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
