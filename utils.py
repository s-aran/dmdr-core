from __future__ import annotations

from django.db import models

from my_field import MyField
from my_model import MyModel
from meta_data import MetaData
from source_code import SourceCode


class MyModelUtils:
    @staticmethod
    def from_instance(model: models.Model) -> MyModel:
        instance = model._meta
        # ic(vars(instance))

        return MyModel(
            app_label=instance.app_label,
            db_table=instance.db_table,
            model_name=instance.model_name,
            object_name=instance.object_name,
            fields=[MyFieldUtils.from_instance(f) for f in instance.get_fields()],
            _meta_data=MetaData.make(model),
        )


class MyFieldUtils:
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
                null=instance.null,
                _meta_data=MetaData.make(field),
            )
        else:
            # if instance.related_model:
            #     from icecream import ic
            #     ic(id(instance.related_model))
            #     m = MetaData.make(instance.related_model)
            #     ic(m.uuid)

            return MyField(
                name=instance.name,
                column=instance.column,
                attname=instance.attname,
                verbose_name=f"{instance.verbose_name}",
                related_model=MetaData.make(instance.related_model)
                if instance.related_model
                else None,
                help_text=f"{instance.help_text}",
                validators=[str(SourceCode.from_obj(v)) for v in instance.validators],
                null=instance.null,
                _meta_data=MetaData.make(field),
            )
