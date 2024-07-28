from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from insuranceApp.models import Insurance

# Create your models here.

class Client(models.Model):
    # Custom validator for client code field
    client_code_validator = RegexValidator(
        regex=r'^[\w.-]+$',
        message='Enter a valid client code. This value may contain only letters, numbers, and ./- characters.'
    )

    # Custom validator for phone number field
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Enter a valid phone number.'
    )



    client_code = models.CharField(max_length=50, unique=True, validators=[client_code_validator])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    gender = models.CharField(max_length=10)
    marital_status = models.CharField(max_length=15)
    insurance = models.ForeignKey(Insurance, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100)
    picture = models.BinaryField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.client_code})"
