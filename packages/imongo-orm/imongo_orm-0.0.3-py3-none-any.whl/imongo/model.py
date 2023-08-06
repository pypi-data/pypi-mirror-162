from typing import Any
from typing import Callable
from typing import Dict

from bson.objectid import ObjectId
from pymongo import MongoClient

from .schema import Schema


class Model:
    def __init__(self, name: str, schema: Schema) -> None:
        self.name = name
        self.schema = schema

    def register_client(self, client: MongoClient, db_name: str = "helloworld") -> None:
        self._client = client
        self.db_name = db_name

    def __getattr__(self, name):  # noqa : CFQ004
        # Regular exit for Model class methods
        if name in ["register_client"]:
            return super().__getattribute__(name)

        # Attempting to get method from MongoClient
        db = self._client[self.db_name]
        collection = db[self.name]
        res = collection.__getattribute__(name)

        if res:
            if name not in [
                "update_one",
                "delete_one",
                "find_one",
                "find",
                "update_many",
                "delete_many",
            ]:
                return res

            # Modified method for injecting ObjectId and validating updates
            @self._integrate_mongo_id
            def modified_fcn(*args, **kwargs) -> Any:
                new_args = args
                if name in ["update_one", "update_many"]:
                    new_args = tuple([args[0], self.schema.update_entry(args[1])])
                return res(*new_args, **kwargs)

            return modified_fcn

        return super().__getattribute__(name)

    def __call__(self, entry: Dict) -> Any:
        return self.schema.new_entry(entry)

    def _integrate_mongo_id(self, main_method: Callable) -> Callable:
        def run(*args, **kwargs) -> None:
            new_args = tuple([self._inject_mongo_id(args[0])] + list(args[1:]))
            return main_method(*new_args, **kwargs)

        return run

    def _inject_mongo_id(self, entry: Dict) -> Dict:
        if "_id" in entry:
            entry["_id"] = ObjectId(entry["_id"])
        return entry
