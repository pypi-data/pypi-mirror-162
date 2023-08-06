import logging
from collections import defaultdict
from typing import Any as AnyValue, Tuple, Dict, Callable, Mapping, Sequence, Iterable

from pystrictconfig import JsonLike, TypeLike


class Any:
    _as_type: TypeLike = None
    _strict: bool = True
    _required: bool = False

    def __init__(self, as_type: TypeLike = None, **config: AnyValue):
        """
        Initialize a validator class.

        @param as_type: default type of the validator
        @param config: all default values for params of validate or get methods
        """
        config['as_type'] = config.get('as_type', as_type)
        self._config = config

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        if value is None and self.required(required):
            logging.warning(f'{value} is None but it is required')

            return False
        # strict as config overrides value
        as_type = self.as_type or type(value)
        if self.strict(strict) and not isinstance(value, as_type):
            logging.warning(f'{value} is not of type {as_type}')

            return False

        return isinstance(self.get(value), as_type)

    def get(self, value: AnyValue, as_type: TypeLike = None, **config) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten
        @param as_type: type of the required value. Default to validator type.
            It may be a callable or a type. Anything that receive a value and return something.
        @param config: other configurations which may be needed by subclasses to get the value
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        if value is None:
            return None

        data_type = as_type or self.as_type

        if not data_type:
            return value

        try:
            return data_type(value)
        except (ValueError, TypeError) as e:
            logging.error(e)

            raise e

    @property
    def config(self) -> JsonLike:
        """
        Property of config given to constructor.

        @return: the configuration of the validator
        """
        return self._config

    @property
    def as_type(self) -> TypeLike:
        """
        Property of the type of the validator.

        @return: the type of the validator or the one specified to the constructor or default of the validator.
        """
        return self.config['as_type'] or self._as_type

    def strict(self, value: bool) -> bool:
        """
        Method to compute if the validator must be strict or not.

        @param value: value passed to validate method
        @return: value if value is provided to method, default of the validator otherwise
        """
        return value if value is not None else self.config.get('strict', self._strict)

    def required(self, value: bool) -> bool:
        """
        Method to compute if the value must be required or not.

        @param value: value passed to validate method
        @return: value if value is provided to method, default of the validator otherwise
        """
        return value if value is not None else self.config.get('required', self._required)


class Invalid(Any):
    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        """
        An Invalid validator which does not validate any value.

        @param value: value to be checked
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param config: other configurations which may be needed by subclasses of validator
        @return: False
        """
        return False


class Integer(Any):
    _as_type: TypeLike = int


class Float(Any):
    _as_type: TypeLike = float


class String(Any):
    _as_type: TypeLike = str


class Bool(Any):
    _as_type: TypeLike = bool

    def __init__(self,
                 as_type: TypeLike = None,
                 yes_values: Tuple[str] = ('YES', 'Y', 'SI', '1', 'TRUE'),
                 no_values: Tuple[str] = ('NO', 'N', '0', 'FALSE'),
                 **config: AnyValue):
        """
        Initialize a boolean validator.

        @param as_type: default type of the validator
        @param yes_values: string values which corresponds to true values
        @param no_values: string values which corresponds to false values
        @param config: all default values for params of validate or get methods
        """
        super().__init__(as_type=as_type, yes_values=yes_values, no_values=no_values, **config)

    def get(self, value: AnyValue, as_type: TypeLike = None, **config) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten. It is checked against true and false values.
        @param as_type: type of the required value. Default to validator type.
            It may be a callable or a type. Anything that receive a value and return something.
        @param config: other configurations which may be needed by subclasses to get the value
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        value = str(value).upper()
        if value in self.yes_values:
            value = True
        elif value in self.no_values:
            value = False

        return super().get(value, as_type=as_type)

    @property
    def yes_values(self) -> Tuple[str]:
        """
        Property of the true values of the validator.

        @return: the true values of the validator or the one specified to the constructor or default of the validator.
        """
        return self.config['yes_values']

    @property
    def no_values(self) -> Tuple[str]:
        """
        Property of the false values of the validator.

        @return: the false values of the validator or the one specified to the constructor or default of the validator.
        """
        return self.config['no_values']


