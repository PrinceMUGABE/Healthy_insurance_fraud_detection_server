from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password

class User(models.Model):
    # Define choices for user roles
    USER_ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('investigator', 'Investigator'),
        ('employee', 'Employee'),
    )

    # Custom validator for username field
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'
    )

    username = models.CharField(max_length=100, validators=[username_validator], unique=True)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=100)  # Saving only hashed password
    role = models.CharField(max_length=30, choices=USER_ROLE_CHOICES, default='user')
    last_login = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)  # New field for storing creation date

    # def save(self, *args, **kwargs):
    #     # Hash the password before saving
    #     if self.password:
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
