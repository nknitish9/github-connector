from pydantic import BaseModel, Field
from typing import Optional


# ── Issues ───────────────────────────────────────────────────────────────────

class CreateIssueRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="Issue title")
    body: Optional[str] = Field(None, description="Issue body / description")
    labels: Optional[list[str]] = Field(default=[], description="List of label names")
    assignees: Optional[list[str]] = Field(default=[], description="GitHub usernames to assign")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Bug: login page crashes on mobile",
                "body": "Steps to reproduce...",
                "labels": ["bug"],
                "assignees": [],
            }
        }
    }


# ── Pull Requests ─────────────────────────────────────────────────────────────

class CreatePullRequestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="PR title")
    head: str = Field(..., description="Branch containing changes (e.g. 'feature/my-branch')")
    base: str = Field(..., description="Branch to merge into (e.g. 'main')")
    body: Optional[str] = Field(None, description="PR description")
    draft: bool = Field(False, description="Open as draft PR")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "feat: add login page",
                "head": "feature/login-page",
                "base": "main",
                "body": "## Summary\nAdds a login page.",
                "draft": False,
            }
        }
    }


# ── Common ────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
