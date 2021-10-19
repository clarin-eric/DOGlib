import json
import os
from typing import List, Union, Optional

from . import curl
from .repos import RegRepo
from .parsers import CMDIParser, JSONParser, XMLParser
from .pid import pid_factory, PID


class DOG:
    def __init__(self):
        self.reg_repos: List[RegRepo] = self._load_repos()

    def _fetch(self, pid: PID) -> dict:
        """
        Method that takes care of parser construction and parse call

        :param pid: PID, class instance of PID protocol
        :return: dict, return fetch result in a format:
            {
                "ref_files": [{"filename": str, "pid": str}],
                "description": str,
                "license: str
            }
        """
        matching_repo: RegRepo = self._sniff(pid)
        print("HERE")
        print(matching_repo)
        if not matching_repo:
            print("NOT")
            return {}
        elif matching_repo:
            request_url: str = matching_repo.get_request_url(pid)
            headers: dict = matching_repo.get_headers()
            final_url, response, response_headers = curl.get(request_url, headers, follow_redirects=True)

            parser: Union[JSONParser, XMLParser] = self._make_parser(matching_repo.get_parser_type(),
                                                                     matching_repo.get_parser_config())
            return parser.fetch(response)

    @staticmethod
    def _load_repos(config_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_configs")) \
            -> List[RegRepo]:
        """
        Method for constructor taking care of loading repository configurations

        :param config_dir: str, path to directory with repository configs, defaults to path './repo_configs' relative
            to doglib.py location
        :return: List[RegRepo], list of RegRepo objects
        """
        reg_repos: List[RegRepo] = []
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Config dir {config_dir} does not exist")

        for config_file in os.listdir(config_dir):
            if config_file.endswith(".json"):
                with open(os.path.join(config_dir, config_file)) as cfile:
                    try:
                        repo_config: dict = json.load(cfile)["repository"]
                    except json.decoder.JSONDecodeError as error:
                        raise Exception(f"{error}\nConfig failing to load: {cfile}")
                    reg_repo: RegRepo = RegRepo(repo_config)
                    reg_repos.append(reg_repo)
        return reg_repos

    def _sniff(self, pid: PID) -> Optional[RegRepo]:
        """
        Check if pid matches any registered repository

        :param pid: PID, class instance of PID protocol
        :return: Optional[RegRepo, None], returns matching RegRepo if found, None otherwise
        """
        sniffed_repos: list = []
        for reg_repo in self.reg_repos:
            if reg_repo.match_pid(pid):
                sniffed_repos.append(reg_repo)
        return self._match_sniffed(sniffed_repos, pid)

    def _match_sniffed(self, sniffed_repos: list, pid: PID) -> Optional[RegRepo]:
        """
        Matches PID with hosting repo. Method used by DOG._sniff()

        :param sniffed_repos: list, registered repositories possibly hosting referenced PID metadata
        :param pid: PID, class instance of PID protocol
        :return: Optional[RegRepo, None], returns matching RegRepo if found, None otherwise
        """
        for matching_repo in sniffed_repos:
            if len(sniffed_repos) > 1:
                try:
                    candidate = curl.get(matching_repo.get_request_url(pid), matching_repo.get_headers(), True)[0]
                except curl.RequestError:
                    continue
                url: PID = pid_factory(candidate)
                if url:
                    if matching_repo.match_pid(url):
                        return matching_repo
            else:
                return matching_repo
        return None

    def _make_parser(self, parser_type: str, parser_config: dict) -> Union[JSONParser, XMLParser, None]:
        """
        Mathod wraping parser constrution

        :param parser_type: str, Repository response format (json, cmdi) dependent Parser type
        :param parser_config: dict, Parser configuration dictionary
        :return: Union[JSONParser, XMLParser], repo specific parser type object
        """
        if parser_type == "json":
            return JSONParser(parser_config)
        elif parser_type == "xml":
            return XMLParser(parser_config)
        elif parser_type == "cmdi":
            return CMDIParser(parser_config)
        else:
            return None

    def is_downloadable(self, pid_string: str) -> bool:
        """
        Method checks if reference link is downloadable by investigating Content-Disposition header of the response

        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :return: bool, true if downloadable, false otherwise
        """
        _, response_headers = curl.head(pid_string, follow_redirects=True)
        return "Content-Disposition: attachment" in response_headers

    def is_host_registered(self, pid_string: str) -> bool:
        """
        Method for recognition whether provided PID reference is hosted by registered repository

        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :return: bool, True if PID belongs to registered repository, False otherwise
        """
        pid = pid_factory(pid_string)
        if not pid:
            return False
        return bool(self._sniff(pid))

    def is_collection(self, pid_string: str) -> bool:
        """
        Method wrap over _sniff() for recognition whether provided PID is a collection hosted by registered repository

        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :return: bool, True if PID belongs to registered repository, False otherwise
        """
        if self.is_host_registered(pid_string):
            if not self.is_downloadable(pid_string):
                pid: PID = pid_factory(pid_string)
                if pid:
                    return bool(self._fetch(pid))

        else:
            return False

    def sniff(self, pid_string: str, format='dict') -> Union[dict, str]:
        """
        Method for sniff call, tries to match pid with registered repositories and returns dict with information
        about repository, if pid is not matched returns empty dict. If there are multiple repositories using the same
        identifier tries to resolve PID and match repo by host (this can take time).

        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :param format: str={'dict', 'jsons'}, format of output, 'dict' by default
        :return: str, repository description of matching registered repository, '' if pid not matched
        """
        accepted_formats: set = {'dict', 'jsons', 'str'}
        if format not in accepted_formats:
            raise ValueError(f"Format {format} not supported, use one of {accepted_formats}")

        pid: PID = pid_factory(pid_string)
        if not pid:
            if format == 'dict':
                return {}
            elif format == 'jsons' or format == 'str':
                return ""
        sniff_result: RegRepo = self._sniff(pid)
        if not sniff_result:
            if format == 'dict':
                return {}
            elif format == 'jsons' or format == 'str':
                return ''
        if format == 'dict':
            return sniff_result.__dict__()
        elif format == 'jsons' or format == 'str':
            return json.dumps(sniff_result.__dict__())

    def fetch(self, pid_string: str, format='dict') -> Union[dict, str]:
        """
        Method for fetch call, tries to match pid with registered repositories and returns dict with collection's
            license and description, and links to referenced resources within the collection, if pid does not match
            any registered repository returns empty dict


        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :param format: str={'dict', 'jsons'}, format of output, 'dict' by default
        :return: dict, return fetch result in a format:
                {
                    "ref_files": [{"filename": str, "pid": str}],
                    "description": str,
                    "license: str
                }
            or
                str, JSON string of dict output
        """
        # TODO nested reference resolving
        accepted_formats: set = {'dict', 'jsons'}
        if format not in accepted_formats:
            raise ValueError(f"Format {format} not supported, use one of {accepted_formats}")

        pid: PID = pid_factory(pid_string)
        if not pid:
            if format == 'dict':
                return {}
            elif format == 'jsons' or format == 'str':
                return ""
        fetch_result: dict = self._fetch(pid)
        if format == 'dict':
            return fetch_result
        elif format == 'jsons' or format == 'str':
            return json.dumps(fetch_result)
