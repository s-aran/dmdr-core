from icecream import ic
import os
import sys
import django
from django import apps


def main(app_name: str):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")

    django.setup()

    # ic(vars(apps.apps))
    
    all_models = apps.apps.get_models()

    for m in all_models:
        fields = m._meta.get_fields()
        for f in fields:
            # if "_unique" in vars(f):
            #     print(f._unique)
            ic(vars(f))

if __name__ == "__main__":
    main("mysite")
