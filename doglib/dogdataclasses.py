from dataclasses import dataclass
from typing import List, Union


@dataclass
class ReferencedResource(dict):
    pid: str
    data_type: str


@dataclass
class ReferencedResources(dict):
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
    authors: Union[str, List[str], None] = None
    description: Union[str, List[str], None] = None
    license: Union[str, List[str], None] = None
    ref_files: Union[List[ReferencedResources], None] = None
    title: Union[str, List[str], None] = None
    recognised: bool = True


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
    title: str
    reverse_pid: str
