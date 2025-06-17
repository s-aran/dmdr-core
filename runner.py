from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type
from icecream import ic
import os
import sys
import django
from django import apps
from django.db import models

from my_field import MyField
from my_model import MyModel


def main(app_name: str, path: str | None = None):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")

    django.setup()

    # ic(vars(apps.apps))

    all_models: list[Type[models.Model]] = apps.apps.get_models()

    models: list[MyModel] = []
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
