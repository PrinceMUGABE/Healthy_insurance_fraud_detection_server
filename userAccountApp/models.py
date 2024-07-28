from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timedelta

class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('doctor', 'Doctor'),
        ('investigator', "Investigator"),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Define related_name to avoid clashes with auth.User's groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username
    
    class Meta:
        permissions = (
            ("can_view_dashboard", "Can view dashboard"),
            ("can_edit_profile", "Can edit profile"),
            ("can_add_user", "Can add user"),
            ("can_view_users", "Can view users"),
            ("can_delete_user", "Can delete user"),
            ("can_update_user", "Can update user"),
            ("can_reset_password", "Can reset password"),
            ("is_doctor", "Is doctor"),
            ("is_investigator", "Is investigator"),
            ("is_admin", "Is admin"),
            ("is_employee", "Is employee"),
            ("can_logout", "Can logout"),
            # add more custom permissions here
        )
    
    
