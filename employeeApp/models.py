from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from insuranceApp.models import Insurance



# Create your models here.
class Employee(models.Model):
    # Custom validator for employee code field
    employee_code_validator = RegexValidator(
        regex=r'^[\w.-]+$',
        message='Enter a valid employee code. This value may contain only letters, numbers, and ./- characters.'
    )

    # Custom validator for phone number field
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Enter a valid phone number.'
    )

    # Custom validator for email field
    email_validator = RegexValidator(
        regex=r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$',
        message='Enter a valid email address.'
    )

    employee_code = models.CharField(max_length=50, unique=True, validators=[employee_code_validator])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=255, validators=[email_validator])
    phone = models.CharField(max_length=15, validators=[phone_validator], unique=True)
    address = models.CharField(max_length=255)
    insurance = models.ForeignKey(Insurance, on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_code})"