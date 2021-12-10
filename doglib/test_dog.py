from collections import defaultdict
import os
from typing import Callable
from unittest import TestCase

from doglib import DOG
from doglib.curl import get
from doglib.pid import PID, URL, HDL, DOI
from doglib.repos import RegRepo


class TestDOG(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.dog = DOG()
        cls.repos: list[RegRepo] = cls.dog._load_repos()


class TestRegisteredRepositories(TestDOG):
    def test_configs_against_schema(self):
        """
        Config still changes, no stable schema yet
        """
        pass

    def test_load_repos(self):
        """
        Tests whether repositories are loaded
        """
        self.assertTrue(self.repos)

    def test_fidelity_loaded_repos(self):
        """
        Checks whether all repositories have been loaded
        """
        config_dir = self.dog.config_dir
        #TODO align loaded repos with config files and report missing repos
        self.assertTrue(len(os.listdir(config_dir)) == len(config_dir))


class TestResolvingAndParsing(TestDOG):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.repos_testcases: dict = {repo: repo.get_test_examples() for repo in cls.repos}

    def _find_failures(self, test_results, conditions: [Callable[[dict], bool]]) -> dict:
        """
        Function for husking failures from mapping function to test cases

        :param test_results: dict, dictionary containing results of test calls over repositories and PID types in format {repo:{pids: resolvable_pid}}
        :param conditions: [Callable], a list of functions dict -> bool, if all return true, record is accepted as correct
        :return: filter, an iterator over input dict without pids with no resolvable test cases
        """
        failures: dict = defaultdict(list)
        for repo, pidtype_result in test_results.items():
            for pidtype, result in pidtype_result.items():
                if not all([condition(result) for condition in conditions]):
                    failures[repo].append(pidtype)
        return failures

    def _filter_empty_testcases(self, test_cases: dict) -> filter:
        """
        Filter out empty test cases

        :param test_cases: dict, dictionary containing test cases for repositories pid types in format {repo:{pids: resolvable_pid}}
        :return: filter, an iterator over input dict without pids with no resolvable test cases
        """
        return filter(lambda pidtype_resolvable: pidtype_resolvable[1] != "", test_cases.items())

    def _map_func_over_testcases(self, func: Callable, test_cases: dict) -> dict:
        """
        Apply function to test cases

        :param func: Callable, a function to map over test examples
        :param test_cases: dict, dictionary containing test cases for repositories pid types in format {repo:{pids: resolvable_pid}}
        :return: dict, dictionary with results of function application to test cases
        """
        return {repo:
                    {pid_type: func(resolvable)
                     for pid_type, resolvable in pidtype_resolvable}
                for repo, pidtype_resolvable in self._filter_empty_testcases(test_cases)}

    def test_sniff(self):
        """
        Test sniff() over all registered repositories
        """
        sniff_results: dict = self._map_func_over_testcases(self.dog.sniff, self.repos_testcases)
        failures: dict = self._find_failures(sniff_results, [bool])
        self.assertFalse(failures)

    def test_fetch_cmdi(self):
        """
        Test fetch() over repos supporting CMDI content negotiation
        """
        cmdi_repos_test_cases: dict = dict(filter(lambda repo_testcases: repo_testcases[0].get_parser_type() == "cmdi",
                                                  self.repos_testcases))
        fetch_results: dict = self._map_func_over_testcases(self.dog.fetch, cmdi_repos_test_cases)
        failures: dict = self._find_failures(fetch_results, [bool, lambda result: bool(result["ref_files"])])
        self.assertFalse(failures)

    def test_fetch_3rd_party(self):
        """
        Test fetch() over repos not supporting CMDI content negotiation (outside CLARIN infrastructure)
        """
        repos_test_cases_3rdparty: dict = dict(filter(lambda repo_testcases: repo_testcases[0].get_parser_type() != "cmdi",
                                                  self.repos_testcases))
        fetch_results: dict = self._map_func_over_testcases(self.dog.fetch, repos_test_cases_3rdparty)
        failures: dict = self._find_failures(fetch_results, [bool, lambda result: bool(result["ref_files"])])
        self.assertFalse(failures)
