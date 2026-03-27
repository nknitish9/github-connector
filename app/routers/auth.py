from fastapi import APIRouter, Security
from fastapi.security import HTTPAuthorizationCredentials

from app.core.github_client import security, get_token
from app.services.auth_service import verify_token, get_authenticated_user

router = APIRouter()


@router.get(
    "/verify",
    summary="Verify GitHub Token",
    description="Validate the provided PAT and return basic user info.",
)
async def verify(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await verify_token(token)


@router.get(
    "/me",
    summary="Get Authenticated User",
    description="Return the full GitHub profile of the authenticated user.",
)
async def me(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await get_authenticated_user(token)
