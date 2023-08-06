from pystrictconfig.core import Integer, List, Map


class SumCalculator:
    def __init__(self, values: list):
        self.values = values

    def sum(self) -> int:
        return sum(self.values)


class AvgCalculator:
    def __init__(self, values: list):
        self.values = values

    def avg(self) -> float:
        return sum(self.values) / len(self.values)


class ProductCalculator:
    def __init__(self, *values: int):
        self.values = values

    def product(self) -> int:
        prod = 1
        for value in self.values:
            prod *= value

        return prod


class Name:
    def __init__(self, firstname: str, lastname: str):
        self.firstname = firstname
        self.lastname = lastname

    def name(self) -> str:
        return f'{self.firstname} {self.lastname}'

    @staticmethod
    def build(config: dict) -> 'Name':
        return Name(config['firstname'], config['lastname'])


def test_list1():
    schema = List()
    data = range(5)

    assert schema.get(data, data_type=Integer(), as_type=SumCalculator).sum() == 10


def test_list2():
    schema = List()
    data = range(5)

    assert schema.get(data, as_type=SumCalculator).sum() == 10


def test_list3():
    schema = List()
    data = range(5)

    assert schema.get(data, strict=False, as_type=AvgCalculator).avg() == 2.0


def test_list4():
    schema = List()
    data = range(5)

    assert schema.get(data, strict=False, as_type=ProductCalculator, expand=True).product() == 0


def test_dict1():
    schema = Map()
    data = {'firstname': 'first', 'lastname': 'last'}

    assert schema.get(data, strict=False, as_type=Name.build).name() == 'first last'


def test_dict2():
    schema = Map()
    data = {'firstname': 'first', 'lastname': 'last'}

    assert schema.get(data, strict=False, expand=True, as_type=Name).name() == 'first last'
