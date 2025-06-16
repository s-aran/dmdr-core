from __future__ import annotations

import json

import inspect

from dataclasses import dataclass
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

@dataclass
class MyField:
    name: str
    column: str
    attname: str
    verbose_name: str

    related_model_name: str
    validators: list[str]

    @staticmethod
    def get_filename_and_lines(obj)->str:
        # ic(vars(type(obj)))
        fl = inspect.getsourcefile(type(obj))
        _, ln = inspect.getsourcelines(type(obj))

        return f"{fl}:L{ln}"

    @staticmethod
    def from_instance(field) -> MyField:
        instance = field
        # ic(vars(instance))

        if isinstance(field, models.ManyToOneRel) or isinstance(field, models.ManyToManyRel):
            return MyField(
                    name=instance.name,
                    column="",
                    attname="",
                    verbose_name="",
                    related_model_name="",
                    validators=[],
                )
        else:
            return MyField(
                    name=instance.name,
                    column=instance.column,
                    attname=instance.attname,
                    verbose_name=instance.verbose_name,
                    related_model_name=str(instance.related_model or ""),
                    validators=[MyField.get_filename_and_lines(v) for v in instance.validators],
                )

    def __str__(self) -> str:
        json.dumps(dataclass.asdict(self))

    
@dataclass
class MyModel:
    app_label: str
    db_table: str
    model_name: str
    object_name: str
    fields: list[MyField]

    @staticmethod
    def from_instance(model: Model)->MyModel:
        instance = model._meta
        # ic(vars(instance))

        return MyModel(
                app_label=instance.app_label,
                db_table=instance.db_table,
                model_name=instance.model_name,
                object_name=instance.object_name,
                fields=[MyField.from_instance(f) for f in instance.get_fields()]
                )

    def __str__(self) -> str:
        json.dumps(dataclass.asdict(self))



@dataclass
class Relation:
    ...


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

