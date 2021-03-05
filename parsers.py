from collections import namedtuple
from requests import Response
from typing import Any, Generator, List, NamedTuple, Type, Union
from lxml.etree import fromstring, Element, ElementTree

from pid import PID
from repos import RegRepo


class JSONParser:
    """
    Generic parser for retrieving direct reference/download link to all resources linked in collection in JSON responses

    See config schema in # TODO repository config schema validation
    """
    def __init__(self, parser_config: dict):
        """

        :param parser_config: dict, parser configuration retrieved from repository JSON config
        """
        super().__init__()
        self.dos_root: dict = parser_config['items_root']
        self.pid_path: str = parser_config['ref_file']['pid']
        self.pid_format: str = ''
        if 'pid_api' in parser_config['ref_file'].keys():
            self.pid_format = parser_config['ref_file']['pid_api']
        self.filename_path: str = parser_config['ref_file']['filename']
        self.description_path: str = parser_config['description']
        self.license_path: str = parser_config['license']

    def fetch(self, response: Response, reg_repo: RegRepo) -> dict:
        """

        :param response: dict, json response from call to repository
        :return: dict, result of response parsing:
            digitalObjects: [{filename: str, pid: str}]
            decriptions: [str]
            license: str
        """
        response: dict = response.json()
        ref_files_root: dict = self.traverse_path_in_dict(response, self.dos_root)
        ref_files: list = self._fetch_resources(ref_files_root, reg_repo)
        descriptions: str = self._parse_description(response)
        _license: str = str(self._parse_license(response))

        return {"ref_files": ref_files,
                "description": descriptions,
                "license": _license}

    def _fetch_resources(self, ref_files_root: dict, reg_repo: RegRepo) -> list:
        """
        Find all direct references/download links to referenced resources and if possible their filenames/labels
        :param ref_files_root: dict, subdict of JSON response that is a root dict of referenced resources
        :return: list, list of dictionaries [{"filename": str, "pid": str}]
        """
        ret = []
        filenames = list(self.fetchall_path_in_dict(ref_files_root, self.filename_path))
        pids = self.fetchall_path_in_dict(ref_files_root, self.pid_path)
        for filename, _pid in zip(filenames, pids):
            try:
                pid: PID = PID(_pid)
            except ValueError:
                continue
            if self.pid_format:
                # TODO generic pid formatting for downloadable resource
                pid: str = f'{reg_repo.get_host_netloc()}{self.pid_format.replace("$pid", str(pid))}'
            else:
                pid: str = pid.get_resolvable()
            ret.append({"filename": filename, "pid": pid})
        return ret

    def _parse_description(self, response: dict) -> str:
        """
        Find collection description if path provided
        :param response: dict, JSON response from repository
        :return: str, description text, if description spread into multiple tags (e.g. Trolling)
        join all collection descriptions
        """
        if self.description_path:
            return '\n'.join(self.fetchall_path_in_dict(response, self.description_path))
        else:
            return ''

    def _parse_license(self, response: dict) -> str:
        """
        Find collection license if path provided
        :param response: dict, JSON response from repository
        :return: str, license
        """
        if self.license_path:
            return list(self.fetchall_path_in_dict(response, self.license_path))[0]
        else:
            return ""

    def traverse_path_in_dict(self, _dict: dict, path: str) -> Union[dict, str, list]:
        """
        Utility method for dict navigation

        :param _dict: dict to traverse
        :param path: file system like path, e.g. A/B/C
        :return: Union[dict, str, list], return first result of path traversal, e.g. for a dict below and
                                            path "A/B" return {"C": "val"},
                                            path "A/B/C" return 'val'
            dict = {"A": {
                        "B": {
                            "C": "val"}}}
        """
        for key in path.split('/'):
            _dict = _dict[key]
        return _dict

    def fetchall_path_in_dict(self, root: dict, path: str) -> list:
        """
        Utility method for fetching all values with a given path in iterable
        :param root: dict, dict to fetch from
        :param path: str, file system like path,
        :return: list, for a dict below and path "A/B/C" return ["val1", "val2"],
            dict = {"A": {
                        "B": [
                            "0": {"C": "val1"},
                            "1": {"C": "val2"}]}}
        """
        keys_to_follow = path.split('/')
        return [elem for elem in self._fetchall_path_in_dict(root, keys_to_follow)]

    def _fetchall_path_in_dict(self, root: dict, keys_to_follow: list) -> Generator[Any, Any, None]:
        """
        Utility generator for yielding all results in iterable
        :param root: dict, dict with nested iterable to yield from
        :param keys_to_follow: list, path split into queue of keys
        :return: Generator, Generator object yielding all found queue matched in dict
        """
        if hasattr(root, 'items'):
            for k, v in root.items():
                if k == keys_to_follow[0]:
                    # Check if last key, in case of multiple occurrences of the same key
                    if k == keys_to_follow[-1] and len(keys_to_follow) == 1:
                        yield v
                    else:
                        keys_to_follow.pop(0)
                        if isinstance(v, dict):
                            for result in self._fetchall_path_in_dict(v, keys_to_follow[:]):
                                yield result
                        elif isinstance(v, list):
                            for d in v:
                                for result in self._fetchall_path_in_dict(d, keys_to_follow[:]):
                                    yield result
        elif isinstance(root, list):
            for d in root:
                for result in self._fetchall_path_in_dict(d, keys_to_follow[:]):
                    yield result


