from __future__ import annotations

from django.db import models

from my_field import MyField
from my_model import MyModel
from meta_data import MetaData
from source_code import SourceCode


class MyModelUtils:
    @staticmethod
    def from_instance(model: type[models.Model]) -> MyModel:
        instance = model._meta

        raw_local_fields = [f for f in instance.get_fields() if not f.auto_created]
        raw_relation_fields = [f for f in instance.get_fields() if f.is_relation and f.auto_created and not f.concrete]
        raw_forward_fields = [f for f in instance.get_fields() if f.is_relation and not f.auto_created]


        return MyModel(
            app_label=instance.app_label,
            db_table=instance.db_table,
            model_name=str(instance.model_name),
            object_name=str(instance.object_name),
            local_fields=[MyFieldUtils.from_instance(f) for f in raw_local_fields],
            relation_fields=[MyFieldUtils.from_instance(f) for f in raw_relation_fields],
            forward_fields=[MyFieldUtils.from_instance(f) for f in raw_forward_fields],
            _meta_data=MetaData.make(model),
        )


class MyFieldUtils:
    @staticmethod
    def from_instance(field) -> MyField:
        instance = field

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
                null=instance.null,
                _meta_data=MetaData.make(type(instance)),
            )
        else:
            return MyField(
                name=instance.name,
                column=instance.column,
                attname=instance.attname,
                verbose_name=f"{instance.verbose_name}",
                related_model=MetaData.make(instance.related_model).uuid
                if instance.related_model
                else None,
                help_text=f"{instance.help_text}",
                validators=[
                    str(SourceCode.from_obj(type(v))) for v in instance.validators
                ],
                null=instance.null,
                _meta_data=MetaData.make(type(instance)),
            )

