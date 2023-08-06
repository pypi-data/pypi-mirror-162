import pytest

from pystrictconfig.core import Any, Integer, Float, String, Bool, Invalid


def test_any1():
    schema = Any()

    assert schema.validate(1)


def test_any2():
    schema = Any()

    assert schema.validate(False)


def test_any3():
    schema = Any()

    assert schema.validate(['test'])


def test_any4():
    schema = Any()

    assert schema.validate(None)


def test_any5():
    schema = Any()

    assert not schema.validate(None, required=True)


def test_any6():
    schema = Any(required=True)

    assert schema.validate(None, required=False)


def test_any7():
    schema = Any()

    with pytest.raises(TypeError):
        schema.get(1, as_type=object)


def test_invalid1():
    schema = Invalid()

    assert not schema.validate(1)


def test_invalid2():
    schema = Invalid()

    assert not schema.validate('test')


def test_invalid3():
    schema = Invalid()

    assert schema.get('test') == 'test'


def test_integer1():
    schema = Integer()

    assert schema.validate(1)


def test_integer2():
    schema = Integer()

    assert schema.validate(1.0, strict=False)


def test_integer3():
    schema = Integer()

    assert not schema.validate(1.0)


def test_integer4():
    schema = Integer()

    assert schema.get(1) == 1


def test_float1():
    schema = Float()

    assert schema.validate(1.0)


def test_float2():
    schema = Float()

    assert schema.validate(1, strict=False)


def test_float3():
    schema = Float()

    assert not schema.validate(1)


def test_float4():
    schema = Float()

    assert schema.get(1.0) == 1.0


def test_string1():
    schema = String()

    assert schema.validate('test')


def test_string2():
    schema = String()

    assert not schema.validate(1)


def test_string3():
    schema = String()

    assert schema.get(1) == '1'


def test_bool1():
    schema = Bool()

    assert schema.validate(True)


def test_bool2():
    schema = Bool()

    assert schema.validate(False)


def test_bool3():
    schema = Bool()

    assert not schema.validate('SI')


def test_bool4():
    schema = Bool()

    assert schema.validate('SI', strict=False)


def test_bool5():
    schema = Bool()

    assert schema.get('SI')


def test_bool6():
    schema = Bool()

    assert not schema.get('FALSE')
