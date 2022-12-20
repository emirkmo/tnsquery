import asyncio

from fastapi import Depends

from tnsquery.db.dao.transient_dao import TransientDAO
from tnsquery.db.models.transient_model import Transient, verify_transient_name
from tnsquery.services import fetch_tns_transient, fetch_tns_transients


async def fetch_and_record_tns_transient(
    name: str,
    dao: TransientDAO = Depends(),
) -> Transient:
    transient = await fetch_tns_transient(name)
    await dao.create_transient_model(transient)
    return transient


async def fetch_and_record_tns_transients(
    names: list[str],
    dao: TransientDAO = Depends(),
) -> list[Transient]:
    tns_transients = await fetch_tns_transients(names)
    await dao.record_transients(tns_transients)
    return tns_transients


async def fetch_transient(
    name: str,
    dao: TransientDAO = Depends(),
) -> Transient:

    transient = await dao.get_verified_transient(name)

    if transient is None:
        return await fetch_and_record_tns_transient(name)

    return transient.as_transient()


async def fetch_transients(
    names: list[str],
    dao: TransientDAO = Depends(),
    limit: int = 10,  # Move to Depends()
    offset: int = 0,  # Move to Depends()
) -> list[Transient]:
    clean_names = [verify_transient_name(name) for name in names]
    maybe_transients = await dao.get_transients(clean_names, limit, offset)
    db_transients = [at.as_transient() for at in maybe_transients if at is not None]

    # Query missing transients from TNS API service:
    retrieved = {at.name for at in db_transients}
    missing = set(clean_names) - retrieved
    tns_transients = await fetch_and_record_tns_transients(list(missing), dao)

    return db_transients + tns_transients


async def window_transients(
    limit: int = 10,
    offset: int = 0,
    dao: TransientDAO = Depends(),
) -> list[Transient]:
    ats = await dao.get_all_transients(limit, offset)
    transients = [at.as_transient() for at in ats]
    return transients
