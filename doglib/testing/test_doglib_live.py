import unittest

from doglib.testing import TestDOG


class TestResolvingAndParsingLive(TestDOG):
    def setUp(self) -> None:
        super(TestResolvingAndParsingLive, self).setUp()
        self.repos_testcases: dict = {repo: repo.get_test_examples() for repo in self.repos}

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
        cmdi_repos_test_cases: dict = {repo: pidtype_resolvable for repo, pidtype_resolvable
                                       in self._filter_empty_testcases(self.repos_testcases).items()
                                       if repo.get_parser_type() == "cmdi"}
        fetch_results: dict = self._map_func_over_testcases(self.dog.fetch, cmdi_repos_test_cases)
        failures: dict = self._find_failures(fetch_results, [bool, lambda result: bool(result["ref_files"])])
        self.assertFalse(failures)

    def test_fetch_3rd_party(self):
        """
        Test fetch() over repos not supporting CMDI content negotiation (mostly outside CLARIN infrastructure)
        """
        repos_test_cases_3rdparty: dict = {repo: pidtype_resolvable for repo, pidtype_resolvable
                                           in self._filter_empty_testcases(self.repos_testcases).items()
                                           if repo.get_parser_type() != "cmdi"}
        fetch_results: dict = self._map_func_over_testcases(self.dog.fetch, repos_test_cases_3rdparty)
        failures: dict = self._find_failures(fetch_results, [bool, lambda result: bool(result["ref_files"])])
        self.assertFalse(failures)

    def test_identify(self):
        """
        Test identify() over all registered repositories
        """
        identify_results: dict = self._map_func_over_testcases(self.dog.identify, self.repos_testcases)
        failures: dict = self._find_failures(identify_results, [bool])
        self.assertFalse(failures)

    # TODO add downloadable resource test cases to repo configs and test against them
    # def test_is_collection(self):
    #     """
    #     Test is_collection over all registered repositories
    #     """
    #     is_collection_results: dict = self._map_func_over_testcases(self.dog.is_collection, self.repos_testcases)
    #     failures: dict = self._find_failures(is_collection_results, [bool])
    #     self.assertFalse(failures)


if __name__ == '__main__':
    unittest.main()
