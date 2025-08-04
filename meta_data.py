from __future__ import annotations
import json
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

    def to_dict(self) -> dict:
        result = {
            "uuid": self.uuid,
            "source": None,
            "code": self.code.to_dict(),
        }

        # test
        try:
            json.dumps(result)
        except TypeError as e:
            print("*" * 80)
            print(self.uuid)
            print(e)

        return result
