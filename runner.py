# from __future__ import annotations
#
# from collections import defaultdict
# from dataclasses import dataclass, field
# from typing import Type
# from icecream import ic
# import os
# import sys
# import django
# from django import apps
# from django.db import models
#
# from my_field import MyField
# from my_model import MyModel
# from utils import MyModelUtils
# from meta_data import MetaData
#
#
# def main(app_name: str, path: str | None = None) -> Output:
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")
#
#     django.setup()
#
#     # ic(vars(apps.apps))
#
#     all_models: list[Type[models.Model]] = apps.apps.get_models()
#
#     models: list[MyModel] = []
#     for m in all_models:
#         # print(m)
#         # ic(vars(m._meta))
#         model = MyModelUtils.from_instance(m)
#         models.append(model)
#
#         # fields = m._meta.get_fields()
#         # for f in fields:
#         #     # if "_unique" in vars(f):
#         #     #     print(f._unique)
#         #     ic(vars(f))
#         #     pass
#
#     # ic(models)
#
#     model_map = {str(m._meta_data.source): m for m in models}
#     field_map = {}
#     rel_map = {}
#     for m in models:
#         field_map |= {id(f._meta_data.source): f for f in m.fields}
#         rel_map |= {id(f.related_model.source): f for f in m.fields if f.related_model }
#         # field_map |= {str(f._meta_data.source): f for f in m.fields}
#         # rel_map |= {str(f.related_model.source): f for f in m.fields if f.related_model }
#
#
#
#     # ic(model_map.keys())
#     # ic(field_map.keys())
#     # ic(rel_map.keys())
#
#     # ic([m._meta_data.source for m in models])
#     # for m in models:
#     #     for f in m.fields:
#     #         if f.related_model:
#     #             ic(m._meta_data.source, type(m._meta_data.source), [str(f.related_model.code)])
#
#     rels = defaultdict(list)
#     # for rk, rv in rel_map.items():
#     #     rels[rk].append(field_map.get(rk))
#
#     # for m in models:
#     #     for f in m.fields:
#     #         if f.related_model:
#     #             rels[f.related_model.uuid] = find_relation(models, f.related_model)
#
#     for mk, mv in model_map.items():
#         ic(id(mv._meta_data.source), id(mv._meta_data.source) in rel_map.keys())
#
#
#     for rk, rv in rel_map.items():
#         r = rv._meta_data.source.remote_field
#         if hasattr(r, "field_name"):
#             ic(rv._meta_data.source.remote_field.field_name)
#         else:
#             if isinstance(r.field, django.db.models.ManyToManyField):
#                 f = r.field
#                 ic(r, f, f.m2m_column_name(), f.m2m_db_table(), f.m2m_field_name(), f.m2m_reverse_field_name(), f.m2m_reverse_name(), f.m2m_reverse_target_field_name(), f.m2m_target_field_name())
#             else:
#                 ic(vars(r.field))
#
#     ic(rels)
#
#     result = Output(models, rels)
#     return result
#
#
# @dataclass
# class Relation:
#     src: MyField
#     dest: list[MyField]
#
#     # TODO: ManyToManyField??
#     join_table: str = ""
#     join_src_column: str = ""
#     join_dest_column: str = ""
#
# @dataclass
# class Output:
#     models: list[MyModel]
#     relations: list[Relation]
#
#
# if __name__ == "__main__":
#     base_dir = "django-tutorial-master"
#     app_name = "mysite"
#     app_path = os.path.join(base_dir, app_name)
#
#     sys.path.insert(0, app_path)
#
#     main(app_name)
#
#


# from __future__ import annotations
# from enum import StrEnum
# import os
# import sys
# from pathlib import Path
# from dataclasses import asdict, dataclass, is_dataclass
# from typing import List
#
# import django
# from django.apps import apps
# from django.db.models import ObjectDoesNotExist
# from icecream import ic
#
# import msgspec
# from meta_data import MetaData
# from utils import MyModelUtils
# from my_model import MyModel
# from my_field import MyField
#
#
# def setup_django(project_pkg: str, project_root: Path):
#     """setup django
#
#     Args:
#         project_pkg: python package
#         project_root: settings.py directory path
#     """
#
#     sys.path.insert(0, str(project_root))
#
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_pkg}.settings")
#
#     django.setup()
#
#
# class RelationType(StrEnum):
#     ForeignKey = "ForeignKey"
#     OneToOne = "OneToOne"
#     ManyToMany = "ManyToMany"
#
#
# @dataclass
# class Relation:
#     src_field: MyField  # source field
#     target_model: MyModel  # ref
#     relation_type: RelationType
#     through_field: MyField | None = None  # ManyToMany
#
#
# @dataclass
# class Output:
#     models: List[MyModel]
#     relations: List[Relation]
#
#
# def inspect_models(project_pkg: str, project_root: Path) -> Output:
#     """inspect models and return Output object."""
#
#     setup_django(project_pkg, project_root)
#
#     model_objs: list[MyModel] = []
#     relations: list[Relation] = []
#     model_lookup: dict[str, MyModel] = {}
#
#     for model_cls in apps.get_models():
#         my_model: MyModel = MyModelUtils.from_instance(model_cls)
#         model_objs.append(my_model)
#         model_lookup[my_model._meta_data.uuid] = my_model
#
#         # extract relation from fields
#         for f in my_model.fields:
#             if f.related_model is None:
#                 continue
#
#             orig_field = f._meta_data.source
#             remote = getattr(orig_field, "remote_field", None)
#             if remote is None:
#                 continue
#
#             if getattr(remote, "many_to_many", False):
#                 rel_type = RelationType.ManyToMany
#             elif getattr(remote, "one_to_one", False):
#                 rel_type = RelationType.OneToOne
#             else:
#                 rel_type = RelationType.ForeignKey
#
#             target = model_lookup.get(f.related_model.uuid)
#             if target is None:
#                 target = MyModelUtils.from_instance(f.related_model.source)
#                 model_objs.append(target)
#                 model_lookup[target._meta_data.uuid] = target
#
#             relations.append(
#                 Relation(
#                     src_field=f,
#                     target_model=target,
#                     relation_type=rel_type,
#                     through_field=None,  # set after if ManyToMany
#                 )
#             )
#
#     return Output(models=model_objs, relations=relations)


