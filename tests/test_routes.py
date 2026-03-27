"""
Tests for the GitHub Cloud Connector.

Uses pytest + httpx AsyncClient with mocked GitHub API responses.
Run with: pytest tests/ -v
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app

AUTH_HEADER = {"Authorization": "Bearer ghp_test_token_123"}

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Health ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "GitHub Cloud Connector"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ── Auth ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_verify_token(client):
    mock_user = {
        "login": "octocat",
        "name": "The Octocat",
        "email": "octocat@github.com",
        "public_repos": 8,
        "plan": {"name": "pro"},
    }
    with patch("app.services.auth_service.github_request", new=AsyncMock(return_value=mock_user)):
        response = await client.get("/auth/verify", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["login"] == "octocat"
    assert data["plan"] == "pro"


@pytest.mark.asyncio
async def test_get_me(client):
    mock_user = {"login": "octocat", "name": "The Octocat", "public_repos": 8}
    with patch("app.services.auth_service.github_request", new=AsyncMock(return_value=mock_user)):
        response = await client.get("/auth/me", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["login"] == "octocat"


@pytest.mark.asyncio
async def test_missing_auth_token(client):
    with patch("app.core.github_client.os.getenv", return_value=None):
        response = await client.get("/auth/verify")
    assert response.status_code == 401


# ── Repositories ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_user_repos(client):
    mock_repos = [
        {"id": 1, "name": "hello-world", "full_name": "octocat/hello-world", "private": False},
        {"id": 2, "name": "Spoon-Knife", "full_name": "octocat/Spoon-Knife", "private": False},
    ]
    with patch("app.services.repo_service.github_request", new=AsyncMock(return_value=mock_repos)):
        response = await client.get("/repos/user/octocat", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "hello-world"


@pytest.mark.asyncio
async def test_get_repo(client):
    mock_repo = {
        "id": 1296269,
        "name": "Hello-World",
        "full_name": "octocat/Hello-World",
        "private": False,
        "stargazers_count": 80,
    }
    with patch("app.services.repo_service.github_request", new=AsyncMock(return_value=mock_repo)):
        response = await client.get("/repos/octocat/Hello-World", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["full_name"] == "octocat/Hello-World"


@pytest.mark.asyncio
async def test_list_my_repos(client):
    mock_repos = [{"id": 1, "name": "private-repo", "private": True}]
    with patch("app.services.repo_service.github_request", new=AsyncMock(return_value=mock_repos)):
        response = await client.get("/repos/me", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()[0]["name"] == "private-repo"


# ── Issues ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_issues(client):
    mock_issues = [
        {"id": 1, "number": 1, "title": "Found a bug", "state": "open"},
        {"id": 2, "number": 2, "title": "Feature request", "state": "open"},
    ]
    with patch("app.services.issue_service.github_request", new=AsyncMock(return_value=mock_issues)):
        response = await client.get("/issues/octocat/Hello-World", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_issues_excludes_prs(client):
    """Pull requests returned by GitHub's /issues endpoint must be filtered out."""
    mock_response = [
        {"id": 1, "number": 1, "title": "Real issue", "state": "open"},
        {"id": 2, "number": 2, "title": "A PR", "state": "open", "pull_request": {"url": "..."}},
    ]
    with patch("app.services.issue_service.github_request", new=AsyncMock(return_value=mock_response)):
        response = await client.get("/issues/octocat/Hello-World", headers=AUTH_HEADER)
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Real issue"


@pytest.mark.asyncio
async def test_create_issue(client):
    mock_issue = {
        "id": 1,
        "number": 42,
        "title": "Bug: crash on login",
        "state": "open",
        "html_url": "https://github.com/octocat/Hello-World/issues/42",
    }
    with patch("app.services.issue_service.github_request", new=AsyncMock(return_value=mock_issue)):
        response = await client.post(
            "/issues/octocat/Hello-World",
            headers=AUTH_HEADER,
            json={"title": "Bug: crash on login", "body": "Steps to reproduce..."},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == 42
    assert data["title"] == "Bug: crash on login"


@pytest.mark.asyncio
async def test_create_issue_missing_title(client):
    response = await client.post(
        "/issues/octocat/Hello-World",
        headers=AUTH_HEADER,
        json={"body": "No title provided"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_single_issue(client):
    mock_issue = {"id": 1, "number": 1, "title": "Found a bug", "state": "open"}
    with patch("app.services.issue_service.github_request", new=AsyncMock(return_value=mock_issue)):
        response = await client.get("/issues/octocat/Hello-World/1", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["number"] == 1


@pytest.mark.asyncio
async def test_close_issue(client):
    mock_issue = {"id": 1, "number": 1, "title": "Found a bug", "state": "closed"}
    with patch("app.services.issue_service.github_request", new=AsyncMock(return_value=mock_issue)):
        response = await client.patch("/issues/octocat/Hello-World/1/close", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["state"] == "closed"


# ── Commits ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_commits(client):
    mock_commits = [
        {"sha": "abc123", "commit": {"message": "Initial commit"}},
        {"sha": "def456", "commit": {"message": "Add README"}},
    ]
    with patch("app.services.commit_service.github_request", new=AsyncMock(return_value=mock_commits)):
        response = await client.get("/commits/octocat/Hello-World", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["sha"] == "abc123"


@pytest.mark.asyncio
async def test_list_commits_with_branch(client):
    mock_commits = [{"sha": "abc123", "commit": {"message": "Feature commit"}}]
    with patch("app.services.commit_service.github_request", new=AsyncMock(return_value=mock_commits)):
        response = await client.get(
            "/commits/octocat/Hello-World?branch=feature/my-branch", headers=AUTH_HEADER
        )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_single_commit(client):
    mock_commit = {
        "sha": "abc123def456",
        "commit": {"message": "Fix critical bug", "author": {"name": "Octocat"}},
    }
    with patch("app.services.commit_service.github_request", new=AsyncMock(return_value=mock_commit)):
        response = await client.get("/commits/octocat/Hello-World/abc123def456", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["sha"] == "abc123def456"


# ── Pull Requests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_pull_requests(client):
    mock_prs = [
        {"id": 1, "number": 1, "title": "Fix login bug", "state": "open"},
    ]
    with patch("app.services.pr_service.github_request", new=AsyncMock(return_value=mock_prs)):
        response = await client.get("/pull-requests/octocat/Hello-World", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Fix login bug"


@pytest.mark.asyncio
async def test_create_pull_request(client):
    mock_pr = {
        "id": 1,
        "number": 10,
        "title": "feat: add dark mode",
        "state": "open",
        "html_url": "https://github.com/octocat/Hello-World/pull/10",
    }
    with patch("app.services.pr_service.github_request", new=AsyncMock(return_value=mock_pr)):
        response = await client.post(
            "/pull-requests/octocat/Hello-World",
            headers=AUTH_HEADER,
            json={
                "title": "feat: add dark mode",
                "head": "feature/dark-mode",
                "base": "main",
                "body": "Adds dark mode support.",
                "draft": False,
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == 10
    assert data["title"] == "feat: add dark mode"


@pytest.mark.asyncio
async def test_create_pr_missing_head(client):
    response = await client.post(
        "/pull-requests/octocat/Hello-World",
        headers=AUTH_HEADER,
        json={"title": "PR without head", "base": "main"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_single_pr(client):
    mock_pr = {"id": 1, "number": 1, "title": "Fix login bug", "state": "open"}
    with patch("app.services.pr_service.github_request", new=AsyncMock(return_value=mock_pr)):
        response = await client.get("/pull-requests/octocat/Hello-World/1", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["number"] == 1
