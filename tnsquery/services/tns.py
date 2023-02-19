"""TNS Service module. Provides TNSAPI as an async context manager."""
import asyncio
import json
import logging
import os
from dataclasses import field
from enum import Enum
from typing import Any, Optional, Type

from fastapi import HTTPException, status
from httpx import AsyncClient, Response
from pydantic.dataclasses import dataclass

from tnsquery.db.models.transient_model import Transient
from tnsquery.services.monitor_tns import reset_time


class StrEnum(str, Enum):
    """Enum with string values."""

    def __str__(self) -> str:
        return str(self.value)


class TNSURL(StrEnum):
    api = "https://www.wis-tns.org/api/get"
    search = "https://www.wis-tns.org/search"


class Config:
    arbitrary_types_allowed = True


@dataclass
class TNSBot:
    id: int = 140550
    name: str = "snphot_bot"
    user_agent: str = field(init=False)
    api_key: str = field(init=False)
    api_key_file: str = field(default="TNS_API_KEY.SECRET")
    headers: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Post init."""
        self.user_agent = " "
        self.api_key = self.get_api_key()
        self.headers = {
            "user-agent": 'tns_marker{"tns_id":'
            + str(self.id)
            + ',"type":"bot","name":"'
            + self.name
            + '"}'
        }

    def get_api_key(self) -> str:
        api_key = os.environ.get("TNS_API_KEY", None)
        if api_key is None:
            api_key = self.read_api_keyfile()
        return api_key

    def read_api_keyfile(self) -> str:
        with open(self.api_key_file, "r") as f:
            api_key = f.read()
        if not api_key:
            raise ValueError(f"API key not found in file: {self.api_key_file}")
        return api_key


@dataclass(config=Config)
class TNSAPI:
    bot: TNSBot = field(default_factory=TNSBot)
    client_type: Type[AsyncClient] = field(default=AsyncClient)
    client: AsyncClient = field(init=False)
    params: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post init."""
        self.params = {"api_key": self.bot.api_key}
        self.data = {"photometry": "0", "spectra": "0"}
        self.client = self.client_type()

    async def get_obj(self, name: str) -> Optional[dict[str, Any]]:
        data = {"objname": name, "photometry": "0", "spectra": "0"}
        params = {"api_key": self.bot.api_key, "data": json.dumps(data)}

        max_tries = 3
        for _ in range(max_tries):
            response: Response = await self.client.post(
                url=TNSURL.api + "/object", data=params, headers=self.bot.headers
            )

            logging.info(
                f"TNS Request {data['objname']} with bot id {self.bot.id} "
                f"received: {response.status_code}"
            )
            # Determine if we are rate limited
            limited = await reset_time.determine_if_limited(response)

            if not limited:
                break
            logging.info("limited!: waiting: {reset_time.remaining_time}s")
            # we are rate limited, must wait.
            await reset_time.wait_remaining_time()
        else:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="TNS access was rejected 3 times.",
            )

        logging.info(response.json())
        data = self.validate_response(response)
        return data

    @staticmethod
    def validate_response(response: Response) -> Optional[dict[str, Any]]:
        response.raise_for_status()
        data = response.json()["data"]

        if "reply" in data:
            reply = data["reply"]
            if not reply:
                return None
            if "objname" not in reply:  # Bit of a cheat, but it is simple and works
                return None
            reply["internal_names"] = [
                name.strip()
                for name in reply["internal_names"].split(",")
                if name.strip()
            ]
            return reply
        return None

    async def make_transient(self, name: str) -> Transient:
        data = await self.get_obj(name)
        if data is None:
            raise ValueError(f"Transient not found: {name}")
        name = data["objname"]
        z = data["redshift"] if data["redshift"] else 0
        ra = data["radeg"]
        dec = data["decdeg"]
        ebv: float = 0
        return Transient(name=name, redshift=z, ra=ra, dec=dec, ebv=ebv)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.client.aclose()


async def fetch_tns_transients(names: list[str]) -> list[Transient]:

    async with TNSAPI() as tns:
        transient_awaitables = (tns.make_transient(name) for name in names)
        transients: list[Transient] = await asyncio.gather(*transient_awaitables)

    return transients


async def fetch_tns_transient(name: str) -> Transient:
    tns_transients = await fetch_tns_transients([name])
    transient = tns_transients.pop()
    return transient
