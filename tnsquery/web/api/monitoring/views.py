from typing import Literal

from fastapi import APIRouter
from starlette import status

from tnsquery.services.monitor_tns import reset_time

router = APIRouter()


@router.get("/health")
def health_check() -> Literal[200]:
    """
    Checks the health of a project.
    It returns 200 since the project is up and running.
    """
    stat = status.HTTP_200_OK
    return stat


@router.get("/tns-time")
def tns_wait_time() -> dict[str, int]:
    """Return the current, total, and max wait times of the TNS API,
    as well as the number of times the wait time has been triggered."""
    return {
        "current": reset_time.remaining_time,
        "total": reset_time.waited_time,
        "max": reset_time.max_time,
        "triggered": reset_time.triggered,
    }
