from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field

from meta_data import MetaData


@dataclass
class MyField:
    name: str
    column: str
    attname: str
    verbose_name: str
    help_text: str

    related_model: MetaData | None
    validators: list[str]

    null: bool

    _meta_data: MetaData = field(
        repr=False, compare=False, hash=False, init=True, metadata={"asdict": False}
    )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "column": self.column,
            "attname": self.attname,
            "verbose_name": f"{self.verbose_name}",
            "help_text": f"{self.help_text}",
            "related_model": self.related_model.to_dict()
            if self.related_model
            else None,
            "validators": self.validators,
            "null": self.null,
            "_meta_data": self._meta_data.to_dict(),
        }

        # test
        try:
            json.dumps(result)
        except TypeError as e:
            print("f" * 80)
            print(self.name)
            # ic(self)
            print("-" * 80)
            print(e)

        return result
