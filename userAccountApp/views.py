from django.shortcuts import get_object_or_404, render
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout, login
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import csv
import json
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import ExtractYear
from datetime import datetime, date, timedelta

from .models import User
from insurancePredictionApp.models import Insurance
from patientApp.models import Client
from insurancePredictionApp.models import Prediction

@api_view(['GET'])
def index(request):
    return Response({'message': 'Welcome to the User Management System'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    role = request.data.get('role')
    password = request.data.get('password')

    if not all([username, email, role, password]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    hashed_password = make_password(password)
    try:
        user = User.objects.create(username=username, email=email, role=role, password=hashed_password)
        subject = 'User Registration Confirmation'
        message = 'Thank you for registering with us!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_login_page(request):
    return Response({'message': 'Login page'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def signin(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            login(request, user)

            if user.role == 'admin':
                return Response({'message': 'Admin dashboard'}, status=status.HTTP_200_OK)
            elif user.role == 'doctor':
                return Response({'message': 'Doctor dashboard'}, status=status.HTTP_200_OK)
            elif user.role == 'investigator':
                return Response({'message': 'Investigator dashboard'}, status=status.HTTP_200_OK)
            elif user.role == 'employee':
                return Response({'message': 'Employee dashboard'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def doctor_dashboard(request):
    search_query = request.GET.get('search', '')

    if search_query:
        all_predictions = Prediction.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(insurance__name__icontains=search_query) |
            Q(available__icontains=search_query) |
            Q(created_date__icontains=search_query)
        )
    else:
        all_predictions = Prediction.objects.all()

    predictions_per_page = 5
    paginator = Paginator(all_predictions, predictions_per_page)
    page_number = request.GET.get('page', 1)

    try:
        predictions_page = paginator.page(page_number)
    except PageNotAnInteger:
        predictions_page = paginator.page(1)
    except EmptyPage:
        predictions_page = paginator.page(paginator.num_pages)

    predictions_by_date = (
        all_predictions
        .values('created_date')
        .annotate(count=Count('id'))
        .order_by('created_date')
    )

    dates = [entry['created_date'].strftime('%Y-%m-%d') for entry in predictions_by_date]
    counts = [entry['count'] for entry in predictions_by_date]

    data = {
        'predictions': [prediction for prediction in predictions_page],
        'search_query': search_query,
        'username': request.user.username,
        'dates': dates,
        'counts': counts
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def list_users(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(
        Q(username__icontains=search_query) | 
        Q(email__icontains=search_query) |
        Q(role__icontains=search_query)
    ).order_by('-id')

    paginator = Paginator(users, 5)
    page = request.GET.get('page')

    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    data = {
        'users': [user for user in users_page]
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
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
        return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def logout_user(request):
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def today_users(request):
    today = timezone.now().date()
    users = User.objects.filter(created_date__date=today).values('username', 'email')
    return Response({'today_users': list(users)}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_signup_page(request):
    return Response({'message': 'Create new system user'}, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def investigator_dashboard(request):
    search_query = request.GET.get('search', '')

    if search_query:
        all_predictions = Prediction.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(insurance__name__icontains=search_query) |
            Q(available__icontains=search_query) |
            Q(created_date__icontains=search_query)
        )
    else:
        all_predictions = Prediction.objects.filter(available=False)

    predictions_per_page = 5
    paginator = Paginator(all_predictions, predictions_per_page)
    page_number = request.GET.get('page', 1)

    try:
        predictions_page = paginator.page(page_number)
    except PageNotAnInteger:
        predictions_page = paginator.page(1)
    except EmptyPage:
        predictions_page = paginator.page(paginator.num_pages)

    predictions_by_date = (
        all_predictions
        .values('created_date')
        .annotate(count=Count('id'))
        .order_by('created_date')
    )

    dates = [entry['created_date'].strftime('%Y-%m-%d') for entry in predictions_by_date]
    counts = [entry['count'] for entry in predictions_by_date]

    data = {
        'predictions': [prediction for prediction in predictions_page],
        'search_query': search_query,
        'username': request.user.username,
        'dates': dates,
        'counts': counts
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def employee_dashboard(request):
    return Response({'message': 'Employee dashboard'}, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def download_users_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Users List")
    
    users = User.objects.all()
    
    p.drawString(100, 750, "Users List")
    
    y = 700
    for user in users:
        p.drawString(100, y, f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}, Created Date: {user.created_date}")
        y -= 20
        if y < 50:  # Prevent writing off the page
            p.showPage()
            y = 750
            
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="users.pdf"'
    return response

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def download_users_excel(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Role', 'Created Date'])
    
    users = User.objects.all()
    for user in users:
        writer.writerow([user.id, user.username, user.email, user.role, user.created_date])
    
    return response

@api_view(['PUT'])
@csrf_exempt
def update_user(request, user_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            user = User.objects.get(id=user_id)
            user.username = data['username']
            user.email = data['email']
            user.role = data['role']
            user.save()
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        return Response(user_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def admin_dashboard(request):
    total_users = User.objects.all().count()
    total_clients = Client.objects.all().count()
    total_insurances = Insurance.objects.all().count()
    total_false_insurances = Prediction.objects.filter(available=False).count()
    
    today = date.today()
    predictions_today = Prediction.objects.filter(created_date__date=today)

    data = {
        'total_users': total_users,
        'total_clients': total_clients,
        'total_insurances': total_insurances,
        'total_false_insurances': total_false_insurances,
        'predictions_today': [prediction for prediction in predictions_today]
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prediction_trends(request):
    start_date = datetime.now() - timedelta(days=365*5)
    
    predictions_by_year = Prediction.objects.filter(created_date__gte=start_date) \
                                            .annotate(year=ExtractYear('created_date')) \
                                            .values('year') \
                                            .annotate(count=Count('id'))
    
    labels = [str(prediction['year']) for prediction in predictions_by_year]
    counts = [prediction['count'] for prediction in predictions_by_year]
    
    data = {
        'labels': labels,
        'counts': counts
    }
    
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_predictions_today(request):
    today = date.today()

    available_predictions = Prediction.objects.filter(created_date__date=today, available=True)

    data = []
    for prediction in available_predictions:
        prediction_data = {
            'id': prediction.id,
            'insurance': prediction.insurance.name,
            'created_date': prediction.created_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        data.append(prediction_data)

    return Response(data, status=status.HTTP_200_OK)
