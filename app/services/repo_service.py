from app.core.github_client import github_request


async def list_user_repos(token: str, username: str, per_page: int, page: int) -> list:
    """Fetch public repositories for a given GitHub user."""
    params = {"per_page": per_page, "page": page, "sort": "updated", "direction": "desc"}
    return await github_request("GET", f"/users/{username}/repos", token, params=params)


async def list_org_repos(token: str, org: str, per_page: int, page: int) -> list:
    """Fetch repositories for a GitHub organization."""
    params = {"per_page": per_page, "page": page, "sort": "updated", "direction": "desc"}
    return await github_request("GET", f"/orgs/{org}/repos", token, params=params)


async def get_repo(token: str, owner: str, repo: str) -> dict:
    """Fetch details of a specific repository."""
    return await github_request("GET", f"/repos/{owner}/{repo}", token)


async def list_authenticated_user_repos(token: str, per_page: int, page: int) -> list:
    """Fetch repositories belonging to the authenticated user (includes private)."""
    params = {"per_page": per_page, "page": page, "sort": "updated", "affiliation": "owner"}
    return await github_request("GET", "/user/repos", token, params=params)
