from __future__ import annotations
from dataclasses import dataclass
import inspect


@dataclass
class SourceCode:
    source_file: str
    partial: str
    line_number: int

    @staticmethod
    def from_obj(obj) -> SourceCode:
        fl = inspect.getsourcefile(type(obj))
        partial, ln = inspect.getsourcelines(type(obj))

        return SourceCode(
            source_file=fl,
            partial=partial,
            line_number=ln,
        )

    def __str__(self) -> str:
        fl = self.source_file
        ln = self.line_number
        return f"{fl}:L{ln}"
