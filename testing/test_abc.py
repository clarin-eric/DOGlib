from collections import defaultdict
from typing import Callable, List, Tuple
import unittest

from doglib import DOG
from doglib.repos import RegRepo


class TestDOG(unittest.TestCase):
    def setUp(self) -> None:
        self.dog: DOG = DOG()
        self.repos: list[RegRepo] = DOG.load_repos()

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
                    failures[repo.get_name()].append(pidtype)
        return failures

    def _filter_empty_testcases(self, test_cases: dict) -> dict:
        """
        Filter out empty test cases from test cases' dictionary
        :param test_cases: dict, dictionary containing test cases for repositories pid types in a format
            {repo:{pids: resolvable_pid}}
        :return: filter, an iterator over input dict without pids with no resolvable test cases
        """
        return {repo:
                    {pidtype: resolvable for pidtype, resolvable in pidtype_resolvable.items() if resolvable}
                for repo, pidtype_resolvable in test_cases.items()}

    def _map_func_over_testcases(self, func: Callable, test_cases: dict) -> dict:
        """
        Apply function to test cases
        :param func: Callable, a function to map over test examples
        :param test_cases: dict, dictionary containing test cases for repositories pid types in a format
            {repo:{pids: resolvable_pid}}
        :return: dict, dictionary with results of function application to test cases
        """
        return {repo: {pid_type: func(resolvable) for pid_type, resolvable in pidtype_resolvable.items()}
                for repo, pidtype_resolvable in self._filter_empty_testcases(test_cases).items()}