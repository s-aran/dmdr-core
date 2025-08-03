from __future__ import annotations

import dataclasses
import json
from django.db import models
from dataclasses import dataclass, field

# from utils import MyModelUtils
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

    null: bool

    _meta_data: MetaData = field(
        repr=False, compare=False, hash=False, init=True, metadata={"asdict": False}
    )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    def to_dixt(self) 
