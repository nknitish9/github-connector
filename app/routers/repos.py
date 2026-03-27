from fastapi import APIRouter, Security, Query
from fastapi.security import HTTPAuthorizationCredentials

from app.core.github_client import security, get_token
from app.services.repo_service import (
    list_user_repos,
    list_org_repos,
    get_repo,
    list_authenticated_user_repos,
)

router = APIRouter()


@router.get(
    "/me",
    summary="List My Repositories",
    description="List repositories for the authenticated user (includes private repos).",
)
async def my_repos(
    per_page: int = Query(30, ge=1, le=100, description="Results per page"),
    page: int = Query(1, ge=1, description="Page number"),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await list_authenticated_user_repos(token, per_page=per_page, page=page)


@router.get(
    "/user/{username}",
    summary="List User Repositories",
    description="List public repositories for any GitHub user.",
)
async def user_repos(
    username: str,
    per_page: int = Query(30, ge=1, le=100),
    page: int = Query(1, ge=1),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await list_user_repos(token, username=username, per_page=per_page, page=page)


@router.get(
    "/org/{org}",
    summary="List Organization Repositories",
    description="List repositories for a GitHub organization.",
)
async def org_repos(
    org: str,
    per_page: int = Query(30, ge=1, le=100),
    page: int = Query(1, ge=1),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await list_org_repos(token, org=org, per_page=per_page, page=page)


@router.get(
    "/{owner}/{repo}",
    summary="Get Repository",
    description="Fetch details for a specific repository.",
)
async def repo_details(
    owner: str,
    repo: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await get_repo(token, owner=owner, repo=repo)
