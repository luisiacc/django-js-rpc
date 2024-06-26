from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PatientViewSet, PatientVisitViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet)
router.register(r"patients/(?P<patient_id>\d+)/visits", PatientVisitViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
