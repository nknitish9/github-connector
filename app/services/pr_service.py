from app.core.github_client import github_request
from app.models.schemas import CreatePullRequestRequest


async def list_pull_requests(
    token: str,
    owner: str,
    repo: str,
    state: str,
    per_page: int,
    page: int,
) -> list:
    """List pull requests for a repository."""
    params = {"state": state, "per_page": per_page, "page": page}
    return await github_request("GET", f"/repos/{owner}/{repo}/pulls", token, params=params)


async def get_pull_request(token: str, owner: str, repo: str, pr_number: int) -> dict:
    """Fetch a single pull request by number."""
    return await github_request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}", token)


async def create_pull_request(
    token: str,
    owner: str,
    repo: str,
    payload: CreatePullRequestRequest,
) -> dict:
    """Open a new pull request."""
    body = {
        "title": payload.title,
        "head": payload.head,
        "base": payload.base,
        "body": payload.body,
        "draft": payload.draft,
    }
    body = {k: v for k, v in body.items() if v is not None}
    return await github_request("POST", f"/repos/{owner}/{repo}/pulls", token, json=body)
