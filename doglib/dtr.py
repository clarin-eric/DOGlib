from enum import Enum
import json
from typing import List, Set, Union

from .curl import get


class DataTypeNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


def expand_datatype(data_type: str) -> dict:
    """
    Wrapper for DTR datatype taxonomy discovery
    """
    return get_dtr_taxonomy_by_type(data_type)


def get_dtr_taxonomy_by_type(data_type: str) -> dict:
    """
    Returns a dictionary representation of the MIME type taxonomy

    :param data_type: str, MIME type, e.g. 'text/xml'
    :return: dict, a dictionary representation of the type's taxonomy
    """
    dtr_type_search_endpoint = f"http://typeapi.lab.pidconsortium.net/v1/taxonomy/search?query={data_type}&name={data_type}"

    try:
        url, dtr_taxonomy_search_response, header = get(dtr_type_search_endpoint)
    except Exception as error:
        raise DataTypeNotFoundException(f"DataType <{data_type}> doesn't exist in the DTR taxonomy") from error

    dtr_taxonomy_json = json.loads(dtr_taxonomy_search_response)
    print("get_dtr_taxonomy_by_type: TAXONOMY")
    print(dtr_taxonomy_json)
    try:
        dtr_type_id = dtr_taxonomy_json[0]["id"]
    except (IndexError, KeyError) as error:
        raise DataTypeNotFoundException(f"DataType <{data_type}> doesn't exist in the DTR taxonomy") from error
    parents = dtr_taxonomy_json[0]["parents"]
    if parents:
        for parent_id, parent_name in parents.items():
            dtr_type_id = get_taxonomy_root_node_by_id(parent_id)
    return get_taxonomy_subtree_from_root_id(dtr_type_id)


def get_taxonomy_root_node_by_id(data_type_id: str) -> str:
    """
    Returns an ID of the root type of the taxonomy for the given data_type_id

    :param data_type_id: str, DTR MIME type PID, e.g. 21.T11969/f33c32fa8246e2ca6d5c
    :return: dict, a dictionary representation of the type's taxonomy
    """
    dtr_taxonomy_endpoint = f"http://typeapi.lab.pidconsortium.net/v1/taxonomy/{data_type_id}"
    url, dtr_taxonomy_node_response, header = get(dtr_taxonomy_endpoint)
    dtr_taxonomy_json = json.loads(dtr_taxonomy_node_response)
    try:
        dtr_type_id = dtr_taxonomy_json["id"]
    except (IndexError, KeyError) as error:
        raise DataTypeNotFoundException(f"DataType with id <{data_type_id}> doesn't exist in the DTR taxonomy") from error
    parents = dtr_taxonomy_json["parents"]
    # Assumption of single parent
    taxonomy_root_id = dtr_type_id
    if parents:
        for parent_id, parent_name in parents.items():
            taxonomy_root_id = get_taxonomy_root_node_by_id(parent_id)
    return taxonomy_root_id


def get_taxonomy_subtree_from_root_id(root_id: str) -> dict:
    """
    Get a subtree from the root ID

    :param root_id: str, the root node ID
    :return: dict, MIME type taxonomy
    """
    dtr_taxonomy_subtree_endpoint = f"http://typeapi.lab.pidconsortium.net/v1/taxonomy/{root_id}/subtree"
    url, dtr_taxonomy_subtree_response, header = get(dtr_taxonomy_subtree_endpoint)
    dtr_taxonomy_subtree_json = json.loads(dtr_taxonomy_subtree_response)
    return dtr_taxonomy_subtree_json


"""
OLD TAXONOMY DISCOVERY IMPLEMENTATION
"""
# class TaxonomyNode:
#     def __init__(self, pid: str, data_type: str, children: list = None, parents: list = None):
#         self.children: List[TaxonomyNode] = [] if children is None else children
#         self.data_type: str = data_type
#         self.parents: List[TaxonomyNode] = [] if parents is None else parents
#         self.pid: str = pid
#         self.dtr_taxonomy_endpoint: str = f"http://typeapi.lab.pidconsortium.net/v1/taxonomy/{self.pid}"
#
#     def dtr_type_query(self) -> dict:
#         url, dtr_taxonomy_search_response, header = get(self.dtr_taxonomy_endpoint)
#         dtr_taxonomy_json: dict = json.loads(dtr_taxonomy_search_response)
#         return dtr_taxonomy_json
#
#     def populate_relatives(self, relatives: Union[str, Set[str]]) -> "TaxonomyNode":
#         dtr_taxonomy_json: dict = self.dtr_type_query()
#         if "children" in relatives:
#             for child_pid, child_name in dtr_taxonomy_json["children"].items():
#                 child_node = TaxonomyNode(child_pid, child_name)
#                 child_node.populate_relatives("children")
#                 self.add_child(child_node)
#         if "parents" in relatives:
#             for parent_pid, parent_name in dtr_taxonomy_json["parents"].items():
#                 parent_node = TaxonomyNode(parent_pid, parent_name)
#                 parent_node.populate_relatives("parents")
#                 self.add_parent(parent_node)
#
#     def add_child(self, child: "TaxonomyNode"):
#         self.children.append(child)
#
#     def add_parent(self, parent: "TaxonomyNode"):
#         self.parents.append(parent)


# def get_dtr_taxonomy(data_type: str, relatives: Union[str, Set[str]]) -> TaxonomyNode:
#     dtr_taxonomy_search_endpoint = f"http://typeapi.lab.pidconsortium.net/v1/taxonomy/search?query={data_type}&name={data_type}"
#     url, dtr_taxonomy_search_response, header = get(dtr_taxonomy_search_endpoint)
#     dtr_taxonomy_json = json.loads(dtr_taxonomy_search_response)
#     try:
#         root_id = dtr_taxonomy_json[0]["id"]
#         root_name = dtr_taxonomy_json[0]["name"]
#     except KeyError as error:
#         raise DataTypeNotFound(f"DataType <{data_type}> doesn't exist in the DTR taxonomy") from error
#
#     taxonomy_node = TaxonomyNode(root_id, root_name)
#     taxonomy_node.populate_relatives({"children", "parents"})
#     return taxonomy_node
