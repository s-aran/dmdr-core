#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import django
from django.apps import apps

from utils import MyModelUtils
from my_model import MyModel


class RelationType(Enum):
    ForeignKey = "ForeignKey"
    OneToOne = "OneToOne"
    ManyToMany = "ManyToMany"


@dataclass
class Relation:
    src_field: str
    target_model: str
    relation_type: RelationType
    through_field: Optional[str] = None

    def to_dict(self) -> dict:
        # Always include through_field (None will be serialized as null)
        return {
            "src_field": self.src_field,
            "target_model": self.target_model,
            "relation_type": self.relation_type.value,
            "through_field": self.through_field,
        }


@dataclass
class Output:
    models: List[MyModel]
    relations: List[Relation]

    def to_dict(self) -> dict:
        return {
            "models": [m.to_dict() for m in self.models],
            "relations": [r.to_dict() for r in self.relations],
        }


def setup_django(project_pkg: str, project_root: Path) -> None:
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_pkg}.settings")
    django.setup()


def inspect_models(project_pkg: str, project_root: Path) -> Output:
    setup_django(project_pkg, project_root)
    model_lookup: dict[type, MyModel] = {}
    models: List[MyModel] = []

    # Load all Django models into MyModel instances
    for model_cls in apps.get_models():
        my_model = MyModelUtils.from_instance(model_cls)
        models.append(my_model)
        model_lookup[model_cls] = my_model

    # Collect relations as UUID strings
    relations: List[Relation] = []
    for model_cls, my_model in model_lookup.items():
        for field in my_model.fields:
            related = field.related_model
            if not related:
                continue
            inst = field._meta_data.source
            if getattr(inst, "many_to_many", False):
                rtype = RelationType.ManyToMany
                through = getattr(inst, "through", None)
            elif getattr(inst, "one_to_one", False):
                rtype = RelationType.OneToOne
                through = None
            else:
                rtype = RelationType.ForeignKey
                through = None

            target_model = model_lookup.get(related.source)
            if not target_model:
                continue

            src_uuid = field._meta_data.uuid
            tgt_uuid = target_model._meta_data.uuid
            through_uuid = through._meta_data.uuid if through is not None else None

            relations.append(
                Relation(
                    src_field=src_uuid,
                    target_model=tgt_uuid,
                    relation_type=rtype,
                    through_field=through_uuid,
                )
            )

    return Output(models=models, relations=relations)


def write_output(output: Output, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = output.to_dict()
    with open(output_dir / "output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    # Usage: runner.py <project_root> <project_package>
    if len(sys.argv) >= 3:
        project_root = Path(sys.argv[1]).resolve()
        project_pkg = sys.argv[2]
    else:
        base = Path(__file__).resolve().parent
        project_root = base / "django-tutorial-master" / "mysite"
        project_pkg = "mysite"

    result = inspect_models(project_pkg, project_root)
    write_output(result, Path(__file__).resolve().parent)


if __name__ == "__main__":
    main()
