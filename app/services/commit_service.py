from app.core.github_client import github_request


async def list_commits(
    token: str,
    owner: str,
    repo: str,
    branch: str | None,
    per_page: int,
    page: int,
) -> list:
    """Fetch commits from a repository, optionally filtered by branch."""
    params: dict = {"per_page": per_page, "page": page}
    if branch:
        params["sha"] = branch
    return await github_request("GET", f"/repos/{owner}/{repo}/commits", token, params=params)


async def get_commit(token: str, owner: str, repo: str, sha: str) -> dict:
    """Fetch details of a specific commit by SHA."""
    return await github_request("GET", f"/repos/{owner}/{repo}/commits/{sha}", token)
