from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os

from utils.formatter import generate_branch_name
from services.github_service import clone_repository, create_new_repo, push_fixed_repo
from services.test_runner import run_tests
from services.ai_fixer import generate_fix


app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepoRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str


@app.post("/run-agent")
def run_agent(data: RepoRequest):

    branch_name = generate_branch_name(data.team_name, data.leader_name)
    clone_path = clone_repository(data.repo_url, branch_name)

    test_result = run_tests(clone_path)

    fix_count = 0
    iterations = 0
    max_iterations = 3

    while not test_result["success"] and iterations < max_iterations:

        iterations += 1
        failures = test_result["failures"]

        if not failures:
            break

        failure = failures[0]

        file_path = os.path.abspath(
            os.path.join(clone_path, failure["file"])
        )

        if not os.path.exists(file_path):
            break

        with open(file_path, "r") as f:
            content = f.read()

        fixed_content = generate_fix(content, failure["error"])

        if fixed_content:
            with open(file_path, "w") as f:
                f.write(fixed_content)
            fix_count += 1
        else:
            break

        test_result = run_tests(clone_path)

    final_status = "PASSED" if test_result["success"] else "FAILED"

    new_repo_name = f"{branch_name}_fixed"
    new_repo_url = create_new_repo(new_repo_name)
    push_fixed_repo(clone_path, new_repo_url)

    return {
        "repository": data.repo_url,
        "branch": branch_name,
        "total_failures": len(test_result["failures"]),
        "total_fixes": fix_count,
        "iterations": iterations,
        "final_status": final_status,
        "new_repo": new_repo_url,
        "fixes": test_result["failures"]
    }