from pid import PID
from repos import load_repos, RegRepo
from pid import PID


def match(pid: PID, reg_repo: RegRepo) -> bool:
    return pid.match(reg_repo)

def dog_fetch(pid_string: str):
    pid = PID(pid_string)


