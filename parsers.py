from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Generator, NamedTuple, Type
from xml.etree import ElementTree


class Parser(ABC):
    @abstractmethod
    def parse(self, response: dict) -> list:
        pass


class JSONParser(Parser):
    def __init__(self, parser_config: dict):
        self.items_root = parser_config['items_root']
        self.item_key = parser_config['item']['pid']
        self.title_key = parser_config['item']['title']

    def parse(self, response: dict):
        items_root: dict = response[self.items_root]
        items = self._parse_items(items_root)
        return items

    def _parse_items(self, items_root: dict) -> list:
        items = []
        for item in items_root:
            items.append((item[self.title_key], item[self.item_key]))
        return items

    def _parse_metadata(self):
        pass


class CMDIParser(Parser):
    def __init__(self, items_root: str, item_key: str, title_key: str):
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
