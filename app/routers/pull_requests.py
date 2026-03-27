from fastapi import APIRouter, Security, Query
from fastapi.security import HTTPAuthorizationCredentials
from typing import Literal

from app.core.github_client import security, get_token
from app.models.schemas import CreatePullRequestRequest
from app.services.pr_service import list_pull_requests, get_pull_request, create_pull_request

router = APIRouter()


@router.get(
    "/{owner}/{repo}",
    summary="List Pull Requests",
    description="List pull requests for a repository.",
)
async def get_prs(
    owner: str,
    repo: str,
    state: Literal["open", "closed", "all"] = Query("open", description="Filter by PR state"),
    per_page: int = Query(30, ge=1, le=100),
    page: int = Query(1, ge=1),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await list_pull_requests(token, owner=owner, repo=repo, state=state, per_page=per_page, page=page)


@router.get(
    "/{owner}/{repo}/{pr_number}",
    summary="Get Pull Request",
    description="Fetch a single pull request by its number.",
)
async def get_single_pr(
    owner: str,
    repo: str,
    pr_number: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await get_pull_request(token, owner=owner, repo=repo, pr_number=pr_number)


@router.post(
    "/{owner}/{repo}",
    summary="Create Pull Request",
    description="Open a new pull request in the specified repository.",
    status_code=201,
)
async def post_pr(
    owner: str,
    repo: str,
    payload: CreatePullRequestRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await create_pull_request(token, owner=owner, repo=repo, payload=payload)
