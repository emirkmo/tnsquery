import uvicorn

from tnsquery.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    uvicorn.run(
        "tnsquery:app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.value.lower(),
    )


if __name__ == "__main__":
    main()
