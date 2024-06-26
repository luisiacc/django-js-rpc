from setuptools import find_packages, setup

setup(
    name="django-js-rpc",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.0",
        "djangorestframework>=3.11",
        "Jinja2>=2.11",
    ],
    entry_points={
        "django.apps": [
            "django_js_rpc = django_js_rpc.apps.DjangoTsApiGeneratorConfig",
        ],
    },
)
