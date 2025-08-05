from __future__ import annotations
from dataclasses import dataclass
import inspect
import types


@dataclass
class SourceCode:
    source_file: str
    partial: list[str]
    line_number: int

    @staticmethod
    def from_obj(obj) -> SourceCode:
        if isinstance(obj, types.FunctionType):
            fl = "<build-in function>"
            partial, ln = ["<build-in function>"], 0
        else:
            fl = str(inspect.getsourcefile(type(obj)))
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

    def to_dict(self) -> dict:
        result = {
            "source_file": self.source_file,
            "partial": self.partial,
            "line_number": self.line_number,
        }

        return result
