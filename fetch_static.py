import argparse
import os
import pycurl
import traceback

from doglib import DOG, REPO_CONFIG_DIR, STATIC_TEST_FILES_DIR
from doglib import curl, pid_factory


parser = argparse.ArgumentParser(description='Fetch PID responses and save them to static.')
parser.add_argument('--local',
                    action="store_true",
                    help="If passed fetches static files into repo dir, otherwise into DOGlib install location")

parser.set_defaults(feature=False)
args = parser.parse_args()

if args.local:
    STATIC_TEST_FILES_DIR = "./doglib/static/"


def fetch_static_test_examples():
    dog = DOG()
    secrets = dog.secrets
    repos = DOG.load_repos(REPO_CONFIG_DIR)
    for idx, repo in enumerate(repos):
        print(f"Processing {repo.name} ({idx+1}/{len(repos)}")
        test_examples = repo.get_test_examples()
        repo_id = repo.id
        if not os.path.exists(f"{STATIC_TEST_FILES_DIR}/{repo_id}"):
            os.makedirs(f"{STATIC_TEST_FILES_DIR}/{repo_id}")
        for pid_type, test_pid in test_examples.items():
            if test_pid:
                print(f"Fetching {pid_type} response")
                fetch_static_test_example(repo, pid_type, test_pid, secrets)


def fetch_static_test_example(repo, pid_type, test_pid, secrets):
    repo_id = repo.id
    test_pid = pid_factory(test_pid)
    with open(f"{STATIC_TEST_FILES_DIR}/{repo_id}/{pid_type}", "w") as pid_response:
        try:
            target_url = repo.get_request_url(test_pid, secrets)
            headers = repo.get_headers(test_pid)
            effective_url, decoded_body, decoded_response = curl.get(target_url, headers, follow_redirects=True)
            pid_response.write(decoded_body)
        except pycurl.error as e:
            print(traceback.format_exc())


if __name__ == "__main__":
    fetch_static_test_examples()