from __future__ import annotations

import dataclasses
import json
from django.db import models
from dataclasses import dataclass, field

from meta_data import MetaData
from my_field import MyField


@dataclass
class MyModel:
    app_label: str
    db_table: str
    model_name: str
    object_name: str
    fields: list[MyField]

    _meta_data: MetaData = field(
        repr=False, compare=False, hash=False, init=True, metadata={"asdict": False}
    )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    def to_dict(self) -> dict:
        result = {
                "app_label": self.app_label,
                "db_table": self.db_table,
                "model_name":self.model_name,
                "object_name": self.object_name,
                "fields": [f.to_dict() for f in self.fields],
                "_meta_data": self._meta_data.to_dict(),
                }
        return result

