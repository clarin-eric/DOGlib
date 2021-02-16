from collections import namedtuple
from typing import Generator, NamedTuple, Type
from xml.etree import ElementTree


class Parser:
    def __init__(self):
        pass

    def parse(self, response: dict) -> list:
        pass


class JSONParser(Parser):
    def __init__(self, parser_config: dict):
        super().__init__()
        self.items_root: str = parser_config['items_root']
        self.item_key: str = parser_config['item']['pid']
        self.title_key: str = parser_config['item']['title']
        self.descritption_path: str = parser_config["description"]

    def parse(self, response: dict) -> dict:
        items_root: dict = response[self.items_root]

        items = self._parse_items(items_root)
        descriptions = self._parse_description(response)
        _license = self._parse_license(response)

        return {"items": items,
                "descriptions": descriptions,
                "license": _license}

    def _parse_items(self, items_root: dict) -> list:
        items = []
        for item in items_root:
            title: str = item[self.title_key]
            # The link to the item can be a nested dict in the file json (e.g. Zenodo)
            link_keys: list = self.item_key.split('/')
            for key in link_keys:
                item = item[key]
            digital_object = item
            items.append({"title": title, "url": digital_object})
        return items

    def _parse_description(self, response: dict) -> list:
        ret = []
        for key in self.descritption_path.split('/'):
            if isinstance(response, list):
                for desc in response:
                    ret.append(desc[key])
            else:
                response = response[key]
        return ret

    def _parse_license(self, response) -> str:
        _license = response
        for key in self.license.split('/'):
            _license = _license[key]
        return _license


class DataverseParser(Parser):
    def __init__(self, parser_config: dict):
        super().__init__()
        self.record_api: str = "https://dataverse.no/api/access/datafile/:persistentId?persistentId=$persistentId"

    def parse(self, response: dict):
        response = response["data"]["latestVersion"]
        items_root: dict = response["files"]
        metadata: dict = response["metadataBlocks"]

        _license = response["license"]
        items = self._parse_items(items_root)
        title = self._parse_title(metadata)

        return {"items": items,
                "license": _license}

    def _parse_items(self, items_root: dict) -> list:
        items = []
        for item in items_root:
            persistentId = item["dataFile"]["persistentId"]
            title = item["dataFile"]["filename"]
            items.append({"title": title, "url": self.record_api.replace("$persistentId", persistentId)})
        return items

    def _parse_title(self, metadata: dict) -> str:
        for field in metadata["citation"]["fields"]:
            if field["typeName"] == "title":
                return field["value"]


class CMDIParser(Parser):
    def __init__(self, items_root: str, item_key: str, title_key: str):
        super().__init__()
        self.items_root = items_root
        self.item_key = item_key
        self.title_key = title_key

    def parse(self, response: str):
        tree = ElementTree.parse(response)
        items_root = tree.getroot()
        return self._parse()

    def _parse(self, items_root):
        for item in items_root.getchildren():
            if item.tag == self.item_key:
                print(item)
            else:
                self.parse(item)
