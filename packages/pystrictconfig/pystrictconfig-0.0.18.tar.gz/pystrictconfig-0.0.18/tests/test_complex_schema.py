from pystrictconfig.core import List, Integer, Map, Enum, OneOf, Any, Float, String


def test_list1():
    schema = List()

    assert schema.validate([])


def test_list2():
    schema = List()

    assert schema.validate([1, 2, 3], strict=False)


def test_list3():
    schema = List()

    assert schema.validate([1, 2, 3], data_type=Integer())


def test_list4():
    schema = List()

    assert not schema.validate([1.0, 2.0, 3.0], data_type=Integer())


def test_list5():
    schema = List()

    assert schema.validate([1.0, 2.0, 3.0], data_type=Integer(strict=False))


def test_list6():
    schema = List()

    assert schema.get([1.0, 2.0, 3.0], data_type=Integer()) == [1, 2, 3]


def test_list7():
    schema = List()

    assert not schema.validate(1, data_type=Integer())


def test_map1():
    schema = Map()

    assert schema.validate({})


def test_map2():
    schema = Map()

    assert schema.validate({1: 2}, strict=False)


def test_map3():
    schema = Map()

    assert not schema.validate({1: 2})


def test_map4():
    schema = Map()

    assert not schema.validate({'nest1': 1.0}, schema={'nest1': Integer()})


def test_map5():
    schema = Map()

    assert schema.validate({'nest1': 1.0}, schema={'nest1': Integer(strict=False)})


def test_map6():
    schema = Map()

    assert not schema.validate({'nest1': 1.0}, schema={'nest1': Integer()})


def test_map7():
    schema = Map()

    assert not schema.validate({}, schema={'nest1': Integer()})


def test_map8():
    schema = Map()

    assert schema.validate({}, schema={'nest1': Integer()}, strict=False)


def test_enum1():
    schema = Enum(valid_values=[])

    assert not schema.validate(1)


def test_enum2():
    schema = Enum(valid_values=[1, 2, 3])

    assert schema.validate(1)


def test_enum3():
    schema = Enum(valid_values=range(3))

    assert schema.validate(1)


def test_enum4():
    schema = Enum(valid_values=range(3))

    assert schema.validate(None)


def test_enum5():
    schema = Enum(valid_values=range(3))

    assert not schema.validate(None, required=True)


def test_enum6():
    schema = Enum(valid_values=['1', '2', '3'])

    assert not schema.validate(1)


def test_enum7():
    schema = Enum(valid_values=['1', '2', '3'])

    assert schema.validate(1, strict=False)


def test_enum8():
    schema = Enum(valid_values=['1', 'test', '3'])

    assert schema.validate(1.0, strict=False)


def test_enum9():
    schema = Enum(valid_values=[1, None, '3'])

    assert schema.validate('1', strict=False)


def test_enum10():
    schema = Enum(valid_values=['1', None, '3'])

    assert schema.validate(None)


def test_enum11():
    schema = Enum(valid_values=['1', None, '3'])

    assert not schema.validate(None, required=True)


def test_oneof1():
    schema = OneOf()

    assert not schema.validate(1)


def test_oneof2():
    schema = OneOf(valid_types=(Any(),))

    assert schema.validate(1)


def test_oneof3():
    schema = OneOf(valid_types=(Integer(), Float()))

    assert schema.validate(1)


def test_oneof4():
    schema = OneOf(valid_types=(Float(), Integer()))

    assert schema.validate(1)


def test_oneof5():
    schema = OneOf(valid_types=(Float(), String()))

    assert not schema.validate(1)
