import os
import unittest

from doglib.testing import TestDOG
from doglib import STATIC_TEST_FILES_DIR, REPO_CONFIG_DIR


class TestRegisteredRepositoriesStatic(TestDOG):
    def setUp(self) -> None:
        super(TestRegisteredRepositoriesStatic, self).setUp()
        self.repos_map: dict = {repo.id: repo for repo in self.repos}
        # Loads static responses
        self.static_responses: dict = self._load_static_responses()
        # Loads PIDs to the resources
        self.repos_testcases: dict = {repo: repo.get_test_examples() for repo in self.repos}

    def _load_static_response(self, repo_id, static_dir):
        """
        Load static response from a file
        """
        for _, _, static_response_pid_type in os.walk(f"{static_dir}/{repo_id}"):
            for pid_type in static_response_pid_type:
                with open(f"{static_dir}/{repo_id}/{pid_type}") as static_response:
                    yield pid_type, static_response.read()

    def _load_static_responses(self, static_dir=STATIC_TEST_FILES_DIR) -> dict:
        """
        Loads static responses from repositories for static testing

        {repo_id:
            {pid_type: static_response}
        }
        """

        repo_ids = [repo.id for repo in self.repos]
        return {repo_id: self._load_static_response(repo_id, static_dir) for repo_id in repo_ids}

    def test_fidelity_loaded_repos(self, repo_config_dir=REPO_CONFIG_DIR):
        """
        Checks whether all repositories have been loaded
        """
        config_dir = repo_config_dir
        #TODO align loaded repos with config files and report missing repos
        self.assertTrue((len(os.listdir(config_dir)) - 1), len(config_dir))

    def test_identify(self):
        """
        Test identify() over all registered repositories
        """
        identify_results: dict = {repo_id:
                                      {pid_type: self.repos_map[repo_id].get_parser().fetch(test_case)
                                       for pid_type, test_case in test_cases}
                                  for repo_id, test_cases in self.static_responses.items()}
        #identify_results: dict = self._map_func_over_testcases(self.dog.identify, self.repos_testcases)
        failures: dict = self._find_failures(identify_results, [bool])
        self.assertFalse(failures)

    def test_static_fetch(self):
        """
        Test fetch() over all registered repositories
        """
        parsing_results: dict = {repo_id:
                                     {pid_type: self.repos_map[repo_id].get_parser().fetch(test_case)
                                      for pid_type, test_case in test_cases}
                                 for repo_id, test_cases in self.static_responses.items()}
        failures = self._find_failures(parsing_results, [bool, lambda result: bool(result["ref_files"])])
        self.assertFalse(failures)

    def test_static_sniff(self):
        """
        Test sniff() over all registered repositories
        """
        sniff_results: dict = self._map_func_over_testcases(self.dog.sniff, self.repos_testcases)
        failures: dict = self._find_failures(sniff_results, [bool])
        self.assertFalse(failures)


if __name__ == '__main__':
    unittest.main()
