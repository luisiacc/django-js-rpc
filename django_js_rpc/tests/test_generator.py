import os

import pytest
from django.apps import apps
from django.test import override_settings
from django.urls import include, path

from django_js_rpc.generator import TypeScriptAPIGenerator


@pytest.fixture
def generator():
    return TypeScriptAPIGenerator()


@pytest.fixture
def test_app_urls():
    return [
        path("api/", include("django_js_rpc.tests.test_app.urls")),
    ]


@pytest.mark.urls("django_js_rpc.tests.test_app.urls")
def test_analyze_views(generator):
    views = generator.analyze_views()

    assert "PatientViewSet" in views
    assert "PatientVisitViewSet" in views

    patient_view = views["PatientViewSet"]
    assert set(patient_view["methods"]) == {"list", "create", "retrieve", "update", "partial_update", "destroy"}
    assert patient_view["path"] == r"^patients/(?:(?P<pk>[^/.]+)/)?$"
    assert patient_view["params"] == ["pk"]

    visit_view = views["PatientVisitViewSet"]
    assert set(visit_view["methods"]) == {"list", "create", "retrieve", "update", "partial_update", "destroy"}
    assert visit_view["path"] == r"^patients/(?P<patient_id>[^/.]+)/visits/(?:(?P<pk>[^/.]+)/)?$"
    assert set(visit_view["params"]) == {"patient_id", "pk"}


def test_generate_typescript(generator):
    views = {
        "PatientViewSet": {
            "methods": ["list", "create", "retrieve", "update", "partial_update", "destroy"],
            "path": r"^patients/(?:(?P<pk>[^/.]+)/)?$",
            "params": ["pk"],
        },
        "PatientVisitViewSet": {
            "methods": ["list", "create", "retrieve", "update", "partial_update", "destroy"],
            "path": r"^patients/(?P<patient_id>[^/.]+)/visits/(?:(?P<pk>[^/.]+)/)?$",
            "params": ["patient_id", "pk"],
        },
    }

    typescript_code = generator.generate_typescript(views)

    assert "class RpcClient" in typescript_code
    assert "patient = {" in typescript_code
    assert "patientvisit = {" in typescript_code

    # Check for correct parameter handling
    assert "query: (pk: string, options?: any)" in typescript_code
    assert "query: (patient_id: string, pk: string, options?: any)" in typescript_code


@override_settings(JS_RPC_OUTPUT_DIR="test_output")
def test_app_config_ready():
    # Manually run the ready method
    app_config = apps.get_app_config("django_js_rpc")
    app_config.ready()

    # Check if the file was generated
    assert os.path.exists("test_output/rpcClient.ts")

    # Clean up
    os.remove("test_output/rpcClient.ts")
    os.rmdir("test_output")
