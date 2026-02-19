from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel
from utils.formatter import generate_branch_name
from services.github_service import clone_repository
from services.test_runner import run_tests
from services.fixer import apply_simple_fix
from services.github_service import commit_and_push
from services.test_runner import run_tests, extract_failures
import os
from services.ai_fixer import generate_fix


app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str

@app.get("/")
def root():
    return {"message": "Backend is running"}

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

        # Only attempt first failure to save quota
        failure = failures[0]

        file_path = os.path.abspath(
            os.path.join(clone_path, failure["file"])
        )

        # Ignore anything outside repo
        if clone_path not in file_path:
            break

        # Ignore venv / site-packages
        if "site-packages" in file_path or "venv" in file_path:
            break

        if not os.path.exists(file_path):
            break

        with open(file_path, "r") as f:
            content = f.read()

        fixed_content = generate_fix(content, failure["error"])

        # Only overwrite if AI returned valid python
        if fixed_content and "def " in fixed_content:
            with open(file_path, "w") as f:
                f.write(fixed_content)
            fix_count += 1
        else:
            break

        # Re-run tests after fix
        test_result = run_tests(clone_path)

    final_status = "PASSED" if test_result["success"] else "FAILED"

    return {
        "repository": data.repo_url,
        "branch": branch_name,
        "total_failures": len(test_result["failures"]),
        "total_fixes": fix_count,
        "iterations": iterations,
        "final_status": final_status,
        "time_taken": "0m 10s",
        "score": 100,
        "fixes": test_result["failures"],
        "timeline": [
            {
                "iteration": iterations,
                "status": final_status,
                "timestamp": "NOW"
            }
        ]
    }

