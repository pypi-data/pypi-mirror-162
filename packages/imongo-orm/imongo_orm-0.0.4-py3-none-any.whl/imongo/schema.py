from datetime import datetime
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import TypeVar
from typing import Union

from imongo.errors import SchemaImmutableOverwriteError
from imongo.errors import SchemaMismatchError
from imongo.key import Key
from imongo.validator import Validator

T = TypeVar("T")


class Schema:
    def __init__(self, keys: Dict[str, Key], timestamps: bool = False, validate: bool = False) -> None:
        self.keys = keys
        self.timestamps = timestamps
        self.validate = validate

    def _nested_walk(self, obj: Dict, parent: Union[List[str], None] = None) -> Generator[List[str], None, None]:
        for key, value in obj.items():
            if parent and not isinstance(value, dict):
                yield [*parent, key]

            if parent is None and not isinstance(value, dict):
                yield [key]

            if isinstance(value, dict):
                if parent is None:
                    parent = []
                yield from self._nested_walk(value, [*parent, key])

    def _get_nested_value(self, obj: Dict[str, T], keys: List[str], raise_err: bool = True) -> T:
        try:
            entry = None
            for i, key in enumerate(keys):
                if i == 0:
                    entry = obj[key]
                else:
                    entry = entry[key]  # type: ignore
            return entry  # type: ignore
        except KeyError:
            if raise_err:
                raise SchemaMismatchError(f"Key {'.'.join(keys)} not found in new entry")
            return None  # type: ignore

    def _nested_insert(self, obj: dict, value: Any, keys: List[str]) -> None:
        entry = obj
        for i, key in enumerate(keys):
            if key not in entry and i != len(keys) - 1:
                entry[key] = {}
            if key in entry or i == len(keys) - 1:
                entry[key] = value
                continue

            entry = entry[key]

    def new_entry(self, entry: Dict) -> Dict:
        if not self.validate:
            return entry

        validator = Validator()
        new_entry: Dict[str, Any] = {}
        # Validate all keys of schema and create new entry
        # A new entry obj is created to disregard extra keys provided not in schema
        for dict_keys in self._nested_walk(self.keys):
            # print(dict_keys)
            schema_key: Key = self._get_nested_value(self.keys, dict_keys)

            value = None

            # Check key exists if required
            if schema_key.required:
                value = self._get_nested_value(entry, dict_keys)

            # Fetch key if it exists
            value = value if value is not None else self._get_nested_value(entry, dict_keys, raise_err=False)
            # print(value)

            # Validate key
            if value is not None:
                modified = validator.validate(value, schema_key, dict_keys)
                self._nested_insert(new_entry, modified if modified else value, dict_keys)

            else:
                # Check if key has default value
                if schema_key.default:
                    validator.validate(schema_key.default, schema_key, dict_keys)
                    self._nested_insert(new_entry, schema_key.default, dict_keys)

        if self.timestamps:
            new_date = datetime.utcnow()
            new_entry["createdAt"] = new_date
            new_entry["updatedAt"] = new_date

        return new_entry

    def _update_key_validation(self, entry: Dict, dict_keys: List[str], update_op: str) -> None:
        validator = Validator()

        schema_key: Key = self._get_nested_value(self.keys, dict_keys)
        if schema_key.immutable:
            raise SchemaImmutableOverwriteError(f"Attemped to overwrite immutable key: {'.'.join(dict_keys[1:])}")
        value = self._get_nested_value(entry[update_op], dict_keys)
        if value:
            modified = validator.validate(value, schema_key, dict_keys)
            if modified:
                self._nested_insert(entry[update_op], modified, dict_keys)

    def update_entry(self, entry: Dict) -> Dict:
        if self.validate:

            # iterate through all keys of entry
            for update_op, update_body in entry.items():
                for dict_keys in self._nested_walk(update_body):
                    self._update_key_validation(entry, dict_keys, update_op)

        if self.timestamps:
            entry["$currentDate"] = {"updatedAt": {"$type": "date"}}

        return entry
