from dotenv import load_dotenv
load_dotenv()  # Load .env file if present (e.g. for GITHUB_TOKEN)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import repos, issues, commits, pull_requests, auth

app = FastAPI(
    title="GitHub Cloud Connector",
    description="A cloud connector for interacting with the GitHub API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(repos.router, prefix="/repos", tags=["Repositories"])
app.include_router(issues.router, prefix="/issues", tags=["Issues"])
app.include_router(commits.router, prefix="/commits", tags=["Commits"])
app.include_router(pull_requests.router, prefix="/pull-requests", tags=["Pull Requests"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "GitHub Cloud Connector",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
