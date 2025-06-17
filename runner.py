from __future__ import annotations

import uuid

import inspect
import dataclasses
from dataclasses import dataclass, field
from icecream import ic
import os
import sys
import django
from django import apps
from django.db import models


def main(app_name: str, path: str | None = None):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")

    django.setup()

    # ic(vars(apps.apps))

    all_models = apps.apps.get_models()

    models = []
    for m in all_models:
        # print(m)
        # ic(vars(m._meta))
        model = MyModel.from_instance(m)
        models.append(model)

        # fields = m._meta.get_fields()
        # for f in fields:
        #     # if "_unique" in vars(f):
        #     #     print(f._unique)
        #     ic(vars(f))
        #     pass

    ic(models)

    rels = []

    for m in models:
        for f in m.fields:
            f.related_model


def find_relation(models: list[MyModel], field: MyField) -> list[MyField]:
    result = []

    for m in models:
        for f in m.fields:
            # f.
            pass


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


@dataclass
class MetaData:
    uuid: str
    source: SourceCode

    @staticmethod
    def make(obj) -> MetaData:
        return MetaData(
            uuid=uuid.uuid4(),
            source=SourceCode.from_obj(obj),
        )


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
        json.dumps(dataclasses.asdict(self))


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
    def from_instance(model: Model) -> MyModel:
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
        json.dumps(dataclasses.asdict(self))


@dataclass
class Relation: ...


@dataclass
class Output:
    models: list[MyModel]
    relations: list[Relation]


if __name__ == "__main__":
    base_dir = "django-tutorial-master"
    app_name = "mysite"
    app_path = os.path.join(base_dir, app_name)

    sys.path.insert(0, app_path)

    main(app_name)
