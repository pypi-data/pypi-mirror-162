import re
from typing import Any
from typing import List
from typing import Union

from imongo.errors import SchemaDataTypeMismatchError
from imongo.key import Key
from imongo.types import Types
from imongo.validator.type_validations import TYPE_VALIDATIONS


class Validator:
    def __init__(self) -> None:
        pass

    def _valid_types(self, value: Any, key: Key, key_ref: List[str]) -> None:
        if not isinstance(key.type, Types):
            raise TypeError(f"Key={'.'.join(key_ref)} has an invalid type")

        # Validate Type
        if not TYPE_VALIDATIONS[key.type](value):
            raise SchemaDataTypeMismatchError(f"Value: {value} does not match expected type [{key.type}]. Key={'.'.join(key_ref)}")

    def _valid_enum(self, value: Any, key: Key, key_ref: List[str]) -> None:
        if key.enum:
            str_enum = [str(x) for x in key.enum]
            if value not in key.enum:
                raise SchemaDataTypeMismatchError(f"Value: {value} does not match expected enum [{', '.join(str_enum)}]. Key={'.'.join(key_ref)}")

    def _valid_numeric(self, value: Any, key: Key, key_ref: List[str]) -> None:
        if key.type in [Types.Integer, Types.Long, Types.Double]:
            if key.min and key.min > value:
                raise SchemaDataTypeMismatchError(f"Value: {value} is less than expected minimum [{key.min}]. Key={'.'.join(key_ref)}")
            if key.max and key.max < value:
                raise SchemaDataTypeMismatchError(f"Value: {value} is greater than expected maximum [{key.max}]. Key={'.'.join(key_ref)}")

    def _valid_string(self, value: Any, key: Key, key_ref: List[str]) -> None:
        if key.type in [Types.String]:
            if key.min_length and key.min_length > len(value):
                raise SchemaDataTypeMismatchError(f"Value: {value} is less than expected minimum length [{key.min_length}]. Key={'.'.join(key_ref)}")
            if key.max_length and key.max_length < len(value):
                raise SchemaDataTypeMismatchError(
                    f"Value: {value} is greater than expected maximum length [{key.max_length}]. Key={'.'.join(key_ref)}"
                )
            if key.regex and not re.match(key.regex, value):
                raise SchemaDataTypeMismatchError(f"Value: {value} does not match expected regex. Key={'.'.join(key_ref)}")

    def validate(self, value: Any, key: Key, key_ref: List[str]) -> Union[None, Any]:
        self._valid_types(value, key, key_ref)
        self._valid_enum(value, key, key_ref)
        self._valid_numeric(value, key, key_ref)
        self._valid_string(value, key, key_ref)

        # Inline transformation for lower/upper case strings
        if key.type in [Types.String]:
            if key.lowercase:
                return value.lower()
            if key.uppercase:
                return value.upper()

        return None
