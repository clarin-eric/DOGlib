import html
import json
from lxml.etree import fromstring, Element, ElementTree
from re import compile, match, findall, Match, Pattern
from typing import Any, Generator, List, NamedTuple, Type, Union

from .pid import PID
from .repos import RegRepo


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
        self.dos_root: str = parser_config['items_root']
        self.resource_path: str = parser_config['ref_file']['path']
        self.description_path: str = parser_config['description']
        self.license_path: str = parser_config['license']
        if 'resource_format' in parser_config['ref_file'].keys():
            self.resource_format = parser_config['ref_file']['resource_format']
        else:
            self.resource_format = ""

    def fetch(self, response: str, reg_repo: RegRepo) -> dict:
        """

        :param response: dict, json response from call to repository
        :return: dict, result of response parsing:
            digitalObjects: [{filename: str, pid: str}]
            decriptions: [str]
            license: str
        """
        response: dict = json.loads(response)
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
        pids = self.fetchall_path_in_dict(ref_files_root, self.resource_path)
        for _pid in pids:
            try:
                pid: PID = PID(_pid)
            except ValueError:
                continue
            if self.resource_format:
                pid: str = f'{reg_repo.get_host_netloc()}{self.resource_format.replace("$pid", str(pid))}'
            else:
                pid: str = pid.get_resolvable()
            ret.append({"pid": pid})
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
        :return: Generator, Generator object yielding all queued key found matches in dict
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

        :param parser_config: dict, parser configuration retrieved from repository XML config in .repo_configs/
        """
        if 'nsmap' in parser_config.keys():
            self.namespaces: dict = parser_config['nsmap']
        else:
            self.namespaces: dict = {}

        # In case no accepted resource type is provided make sure to not leave the list empty, so the body of main
        # for loop in self._fetch_resources can be executed anyway
        self.accept_resource_type: list = ['']
        if 'resource_type' in parser_config.keys():
            self.accept_resource_type = parser_config['accept_resource_type']

        self.collection_title_path: str = parser_config['collection_title']
        self.reverse_pid_path: str = parser_config['reverse_pid']
        self.resource_path: str = parser_config['ref_file']['path']
        self.description_path: str = parser_config['description']
        self.license_path: str = parser_config['license']
        self.resource_format: str = ''
        if 'resource_format' in parser_config['ref_file'].keys():
            self.resource_format = parser_config['ref_file']['resource_format']

    def fetch(self, response: str) -> dict:
        """
        Method wrapping fetch logic

        :param response: Response, response from repository
        :param reg_repo: RegRepo, object of Registered Repository for providing necessary repo-specific behaviour
        :return: dict, return fetch reimport ossult in a format:
            {
                "ref_files": [{"filename": str, "pid": str}],
                "description": str,
                "license: str
            }
        """
        xml_tree: ElementTree = fromstring(response.encode('utf-8'))

        nsmap = self._prepare_namespaces(response, xml_tree)

        resources: list = self._fetch_resources(xml_tree, nsmap)
        description: str = self._fetch_description(xml_tree, nsmap)
        _license: str = self._fetch_license(xml_tree, nsmap)

        return {"ref_files": resources, "description": description, "license": _license}

    def identify_collection(self, response) -> dict:
        """
        Retrieves title and description
        """
        xml_tree: ElementTree = fromstring(response.encode('utf-8'))

        nsmap: dict = self._prepare_namespaces(response, xml_tree)

        collection_title: str = self._fetch_collection_title(xml_tree, nsmap)
        description: str = self._fetch_description(xml_tree, nsmap)
        reverse_pid: str = self._reverse_pid(xml_tree, nsmap)

        return {"collection_title": collection_title, "description": description, "reverse_pid": reverse_pid}

    def reverse_pid(self, response) -> str:
        """
        Retrieves reverse pid pointing to the collection specified in metadata
        """
        xml_tree: ElementTree = fromstring(response.encode('utf-8'))

        nsmap: dict = self._prepare_namespaces(response, xml_tree)

        reverse_pid: str = self._reverse_pid(xml_tree, nsmap)
        return reverse_pid

    def _fetch_collection_title(self, xml_tree: ElementTree, nsmap: dict) -> str:
        """
        Retrieves collection title according to xPath location specified in config
        """
        try:
            collection_title: str = xml_tree.find(self.collection_title_path, nsmap)
            return collection_title
        except SyntaxError:
            return ''

    def _fetch_resources(self, xml_tree: ElementTree, nsmap: dict) -> list:
        """
        Find all direct references/download links to referenced resources and if possible their filenames/labels
        :param xml_tree: ElementTree, lxml tree object from HTML XML response
        :param nsmap: dict, map of namespace tags to namespace URIs
        :return: list, list of dictionaries [{"filename": str, "pid": str}]
        """
        fetched_resources: dict = {}
        ref_resource_basename: str = self.resource_path.split("/")[-1]
        ret: list = []
        for resource_type in self.accept_resource_type:
            ref_resources: list = xml_tree.findall(self.resource_path.replace("$resource_type", resource_type), nsmap)

            """ 
            check if lxml compatible XPath refers to an attribute, as lxml does not support full XPath (@attribute value 
            retrieval) and XPath does not support default {None: <ns_uri>} namespace
            """
            if "@" in ref_resource_basename:
                namespace, attrib_key = self._xpath_basename_to_attr_key(ref_resource_basename)
                fetched_resources[resource_type] = [ref_resource.get(f"{{{nsmap[namespace]}}}{attrib_key}") for ref_resource in ref_resources]
            else:
                ref_resources = [ref_resource.text for ref_resource in ref_resources]

            if self.resource_format:
                ref_resources = [self.resource_format.replace("$resource", ref_resource) for ref_resource in ref_resources]

            ret.extend([{"resource_type": resource_type, "filename": "", "pid": ref_resource,} for ref_resource in ref_resources])
        return ret

    def _reverse_pid(self, xml_tree: ElementTree, nsmap: dict) -> str:
        """
        Retrieves reverse pid according to xPath location specified in config
        """
        try:
            reverse_pid = xml_tree.find(self.reverse_pid_path, nsmap)
        except SyntaxError:
            return ''

        return reverse_pid

    def _fetch_license(self, xml_tree: ElementTree, nsmap: dict) -> str:
        """
        Find collection license if path provided
        :param response: dict, JSON response from repository
        :return: str, license
        """
        if self.license_path != '':
            _licenses: List[Element] = xml_tree.findall(self.license_path, nsmap)
        else:
            return ""

        if _licenses:
            if len(_licenses) == 1:
                return _licenses[0].text
            else:
                return ""
        else:
            _licenses = [_license.text for _license in _licenses]
            return "\n".join(_licenses)

    def _fetch_description(self, xml_tree: ElementTree, nsmap: dict) -> str:
        """
        Find collection description if path provided
        :param response: dict, JSON response from repository
        :return: str, description text, if description spread into multiple tags (e.g. Trolling)
        join all collection descriptions
        """
        try:
            descriptions: list = xml_tree.findall(self.description_path, nsmap)
        except SyntaxError:
            return ''

        if descriptions:
            if len(descriptions) == 1:
                if hasattr(descriptions[0], "text"):
                    return descriptions[0].text
                else:
                    return ''
            else:
                descriptions = [description.text for description in descriptions]
                return "\n".join(descriptions)

    def _parse_nested_namespaces(self, response_text: str) -> dict:
        """
        Utility method for finding not-default
        :param response_text:
        :return:
        """
        namespace_pattern: Pattern = compile(r'xmlns:(?P<ns_key>[\w]+)="(?P<ns_uri>[^"]*)"')
        matches: list = findall(namespace_pattern, response_text)

        return {_match[0]: _match[1] for _match in matches}

    def _xpath_basename_to_attr_key(self, xpath_basename: str) -> (str, str):
        lxml_attrib_pattern: Pattern = compile(r'.*\[@(?P<attrib_name>[^]]*)]')
        attrib_key_match: Match = match(lxml_attrib_pattern, xpath_basename)
        namespace_tag, attrib_name = attrib_key_match.group("attrib_name").split(':')
        return namespace_tag, attrib_name

    def _prepare_namespaces(self, response: str, xml_tree: ElementTree) -> dict:
        nsmap: dict = {**self.namespaces, **self._parse_nested_namespaces(response)}
        # for parsing default namespace
        nsmap: dict = {**nsmap, **xml_tree.nsmap}
        return nsmap


class CMDIParser(XMLParser):
    def __init__(self, parser_config: dict):
        super().__init__(parser_config)
        if 'resource_type' in parser_config.keys():
            self.accept_resource_type = parser_config["accept_resource_type"]
        else:
            self.accept_resource_type = ["Resource", "LandingPage", "Metadata"]
        if "pid" in parser_config["ref_file"].keys():
            self.pid_path = parser_config["ref_file"]["pid"]
        else:
            self.pid_path: str = ".//ResourceProxy[ResourceType='$resource_type']/ResourceRef"
