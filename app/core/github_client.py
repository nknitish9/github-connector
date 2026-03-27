import os
import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"

# auto_error=False allows requests without Authorization header to fall through
security = HTTPBearer(auto_error=False)


def get_github_headers(token: str) -> dict:
    """Build standard GitHub API headers."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "GitHub-Cloud-Connector/1.0",
    }


def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> str:
    """
    Extract Bearer token from Authorization header.
    Falls back to GITHUB_TOKEN from .env if no header is provided.
    """
    if credentials and credentials.credentials:
        return credentials.credentials

    # Fallback: use token from environment variable (.env file)
    env_token = os.getenv("GITHUB_TOKEN")
    if env_token:
        return env_token

    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide a Bearer token in the Authorization header or set GITHUB_TOKEN in .env",
    )


async def github_request(
    method: str,
    endpoint: str,
    token: str,
    params: Optional[dict] = None,
    json: Optional[dict] = None,
) -> dict | list:
    """
    Make an authenticated request to the GitHub API.

    Raises HTTPException on non-2xx responses.
    """
    url = f"{GITHUB_API_BASE}{endpoint}"
    headers = get_github_headers(token)

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
        )

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired GitHub token.")
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="GitHub token lacks required permissions.")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Resource not found on GitHub.")
    if response.status_code == 422:
        raise HTTPException(
            status_code=422,
            detail=f"Unprocessable request: {response.json().get('message', 'Unknown error')}",
        )
    if not response.is_success:
        detail = response.json().get("message", "GitHub API error") if response.content else "GitHub API error"
        raise HTTPException(status_code=response.status_code, detail=detail)

    if response.status_code == 204 or not response.content:
        return {}

    return response.json()
