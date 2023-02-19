import time
from dataclasses import dataclass, field

from fastapi import status
from httpx import Response


@dataclass
class ResetTime:  # noqa: WPS
    remaining_time: int = 0
    max_time: int = 0
    triggered: int = 0
    waited_time: int = 0
    safety_buffer: int = field(default=1, init=False)

    @staticmethod
    def get_reset_time(response: Response) -> int:
        # If any of the '...-remaining' values is zero, return the reset time
        for name in response.headers:
            value = response.headers.get(name)
            if name.endswith("-remaining") and value == "0":
                return int(response.headers.get(name.replace("remaining", "reset")))
        return 0

    async def update_max_reset_time(self, new_time: int) -> None:
        if self.max_time < new_time:
            self.max_time = new_time  # noqa: WPS

    async def update_remaining_time(self, new_time: int) -> None:
        if self.remaining_time < new_time:
            self.remaining_time = new_time  # noqa: WPS

    async def zero_remaining_time(self) -> None:
        self.remaining_time = 0  # noqa: WPS

    async def update_waited_time(self) -> None:
        self.waited_time += self.remaining_time + self.safety_buffer

    async def update_triggered(self) -> None:
        self.triggered += 1  # noqa: WPS

    async def wait_remaining_time(self) -> bool:
        """Wait the remaining time, update triggered,
        and return true if no longer limited"""
        time.sleep(self.remaining_time + self.safety_buffer)
        await self.update_waited_time()
        await self.zero_remaining_time()
        return not self.limited

    async def determine_if_limited(self, response: Response) -> bool:
        if response.status_code != status.HTTP_200_OK:
            return False

        new_time = self.get_reset_time(response)
        if new_time == 0:
            # Hurray we are no longer limited, reset everything.
            if self.limited:
                await self.zero_remaining_time()
            return self.limited

        # limited:
        await self.update_remaining_time(new_time)
        await self.update_max_reset_time(new_time)
        await self.update_triggered()
        return self.limited

    @property
    def limited(self) -> bool:
        return self.remaining_time > 0

# Singleton, hopefully.
reset_time = ResetTime()

# def get_reset_time() -> ResetTime:
#     """Return a singleton ResetTime instance"""


async def log_tns_usage(response: Response) -> None:
    """Use ResetTime singleton to log TNS usage"""
    raise NotImplementedError("Logging not implemented yet.")
    #await reset_time.determine_if_limited(response)
