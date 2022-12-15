from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery

from tnsquery.settings import settings

API_KEY_HEADER = APIKeyHeader(name="api_key", auto_error=False)
API_KEY_QUERY = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_header: str = Security(API_KEY_HEADER),
    api_key_query: str = Security(API_KEY_QUERY),
) -> str:
    """
    Get api key from `api_key` header or query parameter, authenticate on match to secret.

    :param api_key_header: api_key header.
    :param api_key_query: api_key in query.
    :return: string api_key.

    Raises
    :raise: HTTPException
    """
    if api_key_query == settings.api_key:
        return api_key_header

    elif api_key_header == settings.api_key:
        return api_key_header

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate API KEY.",
    )
