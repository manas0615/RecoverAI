from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette import status

from recoverai.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_frontend_key(
    api_key: str = Security(api_key_header),
) -> str:
    """
    Validates that the request has either the frontend client credential or the n8n orchestrator credential.
    Note: frontend_api_key is a lightweight credential, not a true confidential secret.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    if api_key not in (settings.frontend_api_key, settings.n8n_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key


def require_n8n_key(
    api_key: str = Security(api_key_header),
) -> str:
    """
    Validates that the request has the confidential n8n orchestrator credential.
    The frontend client credential is NOT authorized for these operations.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    if api_key == settings.frontend_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role for this endpoint",
        )
    if api_key != settings.n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key
