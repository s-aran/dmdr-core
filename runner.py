from icecream import ic
import os
import sys
import django
from django import apps


def main(app_name: str, path: str | None = None):
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
    base_dir = "django-tutorial-master"
    app_name = "mysite"
    app_path = os.path.join(base_dir, app_name)

    sys.path.insert(0, app_path)

    main(app_name)
