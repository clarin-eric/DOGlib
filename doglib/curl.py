import certifi
from io import BytesIO
import pycurl
from typing import Optional, Tuple, Union

from .pid import PID


class CurlError(Exception):
    pass


class RequestError(CurlError):
    pass


def get(url: Union[str, PID], headers: dict = None, follow_redirects: bool = False, verbose: int = 0) -> Tuple[str, str, str]:
    """
    Performs http GET request using PyCurl
    :param url: Union[str, PID], request url
    :param headers: dict, request headers
    :param follow_redirects: bool, whether to follow redirects, False by default
    :param verbose: int,
        0: no std output other than exceptions
        1: PyCurl verbose
    :return: Tuple[str, str, str],
        0: effective url request (final redirection landing url)
        1: response body
        2: response headers
    """
    if headers is None:
        headers = {}
    response_body: BytesIO = BytesIO()
    response_headers: BytesIO = BytesIO()
    c: pycurl.Curl = pycurl.Curl()
    c.setopt(c.URL, url)
    if headers:
        c.setopt(c.HTTPHEADER, [k + ': ' + v for k, v in list(headers.items())])
    c.setopt(c.WRITEFUNCTION, response_body.write)
    c.setopt(c.HEADERFUNCTION, response_headers.write)
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(pycurl.CONNECTTIMEOUT, 600)
    c.setopt(c.CAINFO, certifi.where())
    c.setopt(pycurl.VERBOSE, verbose)
    c.perform()

    response_code = c.getinfo(c.RESPONSE_CODE)
    if response_code != 200:
        raise RequestError(f"Response code from {url}: {response_code}") #TODO

    decoded_response_headers: str = response_headers.getvalue().decode("iso-8859-1")
    decoded_response_body: str = response_body.getvalue().decode("utf-8")
    return c.getinfo(c.EFFECTIVE_URL), decoded_response_body, decoded_response_headers


def head(url: Union[str, PID], headers: dict = None, follow_redirects: bool = False, verbose: int = 0) -> \
        Tuple[str, str]:
    """
    Performs http HEAD request using PyCurl
    :param url: request url
    :type url: Union[str, PID]
    :param headers: request headers
    :type headers: dict
    :param follow_redirects: whether to follow redirects, False by default
    :type follow_redirects: bool
    :param verbose:
        0: no std output other than exceptions
        1: PyCurl verbose
    :type verbose: int
    :returns: ,
        0: effective url request (final redirection landing url)
        1: response headers
    :rtype: Tuple[str, str]
    """
    if headers is None:
        headers = {}
    response_headers: BytesIO = BytesIO()
    c: pycurl.Curl = pycurl.Curl()
    c.setopt(c.URL, url)
    if headers:
        c.setopt(c.HTTPHEADER, [k + ': ' + v for k, v in list(headers.items())])
    c.setopt(c.NOBODY, True)
    c.setopt(c.HEADERFUNCTION, response_headers.write)
    c.setopt(c.FOLLOWLOCATION, follow_redirects)
    c.setopt(pycurl.CONNECTTIMEOUT, 60)
    c.setopt(c.CAINFO, certifi.where())
    c.setopt(pycurl.VERBOSE, verbose)
    c.perform()

    response_code = c.getinfo(c.RESPONSE_CODE)
    if response_code != 200:
        raise RequestError(f"Response code from {url}: {response_code}")  # TODO

    decoded_response_headers: str = response_headers.getvalue().decode("iso-8859-1")
    return c.getinfo(c.EFFECTIVE_URL), decoded_response_headers
