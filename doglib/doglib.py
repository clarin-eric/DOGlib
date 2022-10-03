import json
import os
from typing import List, Union, Optional

from . import curl
from .repos import JSONParser, XMLParser
from .pid import pid_factory, PID
from .repos import RegRepo, warn_europeana

REPO_CONFIG_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/repo_configs")
SCHEMA_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/schemas")
STATIC_TEST_FILES_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/testing")


class DOG:
    def __init__(self, secrets: Optional[dict] = None):
        self.secrets: dict = self._load_secrets(secrets)
        self.reg_repos: List[RegRepo] = self.load_repos()

    def _fetch(self, pid: PID) -> dict:
        """
        Method that takes care of parser construction and parse call

        :param pid: class instance of PID protocol
        :type pid: PID
        :return: return fetch result in a dict format:
            {
                "ref_files": [{"filename": str, "pid": str}],
                "description": str,
                "license": str
            }
        :rtype: dict
        """
        matching_repo: RegRepo = self._sniff(pid)
        if not matching_repo:
            return {}
        elif matching_repo:
            request_url: str = matching_repo.get_request_url(pid, self.secrets)
            # cast generated request URL to PID to decide which header from config shall be used
            headers: dict = matching_repo.get_headers(pid_factory(request_url))
            final_url, response, response_headers = curl.get(request_url, headers, follow_redirects=True)
            parser: Union[JSONParser, XMLParser] = matching_repo.get_parser()
            return parser.fetch(response)

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

    def identify(self, pid_string: str) -> dict:
        """
        Identifies collection with its title and description, functionality requested for Virtual Content Registry

        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :return: dict, return identification result in a format:
                {
                    "title": str,
                    "description": str
                }
        """
        pid: PID = pid_factory(pid_string)
        if not pid:
            return {}
        else:
            matching_repo: RegRepo = self._sniff(pid)
            if not matching_repo:
                return {}
            elif matching_repo is not None:
                print(matching_repo)
                request_url: str = matching_repo.get_request_url(pid, self.secrets)
                headers: dict = matching_repo.get_headers(pid)
                final_url, response, response_headers = curl.get(request_url, headers, follow_redirects=True)
                parser: Union[JSONParser, XMLParser] = matching_repo.get_parser()
                return parser.identify(response)

    def is_collection(self, pid_string: str) -> bool:
        """
        Method wrap over _sniff() for recognition whether provided PID is a collection hosted by registered repository
        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :return: bool, True if PID belongs to registered repository, False otherwise
        """
        pid: PID = pid_factory(pid_string)
        matching_repo = self._is_host_registered(pid)
        if matching_repo:
            if not self.is_downloadable(pid_string):
                if pid:
                    return bool(self._fetch(pid))

        else:
            return False

    def is_downloadable(self, pid_string: str, matching_repo: RegRepo = None) -> bool:
        """
        Method checks if reference link is downloadable by investigating Content-Disposition header of the response

        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :param matching_repo: RegRepo, optional parameter, if not provided will _sniff() the repo
        :return: bool, true if downloadable, false otherwise
        """
        pid: PID = pid_factory(pid_string)
        if not matching_repo:
            matching_repo = self._sniff(pid)
        request_headers: dict = matching_repo.get_headers(pid)
        _, response_headers = curl.head(pid_string, headers=request_headers, follow_redirects=True)
        return "Content-Disposition: attachment" in response_headers

    def _is_host_registered(self, pid: PID) -> Union[RegRepo, None]:
        """
        Method for recognition whether provided PID reference is hosted by registered repository

        :param pid: PID, persistent identifier in a format of URL, DOI or HDL
        :return: bool, True if PID belongs to registered repository, False otherwise
        """
        matching_repo = self._sniff(pid)
        return matching_repo

    def is_host_registered(self, pid_string: str) -> bool:
        """
        Method for recognition whether provided PID reference is hosted by registered repository

        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :return: bool, True if PID belongs to registered repository, False otherwise
        """
        pid: PID = pid_factory(pid_string)
        return bool(self._is_host_registered(pid))

    @classmethod
    def load_repo(cls, repo_id: str, config_dir=REPO_CONFIG_DIR) -> RegRepo:
        """
        Method for loading specific repo config, used mainly for testing
        """

        config_path = f"{config_dir}/{repo_id}"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file {config_dir} does not exists")
        with open(f"{REPO_CONFIG_DIR}/{repo_id}") as  cfile:
            try:
                repo_config: dict = json.load(cfile)["repository"]
            except json.decoder.JSONDecodeError as error:
                raise RuntimeError(f"{error}\nConfig failing to load: {cfile}")
            reg_repo: RegRepo = RegRepo(repo_config)
        return reg_repo

    @classmethod
    def load_repos(cls, config_dir=REPO_CONFIG_DIR) -> List[RegRepo]:
        """
        Method for constructor taking care of loading repository configurations

        :param config_dir: path to directory with repository configs, defaults to path './repo_configs' relative
            to doglib.py location
        :type config_dir: str
        :return: List[RegRepo], list of RegRepo objects
        """
        reg_repos: List[RegRepo] = []
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Config dir {config_dir} does not exist")

        for config_file in os.listdir(config_dir):
            if config_file.endswith(".json"):
                reg_repos.append(cls.load_repo(repo_id=config_file, config_dir=config_dir))
        return reg_repos

    def _load_secrets(self, secrets: Optional[dict] = None):
        """
        Loads secrets from environment. Allows for passing explicit secrets that overwrite env vars.
        """
        _secrets = {}
        if "EUROPEANA_WSKEY" in os.environ:
            _secrets["EUROPEANA_WSKEY"] = os.environ.get("EUROPEANA_WSKEY")

        if secrets is not None:
            if "EUROPEANA_WSKEY" in secrets.keys():
                _secrets["EUROPEANA_WSKEY"] = secrets["EUROPEANA_WSKEY"]

        if "EUROPEANA_WSKEY" not in _secrets.keys():
            warn_europeana()

        return _secrets

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
                    candidate = curl.get(matching_repo.get_request_url(pid, self.secrets), matching_repo.get_headers(pid), True)[0]
                    url: PID = pid_factory(candidate)
                    if url:
                        if matching_repo.match_pid(url):
                            return matching_repo
                except curl.RequestError:
                    continue
            else:
                return matching_repo
        return None

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
