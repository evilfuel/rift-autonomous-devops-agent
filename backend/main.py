from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from services.github_service import create_new_repo, push_fixed_repo


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")
from fastapi.middleware.cors import CORSMiddleware

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
    # Create new repo and push fixed code
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
    return {
        "repository": data.repo_url,
        "branch": branch_name,
        "total_failures": len(test_result["failures"]),
        "total_fixes": fix_count,
        "iterations": 1,
        "final_status": final_status,
        "time_taken": "0m 10s",
        "score": 100,
        "new_repo": new_repo_url,   # 👈 ADD IT HERE
        "fixes": test_result["failures"],
        "timeline": [
            {
                "iteration": 1,
                "status": final_status,
                "timestamp": "NOW"
        }
    ]
}

