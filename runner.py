from __future__ import annotations

from collections import defaultdict
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
from utils import MyModelUtils
from meta_data import MetaData


def main(app_name: str, path: str | None = None):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")

    django.setup()

    # ic(vars(apps.apps))

    all_models: list[Type[models.Model]] = apps.apps.get_models()

    models: list[MyModel] = []
    for m in all_models:
        # print(m)
        # ic(vars(m._meta))
        model = MyModelUtils.from_instance(m)
        models.append(model)

        # fields = m._meta.get_fields()
        # for f in fields:
        #     # if "_unique" in vars(f):
        #     #     print(f._unique)
        #     ic(vars(f))
        #     pass

    # ic(models)

    model_map = {str(m._meta_data.source): m for m in models}
    field_map = {}
    rel_map = {}
    for m in models:
        field_map |= {id(f._meta_data.source): f for f in m.fields}
        rel_map |= {id(f.related_model.source): f for f in m.fields if f.related_model }
        # field_map |= {str(f._meta_data.source): f for f in m.fields}
        # rel_map |= {str(f.related_model.source): f for f in m.fields if f.related_model }

        

    # ic(model_map.keys())
    # ic(field_map.keys())
    # ic(rel_map.keys())

    # ic([m._meta_data.source for m in models])
    # for m in models:
    #     for f in m.fields:
    #         if f.related_model:
    #             ic(m._meta_data.source, type(m._meta_data.source), [str(f.related_model.code)])

    rels = defaultdict(list)
    # for rk, rv in rel_map.items():
    #     rels[rk].append(field_map.get(rk))

    # for m in models:
    #     for f in m.fields:
    #         if f.related_model:
    #             rels[f.related_model.uuid] = find_relation(models, f.related_model)

    for mk, mv in model_map.items():
        ic(id(mv._meta_data.source), id(mv._meta_data.source) in rel_map.keys())


    for rk, rv in rel_map.items():
        r = rv._meta_data.source.remote_field
        if hasattr(r, "field_name"):
            ic(rv._meta_data.source.remote_field.field_name)
        else:
            if isinstance(r.field, django.db.models.ManyToManyField):
                f = r.field
                ic(r, f, f.m2m_column_name(), f.m2m_db_table(), f.m2m_field_name(), f.m2m_reverse_field_name(), f.m2m_reverse_name(), f.m2m_reverse_target_field_name(), f.m2m_target_field_name())
            else:
                ic(vars(r.field))


    ic(rels)



@dataclass
class Relation:
    src: MyField
    dest: list[MyField]

    # TODO: ManyToManyField??
    join_table: str = ""
    join_src_column: str = ""
    join_dest_column: str = ""

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

