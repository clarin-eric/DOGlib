from re import compile, match
from typing import Match, NamedTuple, Pattern, Protocol, Union, runtime_checkable
from urllib.parse import urlparse, urlsplit, ParseResult

PID_TYPE_KEYS = {"hdl", "doi", "url"}


@runtime_checkable
class PID(Protocol):
    """
    Abstract interface (a protocol) for PID instances
    """
    def __str__(self):
        ...

    def get_record_id(self) -> str:
        ...

    def get_repo_id(self) -> str:
        ...

    def get_resolvable(self) -> str:
        ...

    def get_host_netloc(self) -> str:
        ...


def pid_factory(pid_string: Union[str, PID]) -> Union[PID, None]:
    """
    Function for constructing relevant instance of PID protocol
    """
    if isinstance(pid_string, PID):
        return pid_string
    elif DOI.is_doi(pid_string):
        return DOI(pid_string)
    elif HDL.is_hdl(pid_string):
        return HDL(pid_string)
    elif URL.is_url(pid_string):
        return URL(pid_string)
    else:
        return None


class URL(PID):
    def __init__(self, url_string: str):
        if not self.is_url(url_string):
            raise ValueError(f"Provided string {url_string} is not an URL")
        if url_string.split('/')[-1] == '':
            url_string = '/'.join(url_string.split('/')[:-1])
        self.url: ParseResult = urlparse(url_string)
        url_split: NamedTuple = urlsplit(url_string)
        self.host_netloc: str = getattr(url_split, 'hostname')
        _path: str = getattr(url_split, 'path')

        self.record_id: str = self.url.geturl().split('/')[-1]
        self.collection: str = self.url.geturl().split('/')[-2]

    def __str__(self):
        return self.url.geturl()

    def get_resolvable(self):
        return self.__str__()

    def get_host_netloc(self):
        return self.host_netloc

    def get_repo_id(self):
        return self.collection

    def get_record_id(self):
        return self.record_id

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


class DOI(PID):
    def __init__(self, doi_string: str):
        if not self.is_doi(doi_string):
            raise ValueError(f"Provided string {doi_string} is not a DOI")

        doi_pattern: Pattern = compile(
            r"(?:https://doi.org/)?.*(?:10\.)(?P<repo_id>[\w\W]+)/(?P<record_id>[\w\W.]+)$")
        doi_match: Match = doi_pattern.match(doi_string)
        matched_groups: dict = doi_match.groupdict()
        self.repo_id: str = "10." + doi_match.group("repo_id")
        self.repo_record_sep: str = ''
        self.record_id: str = ''
        if "repo_record_sep" in matched_groups:
            self.repo_record_sep: str = doi_match.group("repo_record_sep")
        if "record_id" in matched_groups:
            self.record_id: str = doi_match.group("record_id")

    def __str__(self):
        return f'doi:{self.repo_id}/{self.repo_record_sep}{self.record_id}'

    def get_collection(self):
        return ""

    def get_host_netloc(self) -> str:
        pass

    def get_resolvable(self) -> str:
        return 'https://doi.org/' + self.__str__()

    def get_record_id(self):
        return self.record_id

    def get_repo_id(self):
        return self.repo_id

    @staticmethod
    def is_doi(doi_string: str) -> bool:
        regex: Pattern = compile(r"(?:https://doi.org/)?.*(?:10\.)(?P<repo_id>[\w\W]+)/(?P<record_id>[\w\W.]+)$")
        if match(regex, doi_string):
            return True
        else:
            return False


class HDL(PID):
    def __init__(self, hdl_string: str):
        if not self.is_hdl(hdl_string):
            raise ValueError(f"Provided string {hdl_string} is not a HDL")
        hdl_pattern: Pattern = compile(
            r"(?:http://|https://)?(?:hdl.handle.net/)?(?:hdl:)?(?P<repo_id>[\w.]+)/(?P<record_id>[\w\-.]+)(?:@format=cmdi+)?(?:@view+)?(?:\?index=[\d])?$")
        hdl_match: Match = hdl_pattern.fullmatch(hdl_string)
        if not hdl_match:

            raise ValueError(f"Provided string {hdl_string} is not a HDL")
        self.repo_id: str = hdl_match.group("repo_id")
        self.record_id: str = hdl_match.group("record_id")

    def __str__(self):
        return self.get_resolvable()

    def get_host_netloc(self) -> str:
        pass

    def get_resolvable(self) -> str:
        return f"https://hdl.handle.net/{self.repo_id}/{self.record_id}"

    def get_record_id(self):
        return self.record_id

    def get_repo_id(self):
        return self.repo_id

    @staticmethod
    def is_hdl(hdl_string: str) -> bool:
        regex: Pattern = compile(
            r"(?:http://|https://)?(?:hdl.handle.net/)?(?:hdl:)?(?P<repo_id>[\w.]+)/(?P<record_id>[\w\-.]+)(?:@format=cmdi+)?(?:@view+)?(?:\?index=[\d])?$")
        if match(regex, hdl_string):
            return True
        else:
            return False
