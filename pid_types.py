from os import path
from re import compile, match, Match, Pattern
from typing import NamedTuple
from urllib.parse import urlparse, urlsplit, ParseResult


class DOI:
    def __init__(self, doi_string: str):
        if not self.is_doi(doi_string):
            raise ValueError(f"Provided string {doi_string} is not a DOI")

        #TODO test resolvable doi
        doi_pattern: Pattern = compile(
            r"(doi:)?10.(?P<repo_id>\d{4,9})/(?P<host_name>[\w]+)\.(?P<record_id>[\w]+)$")
        doi_match: Match = doi_pattern.match(doi_string)
        self.repo_id: str = doi_match.group("repo_id")
        self.host_name: str = doi_match.group("host_name")
        self.record_id: str = doi_match.group("record_id")

    @staticmethod
    def is_doi(doi_string: str) -> bool:
        regex: Pattern = compile(r"10.\d{4,9}/[\w]+.[\w]+$")
        if match(regex, doi_string):
            return True
        else:
            return False


class URL:
    def __init__(self, url_string: str):
        if not self.is_url(url_string):
            raise ValueError(f"Provided string {url_string} is not a URL")
        url_split: NamedTuple = urlsplit(url_string)

        self.host_name: str = getattr(url_split, 'hostname')
        self.repo_id: str = ''
        _path: str = path.basename(getattr(url_split, 'path'))

    @staticmethod
    def is_url(url_string: str) -> bool:
        try:
            url: ParseResult = urlparse(url_string)
        except ValueError:
            return False
        except TypeError:
            return False
        return True


class HDL:
    def __init__(self):
        pass

    @staticmethod
    def is_hdl(handle_string: str) -> bool:
        pass