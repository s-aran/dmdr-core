from __future__ import annotations

import dataclasses
import json
from django.db import models
from dataclasses import dataclass, field

from meta_data import MetaData
from source_code import SourceCode


@dataclass
class MyField:
    name: str
    column: str
    attname: str
    verbose_name: str
    help_text: str

    related_model: MetaData | None
    validators: list[str]

    _meta_data: MetaData = field(
        repr=False, compare=False, hash=False, init=True, metadata={"asdict": False}
    )

    @staticmethod
    def from_instance(field) -> MyField:
        instance = field
        # ic(vars(instance))

        if isinstance(field, models.ManyToOneRel) or isinstance(
            field, models.ManyToManyRel
        ):
            return MyField(
                name=instance.name,
                column="",
                attname="",
                verbose_name="",
                related_model=None,
                help_text="",
                validators=[],
                _meta_data=MetaData.make(field),
            )
        else:
            return MyField(
                name=instance.name,
                column=instance.column,
                attname=instance.attname,
                verbose_name=instance.verbose_name,
                related_model=MetaData.make(instance.related_model)
                if instance.related_model
                else None,
                help_text=instance.help_text,
                validators=[str(SourceCode.from_obj(v)) for v in instance.validators],
                _meta_data=MetaData.make(field),
            )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self))
