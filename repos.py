import json
from collections import namedtuple
import os
from typing import List


class RegRepo:
    def __init__(self, name: str, host_name: str, host_netloc: str, api: str):
        self.name: str = name
        self.host_name = host_name
        self.host_netloc = host_netloc
        self.api: str = api

    def __str__(self):
        return {cmember: eval("self." + cmember) for cmember in ["name", "host_name", "host_netloc", "api"]}

    def match_pid(self, pid: object) -> bool:
        return self.host_name == pid.host_name

    def request(self, pid: object) -> str:
        return self.api.replace('#RECORD_ID#', pid.record_id)

    @staticmethod
    def config_decoder(json_dict: dict) -> tuple:
        return namedtuple('RegRepo', json_dict.keys())(*json_dict.values())


def load_repos(configs_dir: str= "./repo_configs") -> List[RegRepo]:
    repos: List[RegRepo] = []
    if not os.path.exists(configs_dir):
        raise FileNotFoundError(f"Config dir {configs_dir} does not exist")
    for config_file in os.listdir(configs_dir):
        if not config_file.endswith(".json"):
            continue
        with open(config_file) as cfile:
            repos.append(json.load(cfile, object_hook=RegRepo.config_decoder()))
    return repos
