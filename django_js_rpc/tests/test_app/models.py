from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=100)


class PatientVisit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
