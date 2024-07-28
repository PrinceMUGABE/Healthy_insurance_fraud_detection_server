from django.db import models
from django.utils import timezone
from insuranceApp.models import Insurance

class Prediction(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=6)
    marital_status = models.CharField(max_length=15)
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    picture = models.BinaryField(null=True, blank=True)
    available = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.insurance.name}"
