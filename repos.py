import json
from collections import namedtuple
import os
from re import compile, match, Pattern, Match
from requests import get, Response
from typing import List, Any, Protocol

from pid import PID, HDL


class RegRepo:
    def __init__(self, name: str, host_name: str, host_netloc: str, hdl_id: str, doi_id: str, api: str):
        if api == 'oai':
            self.repo = OAIRepo(hdl_id, doi_id)
        else:
            self.repo = InvenioRepo(hdl_id, doi_id, api)
        self.name: str = name
        self.host_name = host_name
        self.host_netloc = host_netloc

    @staticmethod
    def config_decoder(json_dict: dict) -> Any:
        return namedtuple('RegRepo', json_dict.keys())(*json_dict.values())

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Host name: {self.host_name}\n" \
               f"Host netloc: {self.host_netloc}"


class InvenioRepo:
    def __init__(self, hdl_id: str, doi_id: str, api: str):
        self.api: str = api
        self.hdl_id: str = hdl_id
        self.doi_id: str = doi_id

    def _hdl_doi_redirect(self, hdl: PID) -> PID:
        response: Response = get(str(hdl), allow_redirect=False)
        return PID(self._extract_redirect_doi())

    def _extract_redirect_doi(self, response: Response):
        doi_in_html_pattern: Pattern = compile(r"\w+>(?P<url_string>(http(?:s)//\w+)<)")
        doi_match: Match = match(doi_in_html_pattern, response.text)
        return doi_match.group("url_string")

    def request(self, pid: PID) -> str:
        if pid.pid_type() == HDL:
            pid = self._hdl_doi_redirect(pid)

            return f"{self.api}/{pid.pid}"
        else:
            return ''


class OAIRepo:
    def __init__(self, name: str, host_name: str, host_netloc: str, hdl_id:str, doi_id:str):
        self.name: str = name
        self.host_name = host_name
        self.host_netloc = host_netloc
        self.hdl_id: str = hdl_id
        self.doi_id: str = doi_id

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Host name: {self.host_name}\n" \
               f"Host netloc: {self.host_netloc}"


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
