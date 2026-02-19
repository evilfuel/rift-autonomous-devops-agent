from fastapi import FastAPI
from pydantic import BaseModel

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
    return {
        "repository": data.repo_url,
        "branch": "TEMP_BRANCH",
        "total_failures": 0,
        "total_fixes": 0,
        "iterations": 0,
        "final_status": "PASSED",
        "time_taken": "0m 10s",
        "score": 100,
        "fixes": [],
        "timeline": []
    }