from __future__ import annotations
from enum import StrEnum
import os
import pickle
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Type
from django.conf import settings
from icecream import ic

import django
from django.apps import apps

import msgspec
from meta_data import MetaData
from utils import MyModelUtils
from my_model import MyModel
from my_field import MyField
import json


def setup_django(project_pkg: str, project_root: Path):
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_pkg}.settings")
    django.setup()


class RelationType(StrEnum):
    ForeignKey = "ForeignKey"
    OneToOne = "OneToOne"
    ManyToMany = "ManyToMany"


@dataclass
class Relation:
    src_field: MyField
    target_model: MyModel
    relation_type: RelationType
    through_field: MyField | None = None

    def to_dict(self) -> dict:
        result = {
            "src_field": self.src_field.to_dict(),
            "target_model": self.target_model.to_dict(),
            "relation_type": self.relation_type.value,
            "through_field": self.through_field.to_dict()
            if self.through_field
            else None,
        }

        return result


@dataclass
class Output:
    models: List[MyModel]
    relations: List[Relation]

    def to_dict(self) -> dict:
        result = {
            "models": [m.to_dict() for m in self.models],
            "relations": [r.to_dict() for r in self.relations],
        }

        return result


def inspect_models(project_pkg: str, project_root: Path) -> Output:
    setup_django(project_pkg, project_root)

    model_objs: List[MyModel] = []
    relations: List[Relation] = []
    model_lookup: dict[str, MyModel] = {}
    # プレースホルダーに後で埋めるためのリスト
    pending_fill: List[Tuple[MyModel, Type[django.db.models.Model]]] = []

    # ① まず既存モデルを一度全部 from_instance して登録
    for model_cls in apps.get_models():
        my_model = MyModelUtils.from_instance(model_cls)
        model_objs.append(my_model)
        model_lookup[my_model._meta_data.uuid] = my_model

    # ② 各 MyModel のフィールドを見て Relation を収集
    for my_model in list(model_objs):
        for f in my_model.fields:
            # related_model がなければスキップ
            if f.related_model is None:
                continue

            # orig_field = f._meta_data.source を使わず remote_field 取得
            remote = getattr(f._meta_data.source, "remote_field", None)
            # もし source が None (プレースホルダー) の場合は model_lookup から取る
            if remote is None and hasattr(f, "related_model"):
                # f._meta_data.source がまだ None のプレースホルダーなら
                # apps.get_model から再取得して remote_field だけ見る
                dummy = f.related_model
                remote = getattr(dummy, "remote_field", None)
            if remote is None:
                continue

            # カーディナリティ判定
            if getattr(remote, "many_to_many", False):
                rel_type = RelationType.ManyToMany
            elif getattr(remote, "one_to_one", False):
                rel_type = RelationType.OneToOne
            else:
                rel_type = RelationType.ForeignKey

            # ターゲットモデルを lookup（未登録ならプレースホルダー作成）
            uuid = f.related_model.uuid
            target = model_lookup.get(uuid)
            if target is None:
                # source=None のプレースホルダー
                placeholder = MyModel(
                    _meta_data=MetaData(uuid=uuid, source=None),
                    # 必要なら name, app_label など最低限の属性セット
                )
                model_objs.append(placeholder)
                model_lookup[uuid] = placeholder
                pending_fill.append((placeholder, f.related_model))
                target = placeholder

            # Relation を追加
            relations.append(
                Relation(
                    src_field=f,
                    target_model=target,
                    relation_type=rel_type,
                    through_field=None,  # ManyToMany の場合はあとで設定可
                )
            )

    # ③ プレースホルダーに実データをまとめて埋め戻す
    for placeholder, model_cls in pending_fill:
        real = MyModelUtils.from_instance(model_cls)
        # meta_data と fields をマージ or 上書き
        placeholder._meta_data.source = real._meta_data.source
        placeholder.fields = real.fields

    return Output(models=model_objs, relations=relations)


def print_relations_ascii(output: Output, max_width: int = 60):
    for rel in output.relations:
        src = f"{rel.src_field.name}@{rel.src_field._meta_data.source.model.__name__}"
        tgt = rel.target_model.object_name
        line = f"{src} -> {tgt} ({rel.relation_type})"

        if len(line) > max_width:
            line = line[: max_width - 3] + "..."
        print(line)


def write(output: Output, output_dir: Path):
    output_dir.mkdir(exist_ok=True)

    data = output.to_dict()

    with open("output.json", mode="w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load(path: Path) -> Output:
    from django.conf import settings

    settings.configure(
        USE_I18N=False,
    )

    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = BASE_DIR / "django-tutorial-master" / "mysite"
    PROJECT_PKG = "mysite"

    # result = inspect_models(PROJECT_PKG, PROJECT_ROOT)
    result = load(Path("data.pickled"))

    # print_relations_ascii(result)
    write(result, Path("."))
