#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple

import django
from django.apps import apps
from django.db.models import Model, ForeignKey, OneToOneField, ManyToManyField

from utils import MyModelUtils
from my_model import MyModel


@dataclass
class Relation:
    src_model_uuid: str
    src_model: str
    src_field_uuid: str
    src_field: str
    target_model_uuid: str
    target_model: str
    relation_type: str
    through_model_uuid: Optional[str] = None
    through_model: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def setup_django(
    project_pkg: str,
    project_root: Path,
) -> None:
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_pkg}.settings")
    django.setup()


class RelationType(Enum):
    ForeignKey = "ForeignKey"
    OneToOne = "OneToOne"
    ManyToMany = "ManyToMany"


def _relation_type_of(field) -> Optional[RelationType]:
    if isinstance(field, ManyToManyField):
        return RelationType.ManyToMany
    if isinstance(field, OneToOneField):
        return RelationType.OneToOne
    if isinstance(field, ForeignKey):
        return RelationType.ForeignKey
    return None


def inspect_models(
    project_pkg: str,
    project_root: Path,
) -> Tuple[
    List[MyModel],
    List[Relation],
]:
    setup_django(project_pkg, project_root)

    model_lookup: Dict[type[Model], MyModel] = {}
    my_models: List[MyModel] = []
    for model_cls in apps.get_models():
        my_model = MyModelUtils.from_instance(model_cls)
        my_models.append(my_model)
        model_lookup[model_cls] = my_model

    forward_map: Dict[str, Dict[str, Any]] = {}
    local_map: Dict[str, Dict[str, Any]] = {}
    relation_map: Dict[str, Dict[str, Any]] = {}
    for model_cls, my_model in model_lookup.items():
        muuid = my_model._meta_data.uuid
        forward_map[muuid] = {
            f.name: f for f in getattr(my_model, "forward_fields", [])
        }
        local_map[muuid] = {f.name: f for f in getattr(my_model, "local_fields", [])}
        relation_map[muuid] = {
            f.name: f for f in getattr(my_model, "relation_fields", [])
        }

    relations: List[Relation] = []

    for model_cls in apps.get_models():
        src_my = model_lookup[model_cls]
        src_model_uuid = src_my._meta_data.uuid
        src_model_name = src_my.object_name

        for dj_field in model_cls._meta.get_fields():
            if not getattr(dj_field, "is_relation", False):
                continue
            if getattr(dj_field, "auto_created", False):
                continue

            rtype = _relation_type_of(dj_field)
            if rtype is None:
                continue

            src_field_name = getattr(dj_field, "name", None)
            if not src_field_name:
                continue

            src_field_obj = (
                forward_map.get(src_model_uuid, {}).get(src_field_name)
                or local_map.get(src_model_uuid, {}).get(src_field_name)
                or relation_map.get(src_model_uuid, {}).get(src_field_name)
            )
            if not src_field_obj:
                continue
            src_field_uuid = src_field_obj._meta_data.uuid

            target_model_cls = getattr(dj_field, "related_model", None)
            if target_model_cls is None:
                continue
            target_model = model_lookup.get(target_model_cls)
            if target_model is None:
                continue
            target_model_uuid = target_model._meta_data.uuid
            target_model_name = target_model.object_name

            through_uuid = None
            through_name = None
            if rtype == RelationType.ManyToMany:
                remote = getattr(dj_field, "remote_field", None)
                through_cls = getattr(remote, "through", None) if remote else None
                if through_cls is not None:
                    t_my = model_lookup.get(through_cls)
                    if t_my:
                        through_uuid = t_my._meta_data.uuid
                        through_name = t_my.object_name

            relations.append(
                Relation(
                    src_model_uuid=src_model_uuid,
                    src_model=src_model_name,
                    src_field_uuid=src_field_uuid,
                    src_field=src_field_name,
                    target_model_uuid=target_model_uuid,
                    target_model=target_model_name,
                    relation_type=rtype.value,
                    through_model_uuid=through_uuid,
                    through_model=through_name,
                )
            )

    return my_models, relations


def write_structure(
    models: List[MyModel],
    relations: List[Relation],
    out_path: Path,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "models": [m.to_dict() for m in models],
        "relations": [r.to_dict() for r in relations],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) >= 3:
        project_root = Path(sys.argv[1]).resolve()
        project_pkg = sys.argv[2]

    models, relations = inspect_models(project_pkg, project_root)
    outdir = Path(__file__).resolve().parent
    write_structure(models, relations, outdir / "output.json")


if __name__ == "__main__":
    main()
