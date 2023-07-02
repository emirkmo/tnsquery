from typing import List, Optional

from fastapi import Depends
from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tnsquery.db.dependencies import get_db_session
from tnsquery.db.models.monitoring_model import TransientLogModel


class MonitoringDAO:
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def log_monitoring(
        self, query: str, response: str, code: int = status.HTTP_200_OK
    ) -> None:
        """
        Add single query and response to tns_monitoring

        :param name: name of a monitoring.
        """

        self.session.add(TransientLogModel(query=query, response=response, code=code))

    async def get_tns_log(self, limit: int, offset: int) -> List[TransientLogModel]:
        """
        Get all dummy models with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of dummies.
        """
        raw_dummies = await self.session.execute(
            select(TransientLogModel).limit(limit).offset(offset),
        )

        return raw_dummies.scalars().fetchall()

    async def filter(
        self,
        id: Optional[int] = None,
        code: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[TransientLogModel]:
        """
        Get specific dummy model.

        :param name: name of dummy instance.
        :return: dummy models.
        """

        query = select(TransientLogModel)
        if id:
            query = query.where(TransientLogModel.id == id)
        if code:
            query = query.where(TransientLogModel.code == code)
        query = query.limit(limit).offset(offset)
        rows = await self.session.execute(query)
        return rows.scalars().fetchall()


class TransientLogDAO:
    """Class for accessing transient log table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def log_monitoring(
        self, name: str, query: str, response: str, code: int = status.HTTP_200_OK
    ) -> None:
        """
        Add single query and response to transient log

        :param name: name of a transient.

        """
        self.session.add(
            TransientLogModel(name=name, query=query, response=response, code=code)
        )

    async def upload_logs(self, logs: List[TransientLogModel]) -> None:
        """
        Add multiple logs to transient log

        :param logs: list of logs to add.
        """
        self.session.add_all(logs)

    async def get_transient_log(
        self, limit: int, offset: int
    ) -> List[TransientLogModel]:
        """
        Get all logs with limit/offset pagination.

        :param limit: limit of dummies.
        :param offset: offset of dummies.
        :return: stream of dummies.
        """
        raw_dummies = await self.session.execute(
            select(TransientLogModel).limit(limit).offset(offset),
        )

        return raw_dummies.scalars().fetchall()

    async def filter(
        self,
        id: Optional[int] = None,
        code: Optional[int] = None,
        name: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[TransientLogModel]:
        """
        Get specific transient log.

        :param name: name of transient.
        :return: dummy models.
        """

        query = select(TransientLogModel)
        if id:
            query = query.where(TransientLogModel.id == id)
        if code:
            query = query.where(TransientLogModel.code == code)
        if name:
            query = query.where(TransientLogModel.name == name)
        query = query.limit(limit).offset(offset)
        rows = await self.session.execute(query)
        return rows.scalars().fetchall()
