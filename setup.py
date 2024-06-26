from setuptools import find_packages, setup

setup(
    name="django-js-rpc",
    version="0.1",
    packages=find_packages(include=["django_js_rpc", "django_js_rpc.*"]),
    include_package_data=True,
    install_requires=[
        "Django>=3.0",
        "djangorestframework>=3.11",
        "Jinja2>=2.11",
    ],
    extras_require={
        "test": [
            "pytest>=6.2.3",
            "pytest-django>=4.2.0",
        ],
    },
    entry_points={
        "django.apps": [
            "django_js_rpc = django_js_rpc.apps.DjangoJsRpcConfig",
        ],
    },
)
