from collections import namedtuple
from typing import Any, Generator, List, NamedTuple, Type, Union
from xml.etree import ElementTree

from pid import PID
from repos import RegRepo


class Parser:
    def __init__(self):
        pass

    def fetch(self, response: dict) -> list:
        pass

    def traverse_path_in_dict(self, _dict: dict, path: str) -> Union[dict, str]:
        for key in path.split('/'):
            _dict = _dict[key]
        return _dict

    def fetchall_path_in_dict(self, root: dict, path: str) -> list:
        keys_to_follow = path.split('/')
        return [elem for elem in self._fetchall_path_in_dict(root, keys_to_follow)]

    def _fetchall_path_in_dict(self, root: dict, keys_to_follow: List[str]) -> Generator[Any, Any, None]:
        if hasattr(root, 'items'):
            for k, v in root.items():
                if k == keys_to_follow[0]:
                    if k == keys_to_follow[-1]:
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


class JSONParser(Parser):
    def __init__(self, parser_config: dict):
        """

        :param parser_config: dict,
        """
        super().__init__()
        self.dos_root: str = parser_config['items_root']
        self.pid_path: str = parser_config['digital_object']['pid_key']
        self.pid_api: str = ''
        if 'pid_api' in parser_config['digital_object'].keys():
            self.pid_api = parser_config['digital_object']['pid_api']
        self.filename_path: str = parser_config['digital_object']['filename_key']
        self.description_path: str = parser_config['description']
        self.license_path: str = parser_config['license']

    def fetch(self, response: dict, reg_repo: RegRepo) -> dict:
        """

        :param response: dict, json response from call to repository
        :return: dict, result of response parsing:
            digitalObjects: [{filename: str, pid: str}]
            decriptions: [str]
            license: str
        """
        dos_root: dict = self.traverse_path_in_dict(response, self.dos_root)
        dos: list = self._fetch_dos(dos_root, reg_repo)
        descriptions = self._parse_description(response)
        _license: str = str(self._parse_license(response))

        return {"digitalObjects": dos,
                "descriptions": descriptions,
                "license": _license}

    def _fetch_dos(self, dos_root: dict, reg_repo: RegRepo) -> list:
        """
        Finds all Digital Objects in specified DO
        :param dos_root:
        :return:
        """
        dos = []
        filenames = list(self.fetchall_path_in_dict(dos_root, self.filename_path))
        pids = self.fetchall_path_in_dict(dos_root, self.pid_path)
        for filename, _pid in zip(filenames, pids):
            pid: PID = PID(_pid)
            if self.pid_api:
                pid: str = f'{reg_repo.get_host_netloc()}/{self.pid_api.replace("$pid", str(pid))}'
            else:
                pid: str = pid.get_resolvable()
            dos.append({"filename": filename, "pid": pid})
        return dos

    def _parse_description(self, response: dict) -> list:
        return list(self.fetchall_path_in_dict(response, self.description_path))

    def _parse_license(self, response) -> str:
        return list(self.fetchall_path_in_dict(response, self.license_path))[0]


class CMDIParser(Parser):
    def __init__(self, items_root: str, item_key: str, title_key: str):
        super().__init__()
        self.items_root = items_root
        self.item_key = item_key
        self.title_key = title_key

    def fetch(self, response: str):
        tree = ElementTree.parse(response)
        items_root = tree.getroot()
        return self._parse()

    def _parse(self, items_root):
        for item in items_root.getchildren():
            if item.tag == self.item_key:
                print(item)
            else:
                self.fetch(item)
