from fastapi import APIRouter, Security, Query
from fastapi.security import HTTPAuthorizationCredentials
from typing import Literal

from app.core.github_client import security, get_token
from app.models.schemas import CreateIssueRequest
from app.services.issue_service import list_issues, get_issue, create_issue, close_issue

router = APIRouter()


@router.get(
    "/{owner}/{repo}",
    summary="List Issues",
    description="List issues for a repository. Pull requests are excluded.",
)
async def get_issues(
    owner: str,
    repo: str,
    state: Literal["open", "closed", "all"] = Query("open", description="Filter by issue state"),
    per_page: int = Query(30, ge=1, le=100),
    page: int = Query(1, ge=1),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await list_issues(token, owner=owner, repo=repo, state=state, per_page=per_page, page=page)


@router.get(
    "/{owner}/{repo}/{issue_number}",
    summary="Get Issue",
    description="Fetch a single issue by its number.",
)
async def get_single_issue(
    owner: str,
    repo: str,
    issue_number: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await get_issue(token, owner=owner, repo=repo, issue_number=issue_number)


@router.post(
    "/{owner}/{repo}",
    summary="Create Issue",
    description="Create a new issue in the specified repository.",
    status_code=201,
)
async def post_issue(
    owner: str,
    repo: str,
    payload: CreateIssueRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await create_issue(token, owner=owner, repo=repo, payload=payload)


@router.patch(
    "/{owner}/{repo}/{issue_number}/close",
    summary="Close Issue",
    description="Close an existing issue.",
)
async def patch_close_issue(
    owner: str,
    repo: str,
    issue_number: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await close_issue(token, owner=owner, repo=repo, issue_number=issue_number)
