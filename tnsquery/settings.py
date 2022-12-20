import enum
import logging
import os
from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings, Field
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    api_key: str = Field(..., env="TNSQUERY_API_KEY")  # Required TNSQUERY_API_KEY
    host: str = "0.0.0.0"
    port: int = Field(8080, env="TNSQUERY_PORT")
    # int(os.environ.get("PORT", 8080))
    # if port != 8080:  # not running in prod:
    #     logger = logging.getLogger()
    #     logger.setLevel(logging.DEBUG)
    #     logger.debug("port should be 8080, but is %s", port)
    #     # port = 8080
    # quantity of workers for uvicorn
    workers_count: int = 2
    # Enable uvicorn reloading
    reload: bool = True

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = Field("10.92.48.2", env="TNSQUERY_DB_HOST")
    db_port: int = 5432
    db_user: str = "tnsquery"
    db_pass: str = "tnsquery"
    db_base: str = "tnsquery"
    db_echo: bool = True

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "TNSQUERY_"
        env_file_encoding = "utf-8"


settings = Settings()
