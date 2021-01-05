from pid_types import DOI, URL
from repos import load_repos
from urllib.request import urlopen


def make_pid(input_string: str) -> object:
    pid_types: list = [DOI, URL]
    pid: object = None
    for pid_type in pid_types:
        # Try to make new instance of link type
        try:
            pid = pid_type(input_string)
        except ValueError:
            continue
        if pid:
            break
    if not pid:
        raise ValueError(f"Provided string {pid} is an invalid PID format")
    return pid


def match_pid(reg_repos: list, pid: object) -> object:
    for reg_repo in reg_repos:
        if reg_repo.match_pid(pid):
            return reg_repo
    return None


def load(input_string: str) -> dict:
    links = [DOI, URL]
    pid = make_pid(input_string)
    reg_repos = load_repos()
    repo = match_pid(reg_repos, pid)
    api_request = repo.request(pid)
    return urlopen(api_request)




