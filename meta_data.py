from __future__ import annotations
from dataclasses import dataclass
import uuid

from source_code import SourceCode


@dataclass
class MetaData:
    uuid: str
    source: SourceCode

    @staticmethod
    def make(obj) -> MetaData:
        return MetaData(
            uuid=f"{uuid.uuid4()}",
            source=SourceCode.from_obj(obj),
        )
