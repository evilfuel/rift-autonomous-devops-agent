import os

def apply_simple_fix(repo_path: str, failures: list):
    fixes_applied = []

    for failure in failures:
        file_path = os.path.join(repo_path, failure["file"])

        if not os.path.exists(file_path):
            continue

        with open(file_path, "r") as f:
            lines = f.readlines()

        line_index = failure["line"] - 1

        # Simple demo fix logic
        if "-" in lines[line_index]:
            lines[line_index] = lines[line_index].replace("-", "+")

            with open(file_path, "w") as f:
                f.writelines(lines)

            fixes_applied.append({
                "file": failure["file"],
                "line": failure["line"],
                "status": "✓ Fixed"
            })

    return fixes_applied