class List(Any):
    _as_type: TypeLike = list

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None,
                 data_type: TypeLike = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. Each item of the sequence is checked against the data_type.
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param data_type: data type of any value of the list. If None, strict value is used to default value
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value, strict=strict, required=required):
            return False

        data_type = data_type or (Invalid() if self.strict(strict) else Any())
        for el in value:
            if not data_type.validate(el):
                return False

        return True

    def get(self, value: Sequence, as_type: TypeLike = None,
            data_type: TypeLike = Any(), expand: bool = False, **config) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten. Each item of the sequence is gotten with the data_type.
        @param as_type: type of the required value. Default to validator type.
            It may be a callable or a type. Anything that receive a value and return something.
        @param data_type: data type of any value of the list. Default no transformation on value is performed
        @param expand: if as_type value required to use star (*) expression before the call
        @param config: other configurations which may be needed by subclasses to get the value
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        value = self.as_type(value)
        if expand:
            as_type = self._builder(as_type)

        return super().get([data_type.get(el) for el in value], as_type=as_type)

    @staticmethod
    def _builder(as_type: TypeLike) -> Callable[[list], AnyValue]:
        """
        Wrapper to type to allow star expression of value.

        @param as_type: type which require star expression
        @return: wrapper to the type
        """
        def wrapper(values: list):
            return as_type(*values)
        return wrapper


class Map(Any):
    _as_type: type = dict

    def validate(self, value: Mapping, strict: bool = True, required: bool = True,
                 schema: Dict[str, Any] = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. Each value of the dictionary is checked against data_type in the schema
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param schema: schema of the dictionary. If None, strict value is used to default value
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        default_schema = Invalid() if self.strict(strict) else Any()
        schema = defaultdict(lambda: default_schema, schema or {})
        if self.strict(strict) and value.keys() != schema.keys():
            logging.warning(f'{value.keys()} has different keys with respect to {schema.keys()}')

            return False

        for key, value in value.items():
            if key not in schema:
                logging.warning(f'{key} is missing from {schema.keys()}')
            if not schema[key].validate(value):
                return False

        return True

    def get(self, value: AnyValue, as_type: TypeLike = None,
            schema: Dict[str, Any] = None, expand: bool = False, **config) -> AnyValue:
        """
        Get the value of the type required.

        @param value: value to be gotten. Each value is gotten with the data_type in the schema
        @param as_type: type of the required value. Default to validator type.
            It may be a callable or a type. Anything that receive a value and return something.
        @param schema: schema of the dictionary. Default no transformation on value is performed
        @param expand: if as_type value required to use star (**) expression before the call
        @param config: other configurations which may be needed by subclasses to get the value
        @return: the value of the required type
        @raise ValueError: if an exception occurred when creating the object
        """
        value = self.as_type(value)
        schema = schema or {key: Any() for key, value in value.items()}
        if expand:
            as_type = self._builder(as_type)

        return super().get({k: schema[k].get(value[k]) for k, v in schema.items()}, as_type=as_type)

    @staticmethod
    def _builder(as_type: TypeLike) -> Callable[[dict], AnyValue]:
        """
        Wrapper to type to allow star expression of value.

        @param as_type: type which require star expression
        @return: wrapper to the type
        """
        def wrapper(values: dict):
            return as_type(**values)
        return wrapper


class Enum(Any):

    def __init__(self, as_type: TypeLike = None, valid_values: Iterable[AnyValue] = tuple(), **config: AnyValue):
        """
        Initialize an enum validator.

        @param as_type: default type of the validator
        @param valid_values: iterable of any valid value
        @param config: all default values for params of validate or get methods
        """
        if not valid_values:
            logging.warning('No valid value provided!')
        super().__init__(as_type=as_type, valid_values=valid_values, **config)

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be one of the valid values.
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value, strict=strict, required=required):
            return False

        # if here value is None then required = False
        if value is not None:
            data_type = type(value)
            for el in self.valid_values:
                if (value == el and (type(value) == type(el))) or (not self.strict(strict) and value == data_type(el)):
                    break
            else:
                logging.warning(f'{value} is not one of {self.valid_values}')

                return False

        return True

    @property
    def valid_values(self) -> Iterable[AnyValue]:
        """
        Property of the valid values of the validator.

        @return: the valid values of the validator or the one specified to the constructor or default of the validator.
        """
        return self.config['valid_values']


class OneOf(Any):

    def __init__(self, as_type: TypeLike = None, valid_types: Iterable[Any] = tuple(), **config: AnyValue):
        """
        Initialize an enum validator.

        @param as_type: default type of the validator
        @param valid_types: iterable of any valid type
        @param config: all default values for params of validate or get methods
        """
        if not valid_types:
            logging.warning('No valid type provided!')
        super().__init__(as_type=as_type, valid_types=valid_types, **config)

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be one of the valid values.
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        for valid_type in self.valid_types:
            if valid_type.validate(value):
                break
        else:
            logging.warning(f'{value} is not one of {self.valid_types}')

            return False

        return True

    @property
    def valid_types(self) -> Iterable[Any]:
        """
        Property of the valid types of the validator.

        @return: the valid types of the validator or the one specified to the constructor or default of the validator.
        """
        return self.config['valid_types']
