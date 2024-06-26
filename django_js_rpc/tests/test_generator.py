import os

import pytest
from django.test import override_settings
from django.urls import clear_url_caches, reverse

from django_js_rpc.generator import TypeScriptAPIGenerator


@pytest.fixture
def generator():
    return TypeScriptAPIGenerator()


@pytest.mark.django_db
def test_analyze_views(generator):
    clear_url_caches()
    reverse("patient-list")
    reverse("patient-visit-list", kwargs={"patient_id": 1})

    views = generator.analyze_views()

    assert "patient" in views, "PatientViewSet not found in analyzed views"
    assert "patientvisit" in views, "PatientVisitViewSet not found in analyzed views"

    patient_view = views["patient"]
    assert set(patient_view["methods"]) == {"list", "create", "retrieve", "update", "partial_update", "destroy"}
    assert "patients/${pk}" in patient_view["path"], f"Unexpected path: {patient_view['path']}"
    assert "pk" in patient_view["params"]

    visit_view = views["patientvisit"]
    assert set(visit_view["methods"]) == {"list", "create", "retrieve", "update", "partial_update", "destroy"}
    assert "patients/${patient_id}/visits/${pk}" in visit_view["path"], f"Unexpected path: {visit_view['path']}"
    assert "patient_id" in visit_view["params"] and "pk" in visit_view["params"]


def test_generate_typescript(generator):
    views = {
        "patient": {
            "methods": ["list", "create", "retrieve", "update", "partial_update", "destroy"],
            "path": "/api/patients/${pk}/",
            "params": ["pk"],
        },
        "patientvisit": {
            "methods": ["list", "create", "retrieve", "update", "partial_update", "destroy"],
            "path": "/api/patients/${patient_id}/visits/${pk}/",
            "params": ["patient_id", "pk"],
        },
    }

    typescript_code = generator.generate_typescript(views)

    assert "class RpcClient" in typescript_code
    assert "patient = {" in typescript_code
    assert "patientvisit = {" in typescript_code

    # Check for reverse function usage
    assert "url: (pk: string) => this.reverse('/api/patients/${pk}/', { pk })" in typescript_code
    assert (
        "url: (patient_id: string, pk: string) => this.reverse('/api/patients/${patient_id}/visits/${pk}/', { patient_id, pk })"
        in typescript_code
    )

    # Check for query methods
    assert "query: (options?: any) =>" in typescript_code
    assert "query: (id: string, options?: any) =>" in typescript_code

    # Check for mutation methods
    assert "mutation: (options?: any) =>" in typescript_code


@override_settings(JS_RPC_OUTPUT_DIR="test_output")
def test_app_config_ready():
    os.remove("test_output/rpcClient.ts")
    os.rmdir("test_output")
    from django.apps import apps

    app_config = apps.get_app_config("django_js_rpc")
    app_config.ready()

    assert os.path.exists("test_output/rpcClient.ts")

