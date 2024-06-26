import os

import django
from django.conf import settings

os.environ["DJANGO_SETTINGS_MODULE"] = "django_js_rpc.tests.settings"


def pytest_configure():
    settings.DEBUG = False
    settings.ROOT_URLCONF = "django_js_rpc.tests.test_app.urls"
    django.setup()
