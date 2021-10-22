import json
from collections import namedtuple
import os
from re import match, Match
from typing import List, Any
from urllib.parse import urlencode

from . import curl
from .pid import pid_factory, DOI, HDL, PID, URL


class RegRepo(object):
    """
    Class wrapping registered repository configuration, all objects of this class are loaded on the DOGlib object init
    """
    def __init__(self, config_dict: dict):
        """

        :param config_dict: dict, JSON dict with repository configuration
        """
        self.api: dict = {}
        self.doi: dict = {}
        self.hdl: dict = {}
        self.url: dict = {}
        self.metadata: str = ''
        self.host_name: str = ''
        self.host_netloc: str = ''
        self.name: str = ''
        self.parser: dict = {}
        self.test_collections: dict = {}
        for key in config_dict:
            setattr(self, key, config_dict[key])

    def get_request_url(self, pid: PID) -> str:
        """
        Resolve the persistent identifier in case of URL and HDL and generate URL for GET request

        :param pid: PID, PID object instance
        :return: Response, the response from PID call
        """
        if pid is None:
            return ""
        # Request to repo providing CMDI metadata
        if self.parser["type"] == 'cmdi':
            if type(pid) == HDL:
                return self.hdl["format"].replace("$hdl", pid.get_resolvable())
            if type(pid) == DOI:
                return self.doi["format"].replace("$doi", pid.get_resolvable())
            if type(pid) == URL and "regex" not in self.url.keys():
                return self.url["format"].replace("$url", pid.get_resolvable())

        # Generic case
        request_config: dict = {}
        if type(pid) == HDL:
            request_config = self.hdl
        elif type(pid) == DOI:
            request_config = self.doi
        elif type(pid) == URL:
            request_config = self.url

        # follow redirects
        if request_config["format"] == "redirect":
            target_url: PID = pid_factory(curl.get(pid.get_resolvable(), self.get_headers(), follow_redirects=True)[0])
            return self.get_request_url(target_url)
        # parse id
        elif "regex" in request_config.keys():
            regex = request_config["regex"]
            rmatch: Match = match(regex, pid.get_resolvable())
            record_id = rmatch.group("record_id")
            # get API call
            request_url = request_config["format"].replace("$api", self.api["base"].replace("$record_id", record_id))
            return request_url

    def get_test_collection(self, pid_type: str) -> str:
        if pid_type in self.test_collections.keys():
            return self.test_collections[pid_type]
        else:
            return ""

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
        Return dict with repo specific headers
        :return: dict, headers for http request to the repository
        """
        if self.parser['type'] == "cmdi":
            return {"Accept": "application/x-cmdi+xml"}
        elif "headers" in self.api.keys():
            return self.api["headers"]
        else:
            return {}

    def match_pid(self, pid: PID) -> bool:
        """
        Check if given persistent identifier matches this repository

        :param pid: PID object instance
        :return: bool, True if PID points to collection in this repository, False otherwise
        """
        # Match HDL with repo
        if type(pid) == HDL:
            if "id" in self.hdl.keys():
                if type(self.hdl["id"]) == str:
                    return pid.get_repo_id() == self.hdl["id"]
                else:
                    for _id in self.hdl["id"]:
                        if pid.get_repo_id() == _id:
                            return True

        # Match URL with repo
        elif type(pid) == URL:
            return self.host_netloc.replace('https://', '').replace('http://', '') == \
                   pid.get_host_netloc().replace('https://', '').replace('http://', '')

        # Match DOI with repo
        elif type(pid) == DOI:
            if "id" in self.doi.keys():
                return pid.get_repo_id in self.doi["id"]
        return False

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Host name: {self.host_name}\n" \
               f"Host netloc: {self.host_netloc}\n" \
               f"hdl: {self.hdl}\n" \
               f"doi: {self.doi}"

    def __dict__(self):
        return {"name": self.name, "host_name": self.host_name, "host_netloc": self.host_netloc}

