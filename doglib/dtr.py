import json

from .curl import get


class DataTypeRegistryResolver:
    def __init__(self):
        pass


def expand_datatype(data_type: str):
    # TODO expose config for easy DTR access
    dtr_base_url = "http://typeregistry.lab.pidconsortium.net/search?query=/name:"
    dtr_query_endpoint = f'{dtr_base_url}{data_type}'

    taxonomy_dict: dict = {data_type: {}}
    url, dtr_query_response, header = get(dtr_query_endpoint)

    dtr_query_response = json.loads(dtr_query_response)
    for result in dtr_query_response["results"]:
        content = result["content"]
        if 'properties' in content.keys():
            properties = content['properties']
            for _property in properties:
                property_name = _property['name']
                taxonomy_dict[data_type] = expand_datatype(property_name)
    return taxonomy_dict
