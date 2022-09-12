from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import scoped_session
from tnsquery.db.models.transient_model import Transient
from tnsquery.db.dao import transient_dao
from tnsquery.db.dao.transient_dao import TransientDAO
from tnsquery.services.tns import TNSAPI
from tnsquery.db.dependencies import get_db_session

router = APIRouter()


@router.get("/transient/{name}", response_model=Transient)
async def get_transient(name: str, force_tns: bool = False, dao: TransientDAO = Depends()) -> Transient:
    """
    Get transient data. If transient is not in the database or if force_tns 
    is True, it will be fetched from TNS (even if it is in the database).
    Else, it will be loaded from the database.

    Returns the data for a given transient.
    """
    if not force_tns:
        at = await dao.get_transient(name)
        if at is not None:
            return at.as_transient()
    
    # Transient not found in DB or force reload was set, try to fetch it from TNS.
    async with TNSAPI() as tns:
        transient = await tns.make_transient(name)
        at = await dao.create_transient_model(transient)

    return at.as_transient()

@router.patch("/transient/{name}/redshift", response_model=Transient)
async def update_redshift(name:str, redshift: float, dao: TransientDAO = Depends()) -> Transient:
    """
    Update transient redshift"""

    stored_at = await dao.get_transient(name)
    if not stored_at:
        raise HTTPException(status_code=404, detail=f"Transient {name} not found.")
    stored_at.redshift=redshift  # type: ignore
    return stored_at.as_transient()

@router.patch("/transient/{name}/ebv", response_model=Transient)
async def update_ebv(name:str, ebv: float, dao: TransientDAO = Depends()) -> Transient:
    """
    Update transient ebv"""

    stored_at = await dao.get_transient(name)
    if not stored_at:
        raise HTTPException(status_code=404, detail=f"Transient {name} not found.")
    stored_at.ebv=ebv  # type: ignore
    return stored_at.as_transient()
  
