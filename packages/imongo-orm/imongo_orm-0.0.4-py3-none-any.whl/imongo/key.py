from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Union

from imongo.types import Types


@dataclass
class Key:
    type: Types  # noqa: A003, VNE003
    required: bool = True
    default: Union[Any, None] = None
    enum: Union[List[Any], None] = None
    immutable: bool = False
    lowercase: bool = False
    uppercase: bool = False
    regex: Union[str, None] = None
    min: Union[int, None] = None  # noqa: A003, VNE003
    max: Union[int, None] = None  # noqa: A003, VNE003
    min_length: Union[int, None] = None
    max_length: Union[int, None] = None
