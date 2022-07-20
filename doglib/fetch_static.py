import os

from .curl import get
from .doglib import DOG, REPO_CONFIG_DIR


def fetch_static_test_examples():
    repos = DOG.load_repos(REPO_CONFIG_DIR)
    for repo in repos:
        repo_name = repo.name
        test_examples = repo.get_test_examples()
        os.mkdir(f"./static/testing/{repo_name}")
        for type_pid, test_pid in test_examples:
            if test_pid is not None:
                with open(f"/static/testing/{repo_name}/{test_pid}") as pid_response:
                    effective_url, decoded_body, decoded_response = get(test_pid,
                                                                        repo.get_headers(test_pid),
                                                                        follow_redirects=True)
                    pid_response.write(decoded_body)