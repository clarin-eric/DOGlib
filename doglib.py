import json
from http.client import HTTPResponse
import os
import requests
from requests import Response
from typing import List, Union, Optional, Type
from urllib.parse import urlparse

from repos import RegRepo
from parsers import JSONParser, CMDIParser, Parser
from pid import PID


class DOG:
    def __init__(self):
        self.reg_repos: List[RegRepo] = self._load_repos()

    def _load_repos(self, config_dir: str = os.path.join(os.getcwd(), "repo_configs")) -> List[RegRepo]:
        reg_repos: List[RegRepo] = []
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Config dir {config_dir} does not exist")
        for config_file in os.listdir(config_dir):
            if config_file.endswith(".json"):
                with open(os.path.join(config_dir, config_file)) as cfile:
                    repo_config: dict = json.load(cfile)["repository"]
                    reg_repo: RegRepo = RegRepo(repo_config)
                    reg_repos.append(reg_repo)
        return reg_repos

    def _match(self, pid: PID) -> Optional[RegRepo]:
        for reg_repo in self.reg_repos:
            if reg_repo.match_pid(pid):
                return reg_repo
        return None

    def _make_parser(self, parser_type: str, parser_config: dict):
        if parser_type == "json":
            return JSONParser(parser_config)
        else:
            return CMDIParser()

    def sniff(self, pid_string: str) -> Optional[list]:
        pid = PID(pid_string)
        matching_repo = self._match(pid)
        if not matching_repo:
            return None
        else:
            print(matching_repo)
            matched_repo_entry_url: str = matching_repo.request_url(pid)
            print(matched_repo_entry_url)
            if not urlparse(matched_repo_entry_url).scheme:
                matched_repo_entry_url = 'http://' + matched_repo_entry_url
            response: Response = requests.get(matched_repo_entry_url)
            parser: Union[JSONParser, CMDIParser] = self._make_parser(matching_repo.get_parser_type(),
                                                                      matching_repo.get_parser_config())
            print(response.json())
            return parser.parse(response=response.json())





