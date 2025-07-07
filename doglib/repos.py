from re import match, Match
from typing import AnyStr, Union, Optional
import warnings

from . import curl
from .parsers import CMDIParser, HTMLParser, JSONParser, SignpostParser, XMLParser, FetchResult, IdentifyResult, Parser
from .pid import pid_factory, DOI, HDL, PID, URL


def warn_europeana() -> None:
    warnings.warn("EUROPEANA_WSKEY not provided.\n"
                  "To access Digital Objects hosted by Europeana generate your access key at "
                  "https://pro.europeana.eu/pages/get-api and set it as environment variable "
                  "or pass it as optional argument DOG(secrets={'EUROPEANA_WSKEY': <SECRET>})",
                  NoSecretWarning)


class NoSecretWarning(Warning):
    def __init__(self, message):
        self.message: AnyStr = message

    def __repr__(self):
        self.message.__repr__()


class RegRepo(object):
    """
    Class wrapping registered repository configuration, all objects of this class are loaded on the DOGlib object init
    """
    def __init__(self, config_dict: dict, dtr: bool = True):
        """

        :param config_dict: dict, JSON dict with repository configuration
        """
        self.id: str = ''
        self.api: dict = {}
        self.doi: dict = {}
        self.dtr: bool = dtr
        self.hdl: dict = {}
        self.url: dict = {}
        self.host_name: str = ''
        self.host_netloc: str = ''
        self.name: str = ''
        self.parser: dict = {}
        self.test_examples: dict = {}
        for key in config_dict:
            setattr(self, key, config_dict[key])

    def get_request_url(self, pid: PID, secrets: Optional[dict] = None) -> str:
        """
        Prepare URL to call to resolve to collection

        :param pid: PID, class instance of PID protocol
        :param secrets: Optional[dict], optional map of access tokens, e.g. EUROPEANA_WSKEY
        :return: str, URL to be called by DOG in order to resolve the PID
        """

        if pid is None:
            return ""

        # Request to repository providing CMDI metadata
        if self.parser["type"] == 'cmdi':
            if type(pid) == HDL:
                return self._set_secrets(self.hdl["format"].replace("$hdl",
                                                                    pid.get_resolvable()),
                                         secrets)
            if type(pid) == DOI:
                return self._set_secrets(self.doi["format"].replace("$doi",
                                                                    pid.get_resolvable()),
                                         secrets)
            if type(pid) == URL and "regex" not in self.url.keys():
                return self._set_secrets(self.url["format"].replace("$url",
                                                                    pid.get_resolvable()),
                                         secrets)

        # Generic cases
        request_config: dict = {}
        if type(pid) == HDL:
            request_config = self.hdl
        elif type(pid) == DOI:
            request_config = self.doi
        elif type(pid) == URL:
            request_config = self.url
            # if html scrapping return deposit URL

        # follow redirects
        if request_config["format"] == "redirect":
            target_url: PID = pid_factory(curl.get(pid.get_resolvable(),
                                                   self.get_headers(pid),
                                                   follow_redirects=True)[0])
            return self.get_request_url(target_url, secrets)
        # parse id
        elif "regex" in request_config.keys():
            regex = request_config["regex"]
            rmatch: Match = match(regex, pid.get_resolvable())

            record_id = rmatch.group("record_id")

            # get API call
            request_url = request_config["format"].replace("$api", self.api["base"])
            request_url = request_url.replace("$record_id", record_id)
            request_url = self._set_secrets(request_url, secrets)
            return request_url
        else:
            if type(pid) == HDL:
                return self.hdl["format"].replace("$hdl", pid.get_resolvable())
            elif type(pid) == DOI:
                return self.pid["format"].replace("$doi", pid.get_resolvable())
            elif type(pid) == URL:
                return self.url["format"].replace("$url", pid.get_resolvable())

    def get_host_netloc(self) -> str:
        """
        Return repository's host netloc

        :return: str, host netloc URL
        """
        return self.host_netloc

    def get_headers(self, pid: PID) -> dict:
        """
        Return dict with repo specific headers
        :return: dict, headers for http request to the repository
        """
        if type(pid) == HDL:
            if "headers" in self.hdl.keys():
                return self.hdl["headers"]
        elif type(pid) == DOI:
            if "headers" in self.doi.keys():
                return self.doi["headers"]
        elif type(pid) == URL:
            if "headers" in self.url.keys():
                return self.url["headers"]
        if self.parser['type'] == "cmdi":
            return {"Accept": "application/x-cmdi+xml"}
        elif "headers" in self.api.keys():
            return self.api["headers"]
        else:
            return {}

    def get_name(self) -> str:
        """
        Return repository's name
        :return: str, name of the repository
        """
        return self.name

    def get_parser_config(self) -> dict:
        """
        Return dict with parser configuration, this dict is passed to relevant parser constructor

        :return: dict, parser configuration dict, see JSON schema for possible values # TODO ref JSON schema
        """
        if 'config' in self.parser:
            return self.parser['config']
        else:
            return {}

    def get_parser_type(self) -> str:
        """
        Return parser type relevant for this repository

        :return: str, string representation of parser type, see JSON schema for possible values # TODO ref JSON schema
        """
        return self.parser['type']

    def get_parser(self, parser_type: str = None, parser_config: dict = None) -> Union[JSONParser, XMLParser, SignpostParser, None]:
        """
        Method wrapping parser construction

        :param parser_type: str, Repository response format (json, cmdi) dependent Parser type
        :param parser_config: dict, Parser configuration dictionary
        :return: Union[JSONParser, XMLParser], repo specific parser type object
        """
        if parser_type is None:
            parser_type = self.get_parser_type()

        if parser_config is None:
            parser_config = self.get_parser_config()

        if parser_type == "cmdi":
            return CMDIParser(parser_config)
        elif parser_type == "html":
            return HTMLParser(parser_config)
        elif parser_type == "json":
            return JSONParser(parser_config)
        elif parser_type == "xml":
            return XMLParser(parser_config)
        elif parser_type == "signpost":
            return SignpostParser(parser_config)
        else:
            return None

    def get_test_example(self, pid_type: str) -> str:
        """
        Get test case for specific pid type
        #TODO
        """
        if pid_type in self.test_examples.keys():
            return self.test_examples[pid_type]
        else:
            return ""

    def get_test_examples(self) -> dict:
        """
        Get all test cases
        """
        return self.test_examples

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
            return self.host_netloc.replace('https://', '').replace('http://', '') in \
                   pid.get_resolvable().replace('https://', '').replace('http://', '')
        # Match DOI with repo
        elif type(pid) == DOI:
            if "id" in self.doi.keys():
                return pid.get_repo_id() in self.doi["id"]
        return False

    def _set_secrets(self, pid: str, secrets: dict):
        if secrets is not None:
            for k, v in secrets.items():
                pid = pid.replace(f"${k}", v)
            return pid

    def __str__(self):
        return f"Name: {self.name}\n" \
               f"Host name: {self.host_name}\n" \
               f"Host netloc: {self.host_netloc}\n" \
               f"url: {self.url}\n" \
               f"hdl: {self.hdl}\n" \
               f"doi: {self.doi}"

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return {"name": self.name, "host_name": self.host_name, "host_netloc": self.host_netloc}

