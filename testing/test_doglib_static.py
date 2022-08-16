from collections import defaultdict
import os
from typing import Callable, List, Tuple
import unittest

from abc_test import TestDOG
from doglib import STATIC_TEST_FILES_DIR, REPO_CONFIG_DIR


class TestRegisteredRepositoriesStatic(TestDOG):
    def setUp(self) -> None:
        super(TestRegisteredRepositoriesStatic, self).setUp()
        self.repos_map: dict = {repo.id: repo for repo in self.repos}
        self.static_responses: dict = self._load_static_responses()

    def _load_static_responses(self, static_dir=STATIC_TEST_FILES_DIR) -> dict:
        """
        Loads static responses from repositories for static testing

        {repo_id:
            {pid_type: static_response}
        }
        """

        repo_ids = [repo.id for repo in self.repos]
        return {repo_id: self._load_static_response(repo_id, static_dir) for repo_id in repo_ids}

    def _load_static_response(self, repo_id, static_dir):
        """
        Load static response from a file
        """
        for _, _, static_response_pid_type in os.walk(f"{static_dir}/{repo_id}"):
            for pid_type in static_response_pid_type:
                with open(f"{static_dir}/{repo_id}/{pid_type}") as static_response:
                    yield pid_type, static_response.read()

    def test_configs_against_schema(self):
        """
        Config still changes, no stable schema yet
        """
        pass

    def test_load_repos(self):
        """
        Tests whether repositories are loaded
        """
        self.assertTrue(all(self.repos))

    def test_fidelity_loaded_repos(self, repo_config_dir=REPO_CONFIG_DIR):
        """
        Checks whether all repositories have been loaded
        """
        config_dir = repo_config_dir
        #TODO align loaded repos with config files and report missing repos
        self.assertTrue((len(os.listdir(config_dir)) - 1), len(config_dir))

    def test_static_fetch(self):
        parsing_results = {repo_id:
                               {pid_type: self.repos_map[repo_id].get_parser().fetch(test_case)
                                for pid_type, test_case in test_cases}
                           for repo_id, test_cases in self.static_responses.items()}
        failures = self._find_failures(parsing_results, [bool, lambda result: bool(result["ref_files"])])
        self.assertFalse(failures)


if __name__ == '__main__':
    unittest.main()
