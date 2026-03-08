import base64
import random
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mock GitHub API")

# Generate 16 dummy applications
ORG_NAME = "test-org"
APPS = [f"dummy-app-{i:02d}" for i in range(1, 17)]
MOCK_FILE_CONTENT = """replicaCount: 2
image:
  tag: "1.0.0"
autoscaling:
  minReplicas: 1
  maxReplicas: 3
ingress:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
"""

class CommitRequest(BaseModel):
    message: str
    content: str
    branch: str
    sha: str | None = None

class PullRequest(BaseModel):
    title: str
    body: str
    head: str
    base: str

class ReviewersRequest(BaseModel):
    reviewers: list[str]

@app.get("/orgs/{org}/repos")
async def list_repos(org: str, page: int = 1):
    if org != ORG_NAME:
        return []
    
    if page > 1:
        return []
        
    return [
        {
            "name": app_name,
            "full_name": f"{org}/{app_name}",
            "default_branch": "main"
        }
        for app_name in APPS
    ]

@app.get("/repos/{owner}/{repo}/contents/{path:path}")
async def get_file_content(owner: str, repo: str, path: str, ref: str = "main"):
    if repo not in APPS:
        raise HTTPException(status_code=404, detail="Repo not found")
        
    encoded = base64.b64encode(MOCK_FILE_CONTENT.encode()).decode()
    return {
        "content": encoded,
        "encoding": "base64",
        "sha": f"mock-sha-{random.randint(1000, 9999)}"
    }

@app.get("/repos/{owner}/{repo}/git/ref/heads/{branch}")
async def get_branch_ref(owner: str, repo: str, branch: str):
    return {
        "object": {
            "sha": f"mock-branch-sha-{random.randint(1000, 9999)}"
        }
    }

@app.post("/repos/{owner}/{repo}/git/refs")
async def create_branch(owner: str, repo: str, request: Request):
    payload = await request.json()
    # Mock successful branch creation
    return payload

@app.put("/repos/{owner}/{repo}/contents/{path:path}")
async def commit_file(owner: str, repo: str, path: str, commit: CommitRequest):
    return {
        "content": {
            "name": path,
            "path": path,
            "sha": f"new-file-sha-{random.randint(1000, 9999)}"
        },
        "commit": {
            "sha": f"new-commit-sha-{random.randint(1000, 9999)}"
        }
    }

@app.post("/repos/{owner}/{repo}/pulls")
async def create_pull_request(owner: str, repo: str, pr: PullRequest):
    pr_number = random.randint(100, 999)
    return {
        "number": pr_number,
        "html_url": f"https://github.com/{owner}/{repo}/pull/{pr_number}",
        "title": pr.title,
        "state": "open"
    }

@app.post("/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers")
async def request_reviewers(owner: str, repo: str, pull_number: int, req: ReviewersRequest):
    return {
        "html_url": f"https://github.com/{owner}/{repo}/pull/{pull_number}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
