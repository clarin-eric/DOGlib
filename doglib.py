import json
import os
from typing import List, Union, Optional

import curl
from repos import RegRepo
from parsers import JSONParser, XMLParser
from pid import PID


class DOG:
    def __init__(self):
        self.reg_repos: List[RegRepo] = self._load_repos()

    def _fetch(self, pid_string: str) -> dict:
        """
        Method that takes care of parser construction and parse call

        :param pid_string: str, collection PID to fetch resources from
        :return: dict, return fetch result in a format:
            {
                "ref_files": [{"filename": str, "pid": str}],
                "description": str,
                "license: str
            }
        """
        matching_repo: RegRepo = self.sniff(pid_string)
        if not matching_repo:
            return {}
        elif matching_repo:
            pid = PID(pid_string)

            request_url: str = matching_repo.get_request_url(pid)
            headers: dict = matching_repo.get_headers()
            final_url, response = curl.get(request_url, headers, follow_redirects=True)

            parser: Union[JSONParser, XMLParser] = self._make_parser(matching_repo.get_parser_type(),
                                                                     matching_repo.get_parser_config())
            return parser.fetch(response, matching_repo)

    def _load_repos(self, config_dir: str = os.path.join(os.getcwd(), "repo_configs")) -> List[RegRepo]:
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

    def _sniff(self, pid: PID) -> List[RegRepo]:
        """
        Check if pid matches any registered repository

        :param pid: PID, PID object to be matched
        :return: Optional[RegRepo], if matched returns matching RegRepo object, if not returns None
        """
        ret: list = []
        for reg_repo in self.reg_repos:
            if reg_repo.match_pid(pid):
                ret.append(reg_repo)
        return ret

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
            return XMLParser(parser_config)
        else:
            return None

    # def isdownloadable(self, url: str) -> bool:
    #     """
    #     Is reference link a downloadable
    #
    #     :param url: str, resolvable url
    #     :return: bool, true if downloadable, false otherwise
    #     """
    #     headers = requests.head(url).headers
    #     return 'attachment' in headers.get('Content-Disposition', '')

    def sniff(self, pid_string: str) -> Optional[RegRepo]:
        """
        Method for sniff call, tries to match pid with registered repositories and returns string with information
        about repository, if pid is not matched returns empty string. If there are multiple repositories using the same
        identifier tries to resolve PID and match repo by host.

        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :return: str, repository description of matching registered repository, '' if pid not matched
        """

        pid: PID = PID(pid_string)
        matching_repos: List[RegRepo] = self._sniff(pid)

        for _, matching_repo in enumerate(matching_repos):
            if len(matching_repos) > 1:
                try:
                    candidate = curl.get(matching_repo.get_request_url(pid), matching_repo.get_headers(), True)[0]
                except curl.RequestError:
                    continue
                url: PID = PID(candidate)
                if matching_repo.match_pid(url):
                    return matching_repo
            else:
                return matching_repo
        return None

    def fetch(self, pid_string: str) -> dict:
        """
        Method for fetch call, tries to match pid with registered repositories and returns dict with collection's
            license and description, and links to referenced resources within the collection, if pid does not match
            any registered repository returns empty dict


        :param pid_string: str, persistent identifier of collection, may be in a format of URL, DOI or HDL
        :return: dict, return fetch result in a format:
            {
                "ref_files": [{"filename": str, "pid": str}],
                "description": str,
                "license: str
            }
        """
        # TODO nested reference resolving
        fetch_result: dict = self._fetch(pid_string)
        return fetch_result
