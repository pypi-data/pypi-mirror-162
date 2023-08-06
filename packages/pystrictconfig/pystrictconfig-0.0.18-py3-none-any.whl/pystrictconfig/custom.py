from pathlib import Path
from typing import Any as AnyValue, Iterable

from pystrictconfig import TypeLike
from pystrictconfig.core import Integer, OneOf, Any, String


class Port(Integer):
    def validate(self, value: AnyValue, strict: bool = None, required: bool = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be an integer between 0 and 65535.
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value, strict=strict, required=required):
            return False

        value = self.get(value)

        return 0 <= value <= 65535


class LocalPath(OneOf):
    _as_type: TypeLike = Path

    def __init__(self, as_type: TypeLike = None,
                 valid_types: Iterable[Any] = (String(), String(as_type=Path)), **config: AnyValue):
        """
        Initialize an enum validator.

        @param as_type: default type of the validator
        @param valid_types: iterable of any valid type
        @param config: all default values for params of validate or get methods
        """
        super().__init__(as_type=as_type, valid_types=valid_types, **config)

    def validate(self, value: AnyValue, strict: bool = None, required: bool = None,
                 exists: bool = None, **config) -> bool:
        """
        Validate a value against the validator.

        @param value: value to be checked. It needs to be one of the valid values.
        @param strict: if value must be of the same type as required by the validator or any subtypes or equivalent type
        @param required: if value must be different from None
        @param exists: if the path must or not exists. None if no existence condition is required
        @param config: other configurations which may be needed by subclasses of validator
        @return: True if value is compliant to validator, False otherwise
        """
        if not super().validate(value, strict=strict, required=required):
            return False

        path = self.get(value)

        if path.exists() and (exists is not None and not exists):
            return False
        if not path.exists() and exists:
            return False

        return True
