import json
from collections import namedtuple
import os
from typing import List, Any

from pid import PID, URL, HDL, DOI


class RegRepo(object):
    """

    """
    def __init__(self, config_dict):
        self.api: str = ''
        self.doi_id: str = ''
        self.hdl_id: str = ''
        self.host_name: str = ''
        self.host_netloc: str = ''
        self.name: str = ''
        self.parser: dict = {}
        for key in config_dict:
            setattr(self, key, config_dict[key])

    def request_url(self, pid: PID) -> str:
        pid.to_url()
        print(pid.pid)
        if self.api == "oai":
            pass
        else:
            return f"{self.host_netloc}/{self.api.replace('$record_id', pid.get_record_id())}"

    def get_host_netloc(self) -> str:
        return self.host_netloc

    def get_parser_type(self) -> str:
        return self.parser['type']

    def get_parser_config(self) -> dict:
        return self.parser['config']

    def match_pid(self, pid: PID) -> bool:
        if pid.get_pid_type() == HDL:
            return self.hdl_id == pid.pid.repo_id
        elif pid.get_pid_type() == URL:
            return self.host_netloc.replace('https://', '').replace('http://', '') == \
                   pid.pid.host_netloc.replace('https://', '').replace('http://', '')
        elif pid.get_pid_type() == DOI:
            return self.doi_id == pid.pid.repo_id
        else:
            return False

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Host name: {self.host_name}\n" \
               f"Host netloc: {self.host_netloc}"

    @staticmethod
    def config_decoder(json_dict: dict) -> Any:
        return namedtuple('RegRepo', json_dict.keys())(*json_dict.values())




