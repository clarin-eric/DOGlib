from unittest import TestCase


import doglib
from pid import PID, URL, HDL, DOI
from repos import RegRepo


class TestDOG(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repos: list[RegRepo] = doglib.DOG._load_repos()


class TestDOI(TestDOG):
    pass


class TestHDL(TestDOG):
    pass


class TestURL(TestDOG):
    pass