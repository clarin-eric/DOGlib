import json
from collections import namedtuple
import os
from typing import List, Any

from pid import PID, URL, HDL, DOI


class RegRepo:
    def __init__(self, name: str, host_name: str, host_netloc: str, hdl_id: str, doi_id: str, api: str, parser: dict):
        self.name: str = name
        self.host_name = host_name
        self.host_netloc = host_netloc
        self.api: str = api
        self.hdl_id: str = hdl_id
        self.doi_id: str = doi_id
        self.parser_type = parser['type']

    @staticmethod
    def config_decoder(json_dict: dict) -> Any:
        return namedtuple('RegRepo', json_dict.keys())(*json_dict.values())

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Host name: {self.host_name}\n" \
               f"Host netloc: {self.host_netloc}"

    def fetch(self, pid: PID):
        pid.to_url()

    def match(self, pid: PID) -> bool:
        if pid.pid_type() == HDL:
            return self.hdl_id == pid.pid.repo_id
        elif pid.pid_type() == URL:
            return self.host_name == pid.pid.host_name
        elif pid.pid_type() == DOI:
            return self.doi_id == pid.pid.repo_id
        else:
            return False


def load_repos(configs_dir: str= "./repo_configs") -> List[RegRepo]:
    repos: List[RegRepo] = []
    if not os.path.exists(configs_dir):
        raise FileNotFoundError(f"Config dir {configs_dir} does not exist")
    for config_file in os.listdir(configs_dir):
        if not config_file.endswith(".json"):
            continue
        with open(config_file) as cfile:
            repos.append(json.load(cfile, object_hook=RegRepo.config_decoder))
    return repos
