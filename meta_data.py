from __future__ import annotations
from dataclasses import dataclass
import random
import uuid

from typing import Any
from source_code import SourceCode


@dataclass
class MetaData:
    uuid: str
    source: Any
    code: SourceCode

    @staticmethod
    def make(obj) -> MetaData:
        r = random.Random()
        r.seed(id(obj))
        u = uuid.UUID(int=r.getrandbits(128), version=4)
        return MetaData(
            uuid=f"{u}",
            source=obj,
            code=SourceCode.from_obj(obj),
        )
