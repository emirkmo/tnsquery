import asyncio

from tnsquery.db.dao.transient_dao import TransientDAO
from tnsquery.db.dao.monitoring_dao import TransientLogDAO
from tnsquery.db.models.monitoring_model import TransientLogModel
from tnsquery.db.models.transient_model import Transient, verify_transient_name
from tnsquery.services import fetch_tns_transient, fetch_tns_transients


async def fetch_and_record_tns_transient(
    name: str,
    transient_dao: TransientDAO,
    monitoring_dao: TransientLogDAO,
) -> Transient:
    transient, logs = await fetch_tns_transient(name)

    # Record transient and logs in parallel:
    # Don't save ATModel since we don't want to show ID
    await record_transients_and_logs(
        [transient], logs, transient_dao, monitoring_dao, True
    )

    return transient


async def fetch_and_record_tns_transients(
    names: list[str],
    transient_dao: TransientDAO,
    monitoring_dao: TransientLogDAO,
) -> list[Transient]:
    tns_transients, logs = await fetch_tns_transients(names)

    await record_transients_and_logs(
        tns_transients, logs, transient_dao, monitoring_dao
    )

    return tns_transients


async def fetch_transient(
    name: str, transient_dao: TransientDAO, monitoring_dao: TransientLogDAO
) -> Transient:
    transient = await transient_dao.get_verified_transient(name)

    if transient is None:
        return await fetch_and_record_tns_transient(name, transient_dao, monitoring_dao)

    return transient.as_transient()


async def fetch_transients(
    names: list[str],
    transient_dao: TransientDAO,
    monitoring_dao: TransientLogDAO,
    limit: int = 10,  # Move to Depends()
    offset: int = 0,  # Move to Depends()
) -> list[Transient]:
    clean_names = [verify_transient_name(name) for name in names]
    maybe_transients = await transient_dao.get_transients(clean_names, limit, offset)
    db_transients = [at.as_transient() for at in maybe_transients if at is not None]

    # Query missing transients from TNS API service:
    retrieved = {at.name for at in db_transients}
    missing = set(clean_names) - retrieved
    tns_transients = await fetch_and_record_tns_transients(
        list(missing), transient_dao, monitoring_dao
    )

    return db_transients + tns_transients


async def window_transients(
    transient_dao: TransientDAO,
    limit: int = 10,
    offset: int = 0,
) -> list[Transient]:
    ats = await transient_dao.get_all_transients(limit, offset)
    transients = [at.as_transient() for at in ats]
    return transients


async def record_transients_and_logs(
    transients: list[Transient],
    logs: list[TransientLogModel],
    transient_dao: TransientDAO,
    monitoring_dao: TransientLogDAO,
    single_transient: bool = False,
) -> None:
    if single_transient:
        transient_coroutine = transient_dao.create_transient_model(transients.pop())
    else:
        transient_coroutine = transient_dao.record_transients(transients)

    await asyncio.gather(transient_coroutine, monitoring_dao.upload_logs(logs))
