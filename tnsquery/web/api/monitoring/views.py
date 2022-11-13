from fastapi import APIRouter
from starlette import status
from typing import Literal

router = APIRouter()


@router.get("/health")
def health_check() -> Literal[200]:
    """
    Checks the health of a project.
    It returns 200 since the project is up and running.
    """
    stat = status.HTTP_200_OK
    return stat