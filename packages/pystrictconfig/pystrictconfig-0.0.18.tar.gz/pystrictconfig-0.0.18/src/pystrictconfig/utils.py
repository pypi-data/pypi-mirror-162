from pathlib import Path
import yaml

from pystrictconfig import JsonLike
from pystrictconfig.core import Any


def read_yaml(path: str | Path, schema: Any = Any()) -> JsonLike:
    """
    Read a yaml file with a schema.

    @param path: path to a yaml file
    @param schema: schema of the yaml file
    @return: the content of the file with respect to the schema
    """
    with open(path, 'r') as f:
        value = yaml.safe_load(f)
        if schema.validate(value):
            return schema.get(value)

        raise ValueError
