from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# Create your models here.

class Insurance(models.Model):
    # Custom validator for insurance code field
    insurance_code_validator = RegexValidator(
        regex=r'^[\w.-]+$',
        message='Enter a valid insurance code. This value may contain only letters, numbers, and ./- characters.'
    )

    insurance_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=50, null=False, default='')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.insurance_code} ({self.name})"
