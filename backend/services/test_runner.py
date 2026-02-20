import subprocess
import os
import re


def run_tests(repo_path: str):
    try:
        result = subprocess.run(
            ["pytest"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr

        # If no tests exist, treat as success
        if "no tests ran" in output.lower():
            return {
                "success": True,
                "failures": []
            }

        # If tests passed
        if result.returncode == 0:
            return {
                "success": True,
                "failures": []
            }

        # Otherwise extract real failure
        failures = extract_failures(output, repo_path)

        return {
            "success": False,
            "failures": failures if failures else [{
                "file": "unknown",
                "line": 0,
                "error": output
            }]
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


def extract_failures(output: str, clone_path: str):
    failures = []

    # If assertion failure happened
    if "AssertionError" in output:

        # Try to detect imported module name from test file
        match = re.search(r'from (\w+) import', output)

        if match:
            module_name = match.group(1)
            file_name = module_name + ".py"
        else:
            # fallback
            file_name = "calculator.py"

        failures.append({
            "file": file_name,
            "line": 0,
            "error": output
        })

    return failures