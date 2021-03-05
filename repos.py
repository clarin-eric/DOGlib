import json
from collections import namedtuple
import os
import requests
from typing import List, Any
from urllib.parse import urlencode

from pid import PID, URL, HDL, DOI


class RegRepo(object):
    """
    Class wrapping registered repository configuration, all objects of this class are loaded on the DOGlib object init
    """
    def __init__(self, config_dict: dict):
        """

        :param config_dict: dict, JSON dict with repository configuration
        """
        self.api: dict = {}
        self.doi_id: str = ''
        self.hdl_id: set = set()
        self.headers: dict = {}
        self.host_name: str = ''
        self.host_netloc: str = ''
        self.name: str = ''
        self.parser: dict = {}
        for key in config_dict:
            setattr(self, key, config_dict[key])

    def get_request_url(self, pid: PID) -> str:
        """
        Resolve the persistent identifier in case of URL and HDL and generate URL for GET request

        :param pid: PID, PID object instance
        :return: str, GET request URL string
        """
        pid.to_url()
        base = self.api["base"]
        if "params" in self.api:
            params = self.api["params"]
        else:
            params = {}

        url_query: str = urlencode(params)
        url_query = url_query.replace("%24", "$")
        url: str = f"{base}{url_query}"
        return url.replace('$collection', pid.get_collection()).replace('$record_id', pid.get_record_id())

    def get_host_netloc(self) -> str:
        """
        Return repository's host netloc

        :return: str, host netloc URL
        """
        return self.host_netloc

    def get_parser_type(self) -> str:
        """
        Return parser type relevant for this repository

        :return: str, string representation of parser type, see JSON schema for possible values # TODO ref JSON schema
        """
        return self.parser['type']

    def get_parser_config(self) -> dict:
        """
        Return dict with parser configuration, this dict is passed to relevant parser constructor

        :return: dict, parser configuration dict, see JSON schema for possible values # TODO ref JSON schema
        """
        if 'config' in self.parser:
            return self.parser['config']
        else:
            return {}

    def get_headers(self) -> dict:
        """
        Return headers for collection GET request

        :return: dict, request headers
        """
        return self.headers

    def match_pid(self, pid: PID) -> bool:
        """
        Check if given persistent identifier matches this repository

        :param pid: PID object instance
        :return: bool, True if PID points to collection in this repository, False otherwise
        """
        if pid.get_pid_type() == HDL:
            return pid.pid.repo_id in self.hdl_id
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
