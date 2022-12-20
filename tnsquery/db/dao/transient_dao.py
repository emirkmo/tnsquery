import asyncio
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import Float, Integer, String, cast, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from tnsquery.db.dependencies import get_db_session
from tnsquery.db.models.transient_model import ATModel, Transient, verify_transient_name


class TransientDAO:
    """Class for accessing transient table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_transient_model(self, transient: Transient) -> ATModel:
        """
        Add single transient to session.

        :param name: name of a transient.
        """
        at = ATModel.from_transient(transient)
        self.session.add(at)
        return at

    async def record_transients(self, transients: List[Transient]) -> None:
        await asyncio.gather(
            *(self.create_transient_model(transient) for transient in transients),
        )

    async def get_all_transients(self, limit: int, offset: int) -> List[ATModel]:
        """
        Get all transient models with limit/offset pagination.

        :param limit: limit of transients.
        :param offset: offset of transients.
        :return: transients, a stream of transients.
        """
        raw_transients = await self.session.execute(
            select(ATModel).limit(limit).offset(offset),
        )

        transients: List[ATModel] = raw_transients.scalars().fetchall()
        return transients

    async def get_transients(
        self,
        names: list[str],
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Optional[ATModel]]:
        """
        Get specific transient model.

        :param name: name of transient instance.
        :return: transient models.
        """
        query = select(ATModel).filter(ATModel.name.in_(names))
        rows = await self.session.execute(query.limit(limit).offset(offset))
        transients: List[Optional[ATModel]] = rows.scalars().all()
        return transients

    async def get_transient(
        self,
        name: str,
    ) -> Optional[ATModel]:
        """
        Get specific transient model.

        :param name: name of transient instance.
        :return: transient models.
        """
        query = select(ATModel).filter_by(name=name)
        rows = await self.session.execute(query)
        one: Optional[ATModel] = rows.scalar_one_or_none()
        return one

    async def delete(self, name: str) -> None:
        """
        Delete transient model.

        :param name: name of transient instance.
        """
        query = delete(ATModel).where(ATModel.name == name)
        await self.session.execute(query)
        await self.session.flush()

    async def update_param(
        self, model: ATModel, paramname: str, paramvalue: str | float
    ) -> None:
        """
        Update parameter of transient model.

        :param name: name of parameter to update.
        :paramvalue: value of updated parameter.
        """
        self.session.add(model)
        setattr(model, paramname, paramvalue)
        await self.session.flush()

    async def get_verified_transient(self, name: str) -> Optional[ATModel]:
        """
        Get transients with verified name,
        Raises Exception if name is malformed.

        :param name: name of parameter to update.
        :return: transient model
        """
        name = verify_transient_name(name)
        transient = await self.get_transient(name)
        return transient

    async def get_verified_transients(
        self,
        names: list[str],
        limit: int = 1000,
        offset: int = 0,
    ) -> List[ATModel | None]:
        clean_names = [verify_transient_name(name) for name in names]
        return await self.get_transients(clean_names, limit=limit, offset=offset)
