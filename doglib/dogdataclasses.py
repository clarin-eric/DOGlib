from dataclasses import dataclass
from typing import List, Union


@dataclass
class ReferencedResource:
    pid: str
    data_type: str


@dataclass
class ReferencedResources:
    """
    Referenced resources by resource type
    """
    resource_type: str
    ref_resources: List[ReferencedResource]


@dataclass
class FetchResult(dict):
    """
    Parser's fetch result serialisation
    {
        "description": str
        "license": str
        "ref_files": [ReferencedResource]
        "title": str
    }
    """
    description: Union[str, List[str]]
    license: Union[str, List[str]]
    ref_files: List[ReferencedResources]
    title: Union[str, List[str]]


@dataclass
class IdentifyResult(dict):
    """
    Parser's identify result serialisation
    {
        "description": str
        "item_title": str
        "reverse_pid": str
    }
    """
    description: Union[str, List[str]]
    item_title: str
    reverse_pid: str
