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