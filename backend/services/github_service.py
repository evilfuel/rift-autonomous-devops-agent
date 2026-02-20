import os
from git import Repo
import subprocess

BASE_CLONE_PATH = "temp_repos"

def clone_repository(repo_url: str, branch_name: str):
    os.makedirs(BASE_CLONE_PATH, exist_ok=True)

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    clone_path = os.path.join(BASE_CLONE_PATH, repo_name)

    # If repo already exists, remove it (fresh run each time)
    if os.path.exists(clone_path):
        import shutil
        shutil.rmtree(clone_path)

    repo = Repo.clone_from(repo_url, clone_path)

    # Create new branch
    new_branch = repo.create_head(branch_name)
    repo.head.reference = new_branch
    repo.head.reset(index=True, working_tree=True)

    return clone_path

def commit_and_push(repo_path: str, branch_name: str):
    subprocess.run(["git", "add", "."], cwd=repo_path)

    subprocess.run(
        ["git", "commit", "-m", "[AI-AGENT] Auto-fix applied"],
        cwd=repo_path
    )

    subprocess.run(
        ["git", "push", "origin", branch_name],
        cwd=repo_path
    ) 

import requests
import os
from git import Repo


def create_new_repo(repo_name: str):
    token = os.getenv("GITHUB_TOKEN")

    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"token {token}"
    }

    data = {
        "name": repo_name,
        "private": False
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()["clone_url"] 

def push_fixed_repo(local_path: str, new_repo_url: str):
    repo = Repo(local_path)

    repo.git.remote("remove", "origin")
    repo.create_remote("origin", new_repo_url)

    repo.git.add(A=True)
    repo.index.commit("AI Fixed Code")

    repo.git.push("--set-upstream", "origin", "main")