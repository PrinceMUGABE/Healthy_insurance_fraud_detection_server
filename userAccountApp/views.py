from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.utils import timezone
from .models import User
from insurancePredictionApp.models import Prediction
from insuranceApp.models import Insurance
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def create_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    role = request.data.get('role')
    password = request.data.get('password')

    if not all([username, email, role, password]):
        return Response({'status': 'error', 'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    hashed_password = make_password(password)
    try:
        user = User.objects.create(username=username, email=email, role=role, password=hashed_password)
        subject = 'User Registration Confirmation'
        message = 'Thank you for registering with us!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        return Response({'status': 'success', 'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def signin(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            if user.role == 'admin':
                return Response({'redirect': 'admin_dashboard'}, status=status.HTTP_200_OK)
            elif user.role == 'doctor':
                return Response({'redirect': 'doctor_dashboard'}, status=status.HTTP_200_OK)
            elif user.role == 'investigator':
                return Response({'redirect': 'investigator_dashboard'}, status=status.HTTP_200_OK)
            elif user.role == 'employee':
                return Response({'redirect': 'employee_dashboard'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'status': 'error', 'message': 'Invalid username.'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def doctor_dashboard(request):
    predictions = Prediction.objects.all()
    return Response({'predictions': [prediction.id for prediction in predictions]}, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_users(request):
    users = User.objects.all().values('id', 'username', 'email', 'role')
    return Response({'users': list(users)}, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_user_data(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    username = request.data.get('username')
    email = request.data.get('email')
    role = request.data.get('role')

    try:
        user.username = username
        user.email = email
        user.role = role
        user.save()
        return Response({'status': 'success', 'message': 'User updated successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'status': 'error', 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'status': 'success', 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def today_users(request):
    today = timezone.now().date()
    users = User.objects.filter(created_date__date=today).values('username', 'email')
    return Response({'today_users': list(users)}, status=status.HTTP_200_OK)




from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def admin_dashboard(request):
    data = {
        "message": "Admin Dashboard Data",
        # Add more relevant data here
    }
    return Response(data)

@api_view(['GET'])
def get_signup_page(request):
    data = {
        "message": "Signup Page Data",
        # Add more relevant data here
    }
    return Response(data)

@api_view(['GET'])
def index(request):
    data = {
        "message": "Index Page Data",
        # Add more relevant data here
    }
    return Response(data)

@api_view(['GET'])
def investigator_dashboard(request):
    data = {
        "message": "Investigator Dashboard Data",
        # Add more relevant data here
    }
    return Response(data)

@api_view(['GET'])
def employee_dashboard(request):
    data = {
        "message": "Employee Dashboard Data",
        # Add more relevant data here
    }
    return Response(data)