class XMLParser:
    """
    Generic parser for retrieving direct reference/download link to all resources linked in collection in XML responses

    See config schema in # TODO repository config schema validation
    """
    def __init__(self, parser_config: dict):
        """

        :param parser_config: dict, parser configuration retrieved from repository XML config
        """
        if 'namespaces' in parser_config.keys():
            self.namespaces: dict = parser_config['namespaces']
        else:
            self.namespaces: dict = {}
        self.pid_path: str = parser_config['ref_file']['pid']
        self.filename_path: str = parser_config['ref_file']['filename']
        self.description_path: str = parser_config['description']
        self.license_path: str = parser_config['license']

    def fetch(self, response: Response, reg_repo: RegRepo) -> dict:
        """
        Method wrapping fetch logic

        :param response: Response, response from repository
        :param reg_repo: RegRepo, object of Registered Repository for providing necessary repo-specific behaviour
        :return: dict, return fetch result in a format:
            {
                "ref_files": [{"filename": str, "pid": str}],
                "description": str,
                "license: str
            }
        """
        xml_tree: ElementTree = fromstring(response.text.encode('utf-8'))
        nsmap: dict = {**self.namespaces, **xml_tree.nsmap}
        resources: list = self._fetch_resources(xml_tree, nsmap)
        description: str = self._fetch_description(xml_tree, nsmap)
        _license: str = self._fetch_license(xml_tree, nsmap)

        return {"ref_files": resources,
                "description": description,
                "license": _license}

    def _fetch_resources(self, xml_tree: ElementTree, nsmap: dict) -> list:
        """
        Find all direct references/download links to referenced resources and if possible their filenames/labels
        :param xml_tree: ElementTree, lxml tree object from XML response
        :param nsmap: dict, dictionary with combined parsed namespaces and namespaces from repo config file
            in a case of nested namespaces not parsable by lxml # TODO alternative?
        :return: list, list of dictionaries [{"filename": str, "pid": str}]
        """
        ref_resources = xml_tree.findall(self.pid_path, nsmap)
        if self.filename_path:
            labels = xml_tree.find(self.filename_path, nsmap)
            return [{"filename": label.text, "pid": ref_resource.text} for ref_resource, label in zip(ref_resources, labels)]
        else:
            return [{"filename": '', "pid": ref_resource.text} for ref_resource in ref_resources]

    def _fetch_license(self, xml_tree: ElementTree, nsmap: dict) -> str:
        """
        Find collection license if path provided
        :param response: dict, JSON response from repository
        :return: str, license
        """
        try:
            license = xml_tree.find(self.license_path, nsmap)
        except SyntaxError:
            return ''
        
        if license is not None:
            return license.text
        else:
            return ''

    def _fetch_description(self, xml_tree: ElementTree, nsmap: dict):
        """
        Find collection description if path provided
        :param response: dict, JSON response from repository
        :return: str, description text, if description spread into multiple tags (e.g. Trolling)
        join all collection descriptions
        """
        try:
            description = xml_tree.find(self.description_path, nsmap)
        except SyntaxError:
            return ''

        if description:
            return description.text
        else:
            return ''
