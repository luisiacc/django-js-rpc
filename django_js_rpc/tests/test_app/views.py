from rest_framework import viewsets
from .models import Patient, PatientVisit

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()

class PatientVisitViewSet(viewsets.ModelViewSet):
    queryset = PatientVisit.objects.all()

    def get_queryset(self):
        return self.queryset.filter(patient_id=self.kwargs['patient_id'])
