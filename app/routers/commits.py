from fastapi import APIRouter, Security, Query
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional

from app.core.github_client import security, get_token
from app.services.commit_service import list_commits, get_commit

router = APIRouter()


@router.get(
    "/{owner}/{repo}",
    summary="List Commits",
    description="Fetch commits from a repository, optionally filtered by branch.",
)
async def get_commits(
    owner: str,
    repo: str,
    branch: Optional[str] = Query(None, description="Branch name or SHA (defaults to default branch)"),
    per_page: int = Query(30, ge=1, le=100),
    page: int = Query(1, ge=1),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await list_commits(token, owner=owner, repo=repo, branch=branch, per_page=per_page, page=page)


@router.get(
    "/{owner}/{repo}/{sha}",
    summary="Get Commit",
    description="Fetch details of a specific commit by its SHA.",
)
async def get_single_commit(
    owner: str,
    repo: str,
    sha: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = get_token(credentials)
    return await get_commit(token, owner=owner, repo=repo, sha=sha)
