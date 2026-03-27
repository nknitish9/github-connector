# GitHub Cloud Connector

A clean, modular REST API connector for GitHub built with **Python** and **FastAPI**. Supports Personal Access Token (PAT) authentication and exposes a full suite of actions across repositories, issues, commits, and pull requests.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Server](#running-the-server)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health](#health)
  - [Auth](#auth)
  - [Repositories](#repositories)
  - [Issues](#issues)
  - [Commits](#commits)
  - [Pull Requests](#pull-requests)
- [Example Requests](#example-requests)
- [Running Tests](#running-tests)
- [Design Decisions](#design-decisions)

---

## Features

| Category         | Actions                                                          |
|------------------|------------------------------------------------------------------|
| Authentication   | Verify PAT, fetch authenticated user profile                     |
| Repositories     | List user/org repos, get a specific repo, list own private repos |
| Issues           | List, get, create, close issues                                  |
| Commits          | List commits (with branch filter), get a single commit           |
| Pull Requests    | List, get, create pull requests *(bonus)*                        |

---

## Project Structure

```
github-connector/
├── app/
│   ├── main.py               # FastAPI app + router registration
│   ├── core/
│   │   └── github_client.py  # HTTP client, auth extraction, error handling
│   ├── models/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── routers/
│   │   ├── auth.py           # /auth endpoints
│   │   ├── repos.py          # /repos endpoints
│   │   ├── issues.py         # /issues endpoints
│   │   ├── commits.py        # /commits endpoints
│   │   └── pull_requests.py  # /pull-requests endpoints
│   └── services/
│       ├── auth_service.py   # GitHub auth logic
│       ├── repo_service.py   # Repository actions
│       ├── issue_service.py  # Issue actions
│       ├── commit_service.py # Commit actions
│       └── pr_service.py     # Pull request actions
├── tests/
│   └── test_routes.py        # Full async test suite (mocked)
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.11 or higher
- A GitHub account with a [Personal Access Token](https://github.com/settings/tokens)

### 1. Clone the repository

```bash
git clone https://github.com/nknitish9/github-connector.git
cd github-connector
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your GitHub token

```bash
cp .env.example .env
# Edit .env and set GITHUB_TOKEN=ghp_your_token_here
```

> **Required PAT scopes:** `repo`, `read:org`, `read:user`  
> Generate a token at: https://github.com/settings/tokens

---

## Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

| URL                              | Description              |
|----------------------------------|--------------------------|
| http://localhost:8000            | Root / service info      |
| http://localhost:8000/docs       | Swagger UI (interactive) |
| http://localhost:8000/redoc      | ReDoc documentation      |

---

## Authentication

The connector uses **Bearer Token authentication** via the HTTP `Authorization` header.

Pass your GitHub PAT on every request:

```
Authorization: Bearer ghp_your_personal_access_token
```

Tokens are never stored server-side — they flow through per-request as a header and are forwarded directly to GitHub. Nothing is hardcoded.

---

## API Endpoints

### Health

| Method | Path      | Description         |
|--------|-----------|---------------------|
| GET    | `/`       | Service info        |
| GET    | `/health` | Health check        |

---

### Auth

| Method | Path            | Description                              |
|--------|-----------------|------------------------------------------|
| GET    | `/auth/verify`  | Validate token and return user summary   |
| GET    | `/auth/me`      | Full GitHub profile of the authed user   |

---

### Repositories

| Method | Path                      | Description                              |
|--------|---------------------------|------------------------------------------|
| GET    | `/repos/me`               | Repos belonging to the authed user       |
| GET    | `/repos/user/{username}`  | Public repos for any GitHub user         |
| GET    | `/repos/org/{org}`        | Repos for a GitHub organization          |
| GET    | `/repos/{owner}/{repo}`   | Details of a specific repository         |

**Query parameters (list endpoints):**

| Param      | Default | Description                  |
|------------|---------|------------------------------|
| `per_page` | 30      | Results per page (max 100)   |
| `page`     | 1       | Page number                  |

---

### Issues

| Method | Path                                     | Description              |
|--------|------------------------------------------|--------------------------|
| GET    | `/issues/{owner}/{repo}`                 | List issues (no PRs)     |
| GET    | `/issues/{owner}/{repo}/{issue_number}`  | Get a single issue       |
| POST   | `/issues/{owner}/{repo}`                 | Create a new issue       |
| PATCH  | `/issues/{owner}/{repo}/{number}/close`  | Close an issue           |

**List query parameters:**

| Param      | Default | Options                  |
|------------|---------|--------------------------|
| `state`    | `open`  | `open`, `closed`, `all`  |
| `per_page` | 30      | 1–100                    |
| `page`     | 1       | ≥1                       |

**Create issue body:**

```json
{
  "title": "Bug: login page crashes on mobile",
  "body": "Steps to reproduce...",
  "labels": ["bug"],
  "assignees": ["octocat"]
}
```

---

### Commits

| Method | Path                              | Description              |
|--------|-----------------------------------|--------------------------|
| GET    | `/commits/{owner}/{repo}`         | List commits             |
| GET    | `/commits/{owner}/{repo}/{sha}`   | Get a specific commit    |

**List query parameters:**

| Param      | Default         | Description                              |
|------------|-----------------|------------------------------------------|
| `branch`   | default branch  | Branch name or SHA to filter by          |
| `per_page` | 30              | Results per page (max 100)               |
| `page`     | 1               | Page number                              |

---

### Pull Requests

| Method | Path                                 | Description              |
|--------|--------------------------------------|--------------------------|
| GET    | `/pull-requests/{owner}/{repo}`      | List pull requests       |
| GET    | `/pull-requests/{owner}/{repo}/{n}`  | Get a single PR          |
| POST   | `/pull-requests/{owner}/{repo}`      | Create a pull request    |

**Create PR body:**

```json
{
  "title": "feat: add dark mode",
  "head": "feature/dark-mode",
  "base": "main",
  "body": "## Summary\nAdds dark mode support.",
  "draft": false
}
```

---

## Example Requests

All examples use `curl`. Replace `<YOUR_TOKEN>` with your GitHub PAT.

```bash
# Verify your token
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     http://localhost:8000/auth/verify

# List your own repos
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     http://localhost:8000/repos/me

# List public repos for a user
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     http://localhost:8000/repos/user/octocat

# Get a specific repo
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     http://localhost:8000/repos/octocat/Hello-World

# List open issues
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     "http://localhost:8000/issues/octocat/Hello-World?state=open"

# Create an issue
curl -X POST \
     -H "Authorization: Bearer <YOUR_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Found a bug", "body": "Details here...", "labels": ["bug"]}' \
     http://localhost:8000/issues/octocat/Hello-World

# Close an issue
curl -X PATCH \
     -H "Authorization: Bearer <YOUR_TOKEN>" \
     http://localhost:8000/issues/octocat/Hello-World/1/close

# List commits on a specific branch
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     "http://localhost:8000/commits/octocat/Hello-World?branch=main"

# Create a pull request
curl -X POST \
     -H "Authorization: Bearer <YOUR_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "feat: new feature", "head": "feature/my-branch", "base": "main"}' \
     http://localhost:8000/pull-requests/octocat/Hello-World
```

---

## Running Tests

The test suite uses `pytest` with `pytest-asyncio` and mocks all GitHub API calls so no real token or network access is needed.

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_routes.py::test_root                        PASSED
tests/test_routes.py::test_health                      PASSED
tests/test_routes.py::test_verify_token                PASSED
tests/test_routes.py::test_get_me                      PASSED
tests/test_routes.py::test_missing_auth_token          PASSED
tests/test_routes.py::test_list_user_repos             PASSED
tests/test_routes.py::test_get_repo                    PASSED
tests/test_routes.py::test_list_my_repos               PASSED
tests/test_routes.py::test_list_issues                 PASSED
tests/test_routes.py::test_list_issues_excludes_prs    PASSED
tests/test_routes.py::test_create_issue                PASSED
tests/test_routes.py::test_create_issue_missing_title  PASSED
tests/test_routes.py::test_get_single_issue            PASSED
tests/test_routes.py::test_close_issue                 PASSED
tests/test_routes.py::test_list_commits                PASSED
tests/test_routes.py::test_list_commits_with_branch    PASSED
tests/test_routes.py::test_get_single_commit           PASSED
tests/test_routes.py::test_list_pull_requests          PASSED
tests/test_routes.py::test_create_pull_request         PASSED
tests/test_routes.py::test_create_pr_missing_head      PASSED
tests/test_routes.py::test_get_single_pr               PASSED

21 passed in 1.23s
```

---

## Design Decisions

**Layered architecture** — Routers handle HTTP concerns only. Business logic lives in services. The GitHub HTTP client is isolated in `core/`, making it trivial to swap the transport layer.

**Token security** — Tokens are passed per-request as Bearer headers and forwarded directly to GitHub. Nothing is persisted or logged.

**Error handling** — The GitHub client maps every non-2xx HTTP status (401, 403, 404, 422, 5xx) to a typed `HTTPException` with a clear message. FastAPI serialises these automatically to JSON.

**PR filtering on issues** — GitHub's `/issues` endpoint returns pull requests too. The connector filters them out transparently so callers always receive only real issues.

**Async throughout** — All I/O uses `httpx.AsyncClient` and FastAPI's async handlers, keeping the server non-blocking under load.

**Input validation** — Pydantic models enforce required fields and length constraints before any network call is made, returning 422 with structured errors on bad input.
