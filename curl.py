import certifi
from io import BytesIO
import pycurl
from typing import Any, Tuple, Union

from pid import PID


class CurlError(Exception):
    pass


class RequestError(CurlError):
    pass


def get(url: Union[str, PID], headers: dict = {}, follow_redirects: bool = False, verbose: int = 0) -> Tuple[str, str, str]:
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
    response_body: BytesIO = BytesIO()
    response_headers: BytesIO = BytesIO()
    c: pycurl.Curl = pycurl.Curl()
    c.setopt(c.URL, url)
    print(headers)
    if headers:
        c.setopt(c.HTTPHEADER, [k + ': ' + v for k, v in list(headers.items())])
    c.setopt(c.WRITEFUNCTION, response_body.write)
    c.setopt(c.HEADERFUNCTION, response_headers.write)
    c.setopt(c.FOLLOWLOCATION, follow_redirects)
    c.setopt(pycurl.CONNECTTIMEOUT, 60)
    c.setopt(c.CAINFO, certifi.where())
    c.setopt(pycurl.VERBOSE, verbose)
    c.perform()

    response_code = c.getinfo(c.RESPONSE_CODE)
    if response_code != 200:
        raise RequestError(f"Response code from {url}: {response_code}") #TODO

    a = response_headers.getvalue().decode("utf-8")
    print(response_headers)

    return c.getinfo(c.EFFECTIVE_URL), response_body.getvalue().decode("utf-8"), response_headers.getvalue().decode("utf-8")
