import csv
import json
import logging
import os
import re
from typing import List, Union, Optional

from . import curl
from .dtr import expand_datatype, DataTypeNotFoundException
from .pid import pid_factory, PID, PID_TYPE_KEYS
from .repos import FetchResult, HTMLParser, JSONParser, Parser, SignpostParser, XMLParser
from .repos import RegRepo, warn_europeana


REPO_CONFIG_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/repo_configs")
SCHEMA_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/schemas")
STATIC_TEST_FILES_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/testing")

class NoSignpostException(Exception):
    pass

def _dataclass_to_dict(obj: object) -> dict:
    if not isinstance(obj, dict):
        obj_dict = obj.__dict__
    else:
        obj_dict = obj

    for k, v in obj_dict.items():
        if isinstance(v, list):
            obj_dict[k] = [_dataclass_to_dict(_v) for _v in v]
        if isinstance(v, dict):
            obj_dict[k] = _dataclass_to_dict(obj)
        else:
            obj_dict[k] = _dataclass_to_dict(v)
    return obj_dict


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
            try:
                signpost_url = self._get_signpost_url(request_url)
                if signpost_url:
                    request_url = signpost_url
                    final_url, response, response_headers = curl.get(request_url, follow_redirects=True)
                    parser = matching_repo.get_parser("signpost")
                    print("Using singpost")
                    fetch_result: FetchResult = parser.fetch(response)
                    fetch_dict = _dataclass_to_dict(fetch_result)
                    return fetch_dict
                else:
                    raise NoSignpostException("No signpost")
                    # # TODO code repetition, how to handle if/else with nested try/except
                    # request_headers: dict = matching_repo.get_headers(pid_factory(request_url))
                    # final_url, response, response_headers = curl.get(request_url, request_headers,
                    #                                                  follow_redirects=True)
                    # parser: Parser = matching_repo.get_parser()
                    # print("Using configuration")
                    # fetch_result: FetchResult = parser.fetch(response)
                    # fetch_dict = _dataclass_to_dict(fetch_result)
                    # return fetch_dict

            except: # TODO investigate possible erroneous scenarios, matched HEAD response <link> does not imply signpost
                request_headers: dict = matching_repo.get_headers(pid_factory(request_url))
                final_url, response, response_headers = curl.get(request_url, request_headers, follow_redirects=True)
                parser: Parser = matching_repo.get_parser()
                print("Using configuration")
                fetch_result: FetchResult = parser.fetch(response)
                fetch_dict = _dataclass_to_dict(fetch_result)
                return fetch_dict


            # # try signposting
            # response, response_headers = curl.head(request_url)
            # # dictable_headers_regex = "[^\r\n](?:\\r\\n)(?P<after>[\s\S]+)"
            # dictable_headers_regex = "^[^\n]+\n(?P<headers>[\\s\\S]+)$"
            # print("RESPONSE HEADERS")
            # print(response_headers)
            #
            # dictable_response_match = re.match(dictable_headers_regex, response_headers)
            # print("MATCH")
            # print(dictable_response_match)
            # print("GROUPS")
            # print(dictable_response_match.groups())
            #
            #
            # # CHECK IF FAIR SIGNPOSTING AVAILABLE
            # headers_dict: dict = {}
            # if dictable_response_match is not None:
            #
            #     headers_string = dictable_response_match.group("headers")
            #     if "\r\n" in headers_string:
            #         headers_strings = headers_string.split("\r\n")
            #         print("BEFORE SPLIT")
            #         print(headers_strings)
            #         for header_string in headers_strings:
            #             if header_string:
            #                 header_split = header_string.split(': ')
            #                 headers_dict[header_split[0]] = header_split[1]
            # else:
            #     headers_dict = {}
            #
            # # get parser instance, if FAIR signpost available default to SignpostParser
            # if headers_dict:
            #     signpost_url = self._get_signpost_url(headers_dict)
            #     if signpost_url:
            #         request_url = signpost_url
            #         parser = matching_repo.get_parser("signpost")
            #     else:

    def fetch(self, pid_string: Union[str, PID], format: str = 'dict',
              dtr: bool = False) -> Union[dict, str]:
        """
        Method for fetch call, tries to match pid with registered repositories and returns dict with collection's
            license and description, and links to referenced resources within the collection, if pid does not match
            any registered repository returns empty dict


        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :param format: str={'dict', 'jsons'}, format of output, 'dict' by default
        :param dtr: bool, whether to expand MIME types in fetch response by their Data Type Registry
        taxonomy
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

    def identify(self, pid_string: Union[str, PID]) -> dict:
        """
        Identifies collection with its title and description, functionality requested for Virtual Content Registry

        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :return: dict, return identification result in a format:
                {
                    "item_title": str,
                    "description": str,
                    "reverse_pid": str
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
                request_url: str = matching_repo.get_request_url(pid, self.secrets)
                try:
                    signpost_url = self._get_signpost_url(request_url)
                    if signpost_url:
                        request_url = signpost_url
                        final_url, response, response_headers = curl.get(request_url, follow_redirects=True)
                        parser = matching_repo.get_parser("signpost")
                        return parser.identify(response)
                    else:
                        raise NoSignpostException("No signpost")
                except:
                    request_headers: dict = matching_repo.get_headers(pid_factory(request_url))
                    final_url, response, response_headers = curl.get(request_url, request_headers,
                                                                     follow_redirects=True)
                    parser: Parser = matching_repo.get_parser()
                    return parser.identify(response)

    def is_collection(self, pid_string: Union[str, PID]) -> bool:
        """
        Method wrap over _sniff() for recognition whether provided PID is a collection hosted by registered repository
        :param pid_string: str, persistent identifier in a format of URL, DOI or HDL
        :return: bool, True if PID belongs to registered repository, False otherwise
        """
        ret: bool
        pid: PID = pid_factory(pid_string)
        matching_repo = self._is_host_registered(pid)
        if matching_repo:
            if not self.is_downloadable(str(pid)):
                ret = bool(self._fetch(pid))
            else:
                ret = False
        else:
            ret = False
        return ret

    def is_downloadable(self, pid_string: Union[str, PID], matching_repo: RegRepo = None) -> bool:
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

    def is_host_registered(self, pid_string: Union[str, PID]) -> bool:
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

    def _get_signpost_url(self, request_url: str) -> str:
        final_url, response_headers = curl.head(request_url)
        print(type(response_headers))
        print(response_headers)
        link = ""
        if "link" in response_headers.keys():
            link_regex = "<(?P<link>[^>]+)>"

            link_match = re.match(link_regex, response_headers["link"])
            link = link_match.group("link")
        return link

    def _sniff(self, pid: PID, resolve_identifier_conflicts: bool = True) -> Union[Optional[RegRepo], Optional[List[RegRepo]]]:
        """
        Check if pid matches any registered repository

        :param pid: PID, class instance of PID protocol
        :param resolve_identifier_conflicts: bool, in case of repository identifier clash (e.g. German repositories),
            if True resolve headers and return repo matching, otherwise return list of registered repositories
            with matching identifier
        :return: Optional[RegRepo, None], returns matching RegRepo if found, None otherwise
        """
        sniffed_repos: list = []
        for reg_repo in self.reg_repos:
            if reg_repo.match_pid(pid):
                sniffed_repos.append(reg_repo)
        if resolve_identifier_conflicts:
            ret = self._match_sniffed(sniffed_repos, pid)
        else:
            ret = sniffed_repos
        return ret

    def sniff(self, pid_string: Union[str, PID], format='dict', resolve_identifier_conflicts: bool = True) -> Union[dict, str, List[str]]:
        """
        Method for sniff call, tries to match pid with registered repositories and returns dict with information
        about repository, if pid is not matched returns empty dict. If there are multiple repositories using the same
        identifier tries to resolve PID and match repo by host (this can take time).

        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :param format: str={'dict', 'jsons'}, format of output, 'dict' by default
        :param resolve_identifier_conflicts: bool, in case of repository identifier clash (e.g. German repositories),
            if True resolve headers and return repo matching, otherwise return list of registered repositories
            with matching identifier
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
        sniff_result: Union[RegRepo, List[RegRepo]] = self._sniff(
            pid, resolve_identifier_conflicts=resolve_identifier_conflicts)
        if not sniff_result:
            if format == 'dict':
                return {}
            elif format == 'jsons' or format == 'str':
                return ''
        if format == 'dict':
            if isinstance(sniff_result, List):
                return [sniff_r.__dict__() for sniff_r in sniff_result]
            return sniff_result.__dict__()
        elif format == 'jsons' or format == 'str':
            if isinstance(sniff_result, List):
                return [json.dumps(sniff_r.__dict__()) for sniff_r in sniff_result]
            return json.dumps(sniff_result.__dict__())

    def is_pid(self, pid_string: Union[str, PID]) -> bool:
        """
        Checks whether provided string is PID acceptable by DOG. For PID instance always returns True.

        :param pid_string: PID, string to validate
        :return: True if PID, False otherwise
        """
        pid = pid_factory(pid_string)
        return True if pid is not None else False

    def get_all_repositories(self) -> List[dict]:
        all_repos = [repo.__dict__() for repo in self.reg_repos]
        all_repos.sort(reverse=False, key=lambda x: x["host_name"])
        return all_repos

    def get_repository_status(self, reg_repo: RegRepo) -> dict:
        """
        #TODO docstring and status dict
        """
        status_dict: dict = {}
        for pid_type in PID_TYPE_KEYS:
            test_pid = reg_repo.get_test_example(pid_type=pid_type)
            if not test_pid:
                status_dict[pid_type] = "NA"
            else:
                try:
                    self.fetch(test_pid)
                    status_dict[pid_type] = "SUCCESS"
                except Exception as e:
                    status_dict[pid_type] = str(e)
        return status_dict

    def get_all_repositories_status(self):
        """
        #TODO docstring and report dict
        """
        return {reg_repo.get_name(): self.get_repository_status(reg_repo) for reg_repo in self.reg_repos}

    def get_all_repositories_status_csv(self, output_path: Union[str, bytes, os.PathLike]):
        """
        #TODO docstring
        """
        status_report = self.get_all_repositories_status()
        with open(output_path, "w", newline="") as csv_handle:
            csv_writer = csv.writer(csv_handle, delimiter=';', quotechar='"')
            csv_writer.writerow(["name", "doi", "hdl", "url"])
            for repo_key, repo_status in status_report.items():
                csv_writer.writerow([repo_key, repo_status["doi"], repo_status["hdl"],
                repo_status["url"]])

    def get_repository_by_name(self, repo_name="") -> Union[RegRepo, None]:
        for reg_repo in self.reg_repos:
            if reg_repo.name == repo_name:
                return reg_repo
        return None
