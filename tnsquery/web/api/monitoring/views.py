from typing import Literal, Optional

from fastapi import APIRouter, Depends
from starlette import status

from tnsquery.services.monitor_tns import reset_time
from tnsquery.db.dao.monitoring_dao import TransientLogDAO
from tnsquery.db.models.monitoring_model import TransientLogModel

router = APIRouter()


@router.get("/health", tags=["monitoring"])
async def health_check() -> Literal[200]:
    """
    Checks the health of a project.
    It returns 200 since the project is up and running.
    """
    stat = status.HTTP_200_OK
    return stat


@router.get("/tns-time", tags=["monitoring"])
async def tns_wait_time() -> dict[str, int]:
    """Return the current, total, and max wait times of the TNS API,
    as well as the number of times the wait time has been triggered."""
    return {
        "current": reset_time.remaining_time,
        "total": reset_time.waited_time,
        "max": reset_time.max_time,
        "triggered": reset_time.triggered,
    }


@router.get("/tns-log", tags=["monitoring"])
async def tns_log(
    limit: int = 10, offset: int = 0, dao: TransientLogDAO = Depends()
) -> list[TransientLogModel]:
    """Return the log of TNS API calls."""
    return await dao.get_transient_log(limit, offset)
    # return await dao.get_tns_log(limit, offset)


@router.post("/tns-log", tags=["monitoring"])
async def filter_tns_log(
    id: Optional[int] = None,
    code: int = 200,
    name: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    dao: TransientLogDAO = Depends(),
) -> list[TransientLogModel]:
    """Return the filtered log of TNS API calls."""
    return await dao.filter(id, code, name, limit, offset)
    # return await dao.get_tns_log(limit, offset)
