import re

def generate_branch_name(team_name: str, leader_name: str) -> str:
    team_clean = re.sub(r'[^A-Za-z0-9 ]+', '', team_name)
    leader_clean = re.sub(r'[^A-Za-z0-9 ]+', '', leader_name)

    team_clean = team_clean.strip().replace(" ", "_")
    leader_clean = leader_clean.strip().replace(" ", "_")

    branch_name = f"{team_clean}_{leader_clean}_AI_Fix"
    return branch_name.upper()
