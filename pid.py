import os
from re import compile, match, Match, Pattern
from requests import get, Response
from typing import NamedTuple
from urllib.parse import urlparse, urlsplit, ParseResult


class PID(object):
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

    def pid_type(self) -> type:
        return type(self.pid)

    def record_id(self) -> str:
        return self.pid.record_id

    def to_url(self):
        self.pid = self.pid.to_url()


class URL:
    def __init__(self, url_string: str):
        if (not self.is_url(url_string)) or 'hdl.handle.net' in url_string or 'doi.org' in url_string:
            raise ValueError(f"Provided string {url_string} is not an URL")
        url_split: NamedTuple = urlsplit(url_string)
        self.host_netloc: str = getattr(url_split, 'hostname')

        _path: str = getattr(url_split, 'path')

        self.record_id: str = os.path.basename(_path)
        self.url: str = url_string

    def to_url(self):
        return self

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
            r".*(?P<repo_id>10.\d{4,9})/(?P<host_name>\w+)\.(?P<record_id>\w+)$")
        doi_match: Match = doi_pattern.match(doi_string)
        self.repo_id: str = "10." + doi_match.group("repo_id")
        self.host_name: str = doi_match.group("host_name")
        self.record_id: str = doi_match.group("record_id")

    def to_url(self) -> URL:
        redirect: Response = get(f'https://doi.org/{self.repo_id}/{self.host_name}/{self.repo_id}', follow_redirects=False)
        redirect_url: str = redirect.url
        return URL(redirect_url)

    @staticmethod
    def is_doi(doi_string: str) -> bool:
        regex: Pattern = compile(r".*10.\d{4,9}/[\w]+.[\w]+$")
        if match(regex, doi_string):
            return True
        else:
            return False


class HDL:
    def __init__(self, hdl_string: str):
        if not self.is_hdl(hdl_string):
            raise ValueError(f"Provided string {hdl_string} is not an URL")
        hdl_pattern: Pattern = compile(
            r".*(?P<repo_id>\d{4,9})/(?P<record_id>[\w\-]+)$")
        hdl_match: Match = hdl_pattern.match(hdl_string)
        self.repo_id: str = hdl_match.group("repo_id")
        self.record_id: str = hdl_match.group("record_id")
        self.hdl_string: str = hdl_string

    def to_url(self) -> URL:
        redirect: Response = get(f'http://hdl.handle.net/{self.repo_id}/{self.record_id}', follow_redirects=False)
        redirect_url: str = redirect.url
        return URL(redirect_url)

    @staticmethod
    def is_hdl(hdl_string: str) -> bool:
        regex: Pattern = compile(r".*\d{4,9}/[\w\d-]+$")
        if match(regex, hdl_string):
            return True
        else:
            return False
