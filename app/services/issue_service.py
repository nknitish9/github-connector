from app.core.github_client import github_request
from app.models.schemas import CreateIssueRequest


async def list_issues(
    token: str,
    owner: str,
    repo: str,
    state: str,
    per_page: int,
    page: int,
) -> list:
    """List issues for a repository (excludes pull requests)."""
    params = {"state": state, "per_page": per_page, "page": page}
    issues = await github_request("GET", f"/repos/{owner}/{repo}/issues", token, params=params)
    # GitHub issues endpoint also returns PRs; filter them out
    return [i for i in issues if "pull_request" not in i]


async def get_issue(token: str, owner: str, repo: str, issue_number: int) -> dict:
    """Fetch a single issue by number."""
    return await github_request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}", token)


async def create_issue(
    token: str,
    owner: str,
    repo: str,
    payload: CreateIssueRequest,
) -> dict:
    """Create a new issue in the specified repository."""
    body = {
        "title": payload.title,
        "body": payload.body,
        "labels": payload.labels,
        "assignees": payload.assignees,
    }
    # Remove None values to avoid GitHub API errors
    body = {k: v for k, v in body.items() if v is not None}
    return await github_request("POST", f"/repos/{owner}/{repo}/issues", token, json=body)


async def close_issue(token: str, owner: str, repo: str, issue_number: int) -> dict:
    """Close an existing issue."""
    return await github_request(
        "PATCH",
        f"/repos/{owner}/{repo}/issues/{issue_number}",
        token,
        json={"state": "closed"},
    )
