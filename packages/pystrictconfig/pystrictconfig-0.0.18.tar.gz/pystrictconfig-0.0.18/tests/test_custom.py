import os
from pathlib import Path

from pystrictconfig import FOLDER_ROOT
from pystrictconfig.custom import Port, LocalPath


def test_port1():
    schema = Port()

    assert schema.validate(1234)


def test_port2():
    schema = Port()

    assert not schema.validate(123456)


def test_port3():
    schema = Port()

    assert not schema.validate('123')


def test_port4():
    schema = Port()

    assert schema.validate('123', strict=False)


def test_path1():
    schema = LocalPath()

    assert schema.validate(Path(FOLDER_ROOT, 'src'))


def test_path2():
    schema = LocalPath()

    assert schema.validate(os.path.join(FOLDER_ROOT, 'src'))


def test_path3():
    schema = LocalPath()

    assert schema.validate(Path(FOLDER_ROOT, 'src'), exists=True)


def test_path4():
    schema = LocalPath()

    assert not schema.validate(Path(FOLDER_ROOT, 'src'), exists=False)


def test_path5():
    schema = LocalPath()

    assert schema.validate(Path(FOLDER_ROOT, 'src2'), exists=False)


def test_path6():
    schema = LocalPath()

    assert not schema.validate(Path(FOLDER_ROOT, 'src2'), exists=True)


def test_path7():
    schema = LocalPath()

    assert not schema.validate(123)
