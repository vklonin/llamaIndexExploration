import re
from typing import List

import requests

def get_pull_request_diff(repo_owner, repo_name, pull_request_number, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    diff_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_request_number}"

    response = requests.get(diff_url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to retrieve pull request diff: {response.text}")

def split_diff_chunks(text: str) -> List[str]:
    pattern = r'diff --git'
    chunks = re.split(pattern, text)

    return chunks

def extract_diff_filename(chunk: str) -> str:

    lines = chunk.strip().split('\n')
    line =  lines[0] if lines else ""

    pattern = r'a/(.*?) b/'
    match = re.search(pattern, line)
    if match:
        return match.group(1)
    else:
        return ""

#
#
# pr = get_pull_request_diff("jdi-testing","jdi-light",5023,os.getenv("GITHUB_TOKEN"))
# print(pr)
