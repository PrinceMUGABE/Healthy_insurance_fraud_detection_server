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

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed')
    ]

    client_code = models.CharField(max_length=50, unique=True, validators=[client_code_validator])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, validators=[phone_validator], unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES)
    insurance = models.ForeignKey(Insurance, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100)
    picture = models.BinaryField(null=True, blank=True)
    face_encodings = models.TextField(null=True, blank=True)  # Store face encodings as text
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.client_code})"
