import subprocess
import re
import os


def run_tests(repo_path: str):
    try:
        result = subprocess.run(
            ["pytest"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr

        # 🔥 Simple logic: failure if returncode != 0
        if result.returncode != 0:
                            failures = [{
            "file": "calculator.py",
            "line": 0,
            "error": output
        }]


        else:
            failures = []

        return {
            "success": result.returncode == 0,
            "failures": failures
        }

    except Exception as e:
        return {
            "success": False,
            "failures": [{
                "file": "unknown",
                "line": 0,
                "error": str(e)
            }]
        }

def extract_failures(output, clone_path):
    failures = []

    # If pytest failed at all, assume test file is failing
    if "FAILED" in output or "AssertionError" in output:
        # Find first test file in repo
        for root, dirs, files in os.walk(clone_path):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    failures.append({
                        "file": file,
                        "line": 0,
                        "error": "test failure"
                    })
                    return failures

    return failures


