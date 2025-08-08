#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
import json
import uuid
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import List, Optional, Dict, Tuple, Any

import django
from django.apps import apps
from django.db.models import ForeignKey, OneToOneField, ManyToManyField

from utils import MyModelUtils, MyFieldUtils

@dataclass
class Relation:
    src_model_uuid: str
    src_model: str
    src_field_uuid: str
    src_field: str
    tgt_model_uuid: str
    tgt_model: str
    relation_type: str
    through_model_uuid: Optional[str] = None
    through_model: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModelInfo:
    model_uuid: str
    app_label: str
    model_name: str
    fields: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Output:
    models: List[ModelInfo]
    relations: List[Relation]

    def to_dict(self) -> dict[str, Any]:
        return {
            "models": [m.to_dict() for m in self.models],
            "relations": [r.to_dict() for r in self.relations],
        }


def setup_django(project_pkg: str, project_root: Path) -> None:
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_pkg}.settings")
    django.setup()


class RelationType(Enum):
    ForeignKey = "ForeignKey"
    OneToOne   = "OneToOne"
    ManyToMany = "ManyToMany"


def inspect_models(project_pkg: str, project_root: Path) -> Output:
    setup_django(project_pkg, project_root)
    model_lookup: dict[type, MyModel] = {}
    models: List[MyModel] = []

    # MyModel を構築（Djangoクラス→MyModel の辞書を作る）
    for model_cls in apps.get_models():
        my_model = MyModelUtils.from_instance(model_cls)
        models.append(my_model)
        model_lookup[model_cls] = my_model

    relations: List[Relation] = []
    for model_cls, my_model in model_lookup.items():
        # ★ forward_fields のみ
        for field in my_model.forward_fields:
            # フィールドインスタンス（utils 修正で入る）
            inst = field._meta_data.source
            if inst is None:
                continue

            # 関連先 MetaData（utils 修正で MetaData | None）
            related_meta = field.related_model
            if not related_meta:
                continue

            # リレーション種別
            if getattr(inst, "many_to_many", False):
                rtype = RelationType.ManyToMany
                through_cls = getattr(inst, "through", None)
            elif getattr(inst, "one_to_one", False):
                rtype = RelationType.OneToOne
                through_cls = None
            else:
                rtype = RelationType.ForeignKey
                through_cls = None

            # 対象モデル（Djangoクラス）→ MyModel
            target_model = model_lookup.get(related_meta.source)
            if not target_model:
                continue

            # UUID を詰める
            src_uuid = field._meta_data.uuid
            tgt_uuid = target_model._meta_data.uuid

            through_uuid = None
            if through_cls:
                through_mymodel = model_lookup.get(through_cls)
                if through_mymodel:
                    through_uuid = through_mymodel._meta_data.uuid

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
    with open(output_dir / "output.json", "w", encoding="utf-8") as f:
        json.dump(output.to_dict(), f, indent=2, ensure_ascii=False)


def main():
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
