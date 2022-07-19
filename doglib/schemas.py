import json
import jsonschema
from typing import AnyStr, Callable, List, Union, Protocol
import xmlschema


class SchemaProtocol(Protocol):
    """
    Abstract interface (a protocol) for schema validator instances
    """

    def validate(self, instance) -> bool:
        ...

    def is_schema(self, schema) -> bool:
        ...


class SchemaError(Exception):
    """
    Exception risen if JSON/XML schema is not valid
    """
    def __init__(self, schema_location, message="Schema is incorrect"):
        self.schema_location = schema_location
        self.message = message 
        super().__init__(self.message)


def schema_factory(schema_location) -> Union[SchemaProtocol, None]:
    if ".xsd" in schema_location:
        return XSDSchema(schema_location)
    elif ".schema.json" in schema_location:
        return JSONSchema(schema_location)
    else:
        return None


class XSDSchema(SchemaProtocol):
    """
    Class for .xsd schema following SchemaProtocol
    """
    def __init__(self, schema_location: AnyStr):
        self.schema = xmlschema.XSDSchema(schema_location)
        if not self.schema.is_valid():
            raise SchemaError(schema_location)

    def validate(self, instance) -> bool:
        """
        Validate response
        :param instance: element tree instance
        :type instance: lxml.ETree
        :returns: is instance valid according to schema
        :rtype: Boolean
        """
        return self.schema.validate(instance)

    @classmethod
    def is_schema(cls, schema_location) -> bool:
        schema = xmlschema.XSDSchema(schema_location)
        return schema.is_valid()


class JSONSchema(SchemaProtocol):
    """
    Class for .schema.json schema following SchemaProtol
    """
    def __init__(self, schema_location: AnyStr):
        with open(schema_location, "r") as schema_file:
            try:
                self.schema = json.load(schema_file)
            except json.JSONDecodeError:
                raise SchemaError(schema_location)

    def validate(self, instance) -> bool:
        """
        Validate if instance is valid
        :param instance: element tree instance
        :type instance: Union[dict, AnyString]
        :returns: is instance valid according to schema
        :rtype: Boolean
        """
        return jsonschema.validate(instance=instance, schema=self.schema)

    @classmethod
    def is_schema(cls, schema_location) -> bool:
        with open(schema_location, "r") as schema_file:
            return bool(json.load(schema_file))
