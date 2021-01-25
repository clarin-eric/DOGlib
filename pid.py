from re import compile, match, Match, Pattern
from requests import get, Response
from typing import NamedTuple
from urllib.parse import urlparse, urlsplit, ParseResult

from repos import RegRepo


class PID:
    def __init__(self, pid_string: str):
        pid_types: list = [URL, DOI, HDL]
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

    def match(self, reg_repo: RegRepo) -> bool:
        return self.pid.match(reg_repo)

    def pid_type(self) -> type:
        return type(self.pid)

    def record_id(self) -> str:
        return self.pid.pid.record_id()

    def to_url(self):
        self.pid = self.pid.to_url()


class URL:
    def __init__(self, url_string: str):
        if not self.is_url(url_string) or 'hdl.handle.net' in url_string or 'doi.org' in url_string:
            raise ValueError(f"Provided string {url_string} is not an URL")
        url_split: NamedTuple = urlsplit(url_string)
        self.host_name: str = getattr(url_split, 'hostname')

        _path: str = getattr(url_split, 'path')
        url_pattern: Pattern = compile(r"(?:/)(?P<repo_id>\d{0,9})/(?!/).*(?P<record_id>[\w]+)$")
        url_match: Match = url_pattern.match(_path)

        self.repo_id: str = url_match.group("repo_id")
        self.record_id: str = url_match.group("record_id")
        self.url: str = url_string

    def match(self, reg_repo: RegRepo) -> bool:
        return reg_repo.host_name == self.host_name

    def to_url(self):
        return self

    @staticmethod
    def is_url(url_string: str) -> bool:
        try:
            url: ParseResult = urlparse(url_string)
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
            r"(?:doi:)10.(?P<repo_id>\d{4,9})/(?P<host_name>[\w]+)\.(?P<record_id>[\w]+)$")
        doi_match: Match = doi_pattern.match(doi_string)
        self.repo_id: str = "10." + doi_match.group("repo_id")
        self.host_name: str = doi_match.group("host_name")
        self.record_id: str = doi_match.group("record_id")

    def match(self, reg_repo: RegRepo) -> bool:
        return reg_repo.doi_id == self.repo_id

    def to_url(self) -> URL:
        redirect: Response = get(f'https://doi.org/{self.repo_id}/{self.host_name}/{self.repo_id}', follow_redirects=False)
        redirect_url: str = redirect.url
        return URL(redirect_url)

    @staticmethod
    def is_doi(doi_string: str) -> bool:
        regex: Pattern = compile(r"10.\d{4,9}/[\w]+.[\w]+$")
        if match(regex, doi_string):
            return True
        else:
            return False


class HDL:
    def __init__(self, hdl_string: str):
        if not self.is_hdl(hdl_string):
            raise ValueError(f"Provided string {hdl_string} is not an URL")
        hdl_pattern: Pattern = compile(
            r"(?:hdl:)(?P<repo_id>\d{4,9})/(?P<record_id>[\w]+)$")
        hdl_match: Match = hdl_pattern.match(hdl_string)
        self.repo_id: str = hdl_match.group("repo_id")
        self.record_id: str = hdl_match.group("record_id")
        self.hdl_string: str = hdl_string

    def match(self, reg_repo: RegRepo) -> bool:
        return reg_repo.hdl_id == self.repo_id

    def to_url(self) -> URL:
        redirect: Response = get(f'http://hdl.handle.net/{self.repo_id}/{self.repo_id}', follow_redirects=False)
        redirect_url: str = redirect.url
        return URL(redirect_url)

    @staticmethod
    def is_hdl(hdl_string: str) -> bool:
        regex: Pattern = compile(r"(?:hdl:)\d{4,9}/[\w]+$")
        if match(regex, hdl_string):
            return True
        else:
            return False
