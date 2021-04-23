import os
from re import compile, match
from requests import get, Response
from typing import Match, NamedTuple, Pattern, Sequence
from urllib.parse import urlparse, urlsplit, ParseResult


class PID(object):
    """
    Class wrapping possible parses of input string (HDL, DOI, URL)

    Attributes:
        pid: type,      type of underlying parsed PID class instance
    """
    def __init__(self, pid_string: str):
        """
        :param pid_string:  str, PID string that is a URL, handle or doi.
        """
        pid_types: list = [HDL, DOI, URL]
        self.pid: object = None
        for pid_type in pid_types:
            # Try to create new instance of pid type
            try:
                self.pid = pid_type(pid_string)
            except ValueError:
                continue
            if self.pid:
                break
        if not self.pid:
            raise ValueError(f"Provided string {self.pid} is in invalid PID format")

    def __str__(self):
        return str(self.pid)

    def get_pid_type(self) -> type:
        """
        Get underlying type of PID

        :return: type, one of classes: URL, HDL, DOI
        """
        return type(self.pid)

    def get_record_id(self) -> str:
        """
        Get the ID

        :return: str, record/entity #TODO nomenclature
        """
        return self.pid.get_record_id()

    def get_repo_id(self) -> str:
        return self.pid.get_repo_id()

    def get_resolvable(self) -> str:
        return self.pid.resolvable()

    def get_collection(self) -> str:
        if hasattr(self.pid, 'get_collection'):
            return self.pid.get_collection()
        else:
            return ""

    def to_url(self):
        """
        Cast underlying PID to URL

        :return: None
        """
        url = self.pid.resolve_to_url()
        self.pid = URL(url)

    @classmethod
    def is_pid(cls, pid_string: str):
        return HDL.is_hdl(pid_string) or URL.is_url(pid_string) or DOI.is_doi(pid_string)

    @classmethod
    def is_hdl_or_doi(cls, pid_string: str):
        return HDL.is_hdl(pid_string) or DOI.is_doi(pid_string)


class URL:
    def __init__(self, url_string: str):
        if not self.is_url(url_string):
            raise ValueError(f"Provided string {url_string} is not an URL")
        if url_string.split('/')[-1] == '':
            url_string = '/'.join(url_string.split('/')[:-1])
        self.url: ParseResult = urlparse(url_string)
        url_split: NamedTuple = urlsplit(url_string)
        self.host_netloc: str = getattr(url_split, 'hostname')
        _path: str = getattr(url_split, 'path')
        if getattr(url_split, 'query'):
            q = getattr(url_split, 'query')
            pid: PID = PID(q)
            self.record_id = str(pid)

        self.record_id: str = self.url.geturl().split('/')[-1]
        self.collection: str = self.url.geturl().split('/')[-2]

    def __str__(self):
        return self.url.geturl()

    def resolvable(self):
        return self.__str__()

    def get_collection(self):
        return self.collection

    def get_record_id(self):
        return self.record_id

    def resolve_to_url(self) -> str:
        return self.__str__()

    @staticmethod
    def is_url(url_string: str) -> bool:
        try:
            url: ParseResult = urlparse(url_string)
            if url.netloc == '':
                return False
        except ValueError:
            return False
        except TypeError:
            return False
        return True


class DOI:
    def __init__(self, doi_string: str):
        if not self.is_doi(doi_string):
            raise ValueError(f"Provided string {doi_string} is not a DOI")

        doi_pattern: Pattern = compile(
            r"^(?:10\.)(?P<repo_id>[\d]+)/(?P<collection>[\w-]+)(?P<repo_record_sep>[./])(?P<record_id>[\w]*)?$")
        doi_match: Match = doi_pattern.match(doi_string)
        matched_groups: dict = doi_match.groupdict()
        self.repo_id: str = "10." + doi_match.group("repo_id")
        self.collection: str = doi_match.group("collection")
        self.repo_record_sep: str = ''
        self.record_id: str = ''
        if "repo_record_sep" in matched_groups and "record_id" in matched_groups:
            self.repo_record_sep: str = doi_match.group("repo_record_sep")
            self.record_id: str = doi_match.group("record_id")

    def __str__(self):
        return f'doi:{self.repo_id}/{self.collection}{self.repo_record_sep}{self.record_id}'

    def resolvable(self) -> str:
        return 'https://doi.org/' + self.__str__()

    def get_record_id(self):
        return self.record_id

    def get_repo_id(self):
        return self.repo_id

    @staticmethod
    def is_doi(doi_string: str) -> bool:
        regex: Pattern = compile(r".*10.\d{4,9}/[^\W]+[./][\w]+$")
        if match(regex, doi_string):
            return True
        else:
            return False


class HDL:
    def __init__(self, hdl_string: str):
        if not self.is_hdl(hdl_string):
            raise ValueError(f"Provided string {hdl_string} is not a HDL")
        hdl_pattern: Pattern = compile(
            r".*(?:hdl:|hdl.handle.net\/)(?P<repo_id>[\w.]+)\/(?P<record_id>[\w\-]+)(?:[@\w=]+)?$")
        hdl_match: Match = hdl_pattern.fullmatch(hdl_string)
        if not hdl_match:

            raise ValueError(f"Provided string {hdl_string} is not a HDL")
        self.repo_id: str = hdl_match.group("repo_id")
        self.record_id: str = hdl_match.group("record_id")

    def __str__(self):
        return self.resolvable()

    def resolvable(self) -> str:
        return f"https://hdl.handle.net/{self.repo_id}/{self.record_id}"

    def get_record_id(self):
        return self.record_id

    def get_repo_id(self):
        return self.repo_id

    @staticmethod
    def is_hdl(hdl_string: str) -> bool:
        regex: Pattern = compile(r".*[\d]{4,9}/[\w\d-]+(?:[@\w=]+)?$")
        if match(regex, hdl_string):
            return True
        else:
            return False
