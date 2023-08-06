from pathlib import Path

import pytest

from pystrictconfig import FOLDER_DATA
from pystrictconfig import utils
from pystrictconfig.core import Integer


def test_read_yaml1():
    data = utils.read_yaml(Path(FOLDER_DATA, 'simple_config.yaml'))
    file = {
        'rest': {
            'url': 'https://example.org/primenumbers/v1',
            'port': 8443
        },
        'prime_numbers': [
            2, 3, 5, 7, 11, 13, 17, 19
        ],
        'prime_numbers2': [
            2, 3, 5, 7, 11, 13, 17, 19
        ]
    }

    assert data == file


def test_read_yaml2():
    schema = Integer()

    with pytest.raises(ValueError):
        utils.read_yaml(Path(FOLDER_DATA, 'simple_config.yaml'), schema)
