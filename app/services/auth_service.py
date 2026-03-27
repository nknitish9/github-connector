from app.core.github_client import github_request


async def get_authenticated_user(token: str) -> dict:
    """Retrieve the authenticated user's GitHub profile."""
    return await github_request("GET", "/user", token)


async def verify_token(token: str) -> dict:
    """
    Verify a GitHub PAT by hitting /user.
    Returns a summary of the authenticated user.
    """
    user = await get_authenticated_user(token)
    return {
        "valid": True,
        "login": user.get("login"),
        "name": user.get("name"),
        "email": user.get("email"),
        "public_repos": user.get("public_repos"),
        "plan": user.get("plan", {}).get("name") if user.get("plan") else None,
    }
