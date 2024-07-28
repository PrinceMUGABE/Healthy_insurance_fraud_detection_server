from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.sessions.backends.db import SessionStore
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CustomInteractionTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the user is authenticated and update last interaction time
        if request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                try:
                    session = Session.objects.get(session_key=session_key)
                    session_data = session.get_decoded()
                    last_interaction_str = session_data.get('_last_activity')
                    now = timezone.now()

                    # Parse the last interaction timestamp
                    if last_interaction_str:
                        last_interaction = datetime.fromisoformat(last_interaction_str)
                    else:
                        last_interaction = None

                    # Update last interaction timestamp if it's a new session or expired
                    if not last_interaction or (now - last_interaction) > timedelta(minutes=5):
                        session_data['_last_activity'] = now.isoformat()
                        s = SessionStore(session_key=session_key)
                        s.update(session_data)
                        s.save()
                except Session.DoesNotExist:
                    pass

        # Log the authorization header for debugging
        auth_header = request.headers.get('Authorization', '')
        logger.debug(f"Authorization header: {auth_header}")

        return response



    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from userAccountApp.models import User

@receiver(post_save, sender=User)
def assign_role_permissions(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'admin':
            group, created = Group.objects.get_or_create(name='admin')
            if created:
                permissions = [
                    'can_view_dashboard',
                    'can_edit_profile',
                    'can_delete_user',
                    'can_add_user',
                    'can_update_user',
                    'can_view_users',
                    'can_reset_password',
                    'can_logout',
                    # add more permissions here
                ]
                for perm in permissions:
                    permission = Permission.objects.get(codename=perm)
                    group.permissions.add(permission)
            instance.groups.add(group)
        elif instance.role == 'employee':
            group, created = Group.objects.get_or_create(name='employee')
            if created:
                permissions = [
                    'can_view_dashboard',
                    'can_edit_profile',
                    'can_reset_password',
                    'can_logout',
                    # add more permissions here
                ]
                for perm in permissions:
                    permission = Permission.objects.get(codename=perm)
                    group.permissions.add(permission)
            instance.groups.add(group)
            
        elif instance.role == 'investigator':
            group, created = Group.objects.get_or_create(name='investigator')
            if created:
                permissions = [
                    'can_view_dashboard',
                    'can_edit_profile',
                    'can_reset_password',
                    'can_logout',
                    # add more permissions here
                ]
                for perm in permissions:
                    permission = Permission.objects.get(codename=perm)
                    group.permissions.add(permission)
            instance.groups.add(group)
            
        elif instance.role == 'doctor':
            group, created = Group.objects.get_or_create(name='doctor')
            if created:
                permissions = [
                    'can_view_dashboard',
                    'can_edit_profile',
                    'can_reset_password',
                    'can_logout',
                    # add more permissions here
                ]
                for perm in permissions:
                    permission = Permission.objects.get(codename=perm)
                    group.permissions.add(permission)
            instance.groups.add(group)
        # Add similar blocks for other roles

