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

    @staticmethod
    def from_instance(model: models.Model) -> MyModel:
        instance = model._meta
        # ic(vars(instance))

        return MyModel(
            app_label=instance.app_label,
            db_table=instance.db_table,
            model_name=instance.model_name,
            object_name=instance.object_name,
            fields=[MyField.from_instance(f) for f in instance.get_fields()],
            _meta_data=MetaData.make(model),
        )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self))
