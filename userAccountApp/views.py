from django.shortcuts import get_object_or_404, render
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout, login
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import csv
import json
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models.functions import ExtractYear
from datetime import datetime, date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken



from insurancePredictionApp.models import Insurance
from patientApp.models import Client
from insurancePredictionApp.models import Prediction


from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer
import random
import string

@api_view(['GET'])
def index(request):
    return Response({'message': 'Welcome to the User Management System'}, status=status.HTTP_200_OK)


   
    


def generate_username(first_name, last_name):
    base_username = (first_name[:3] + last_name[:2]).lower()
    random_digits = ''.join(random.choices(string.digits, k=3))
    username = (base_username + random_digits)[:8]

    while User.objects.filter(username=username).exists():
        random_digits = ''.join(random.choices(string.digits, k=3))
        username = (base_username + random_digits)[:8]

    return username

def generate_password():
    characters = string.ascii_letters + string.digits + ';'
    password = ''.join(random.choices(characters, k=8))
    return password



@api_view(['POST'])
# @permission_classes([IsAdminUser])
def create_user(request):
    data = request.data
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')

    print(f'Received data: first_name={first_name}, last_name={last_name}, \n\n email={email}, phone={phone}, role={role}')

    if not email or not email.strip():
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    # Validate and process the role field as needed
    if role not in ['employee', 'investigator', 'doctor']:
        return Response({'error': 'Invalid role specified'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    if not phone or not phone.strip():
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
    if len(phone) != 10 or not phone.isdigit():
        return Response({'error': 'Phone number must be 10 digits'}, status=status.HTTP_400_BAD_REQUEST)
    valid_prefixes = ['078', '072', '073', '079']
    if not phone.startswith(tuple(valid_prefixes)):
        return Response({'error': 'The phone number must start with one of: 078, 072, 073, 079'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(phone=phone).exists():
        return Response({'error': 'Phone number is already registered'}, status=status.HTTP_400_BAD_REQUEST)

    password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    print(f'Generated password: {password}')

    # Generate random username
    random_chars = ''.join(random.choices(string.ascii_lowercase, k=5))
    random_numbers = ''.join(random.choices(string.digits, k=3))
    username = random_chars + random_numbers
    print(f'Generated username: {username}')
    
    hashed_password = make_password(password)
   
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        username=username,
        password=hashed_password,
        role=role,
        is_active=True
    )

    # Send activation email
    subject = 'Activate Your Account'
    message = f'Hi {first_name},\n\n Welcome to FraudGuardHealth System\n Your details are:\n Username: {username}\n Password: {password}\n\n'
    from_email = 'test'
    to_email = [email]
    send_mail(subject, message, from_email, to_email, fail_silently=False)
    
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Validate the username and password
    if not username:
        return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
        return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if check_password(password, user.password):
        login(request, user)
        request.session['_last_activity'] = timezone.now().isoformat()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_info = {
            'username': user.username,
            'role': user.role,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'id': user.id,
            'phone': user.phone,
        }
        print(f'\n\n user logged in successfully as {user.role} \n\n')
        return Response(user_info)
    else:
        return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def some_protected_view(request):
    last_activity_str = request.session.get('_last_activity')
    if last_activity_str:
        last_activity = datetime.fromisoformat(last_activity_str)
        if (timezone.now() - last_activity) > timedelta(minutes=5):
            logout(request)
            return Response({'detail': 'Session expired due to inactivity.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Your view logic here
    request.session['_last_activity'] = timezone.now().isoformat()
    return Response({'message': 'You have access to this view.'})








@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def doctor_dashboard(request):
   
    all_predictions = Prediction.objects.all()
    return Response({'predictions': all_predictions}, status=status.HTTP_200_OK)



class UserPagination(PageNumberPagination):
    page_size = 5



@api_view(['GET'])
# @permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.all().values('id', 'first_name', 'last_name', 'email', 'username', 'phone', 'role')
    users_list = list(users)
    return JsonResponse({'users': users_list}, safe=False)



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

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        # Get the token from the request
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

        # Log out the user
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    predictions = Prediction.objects.filter(available=False)
    return Response({'predictions': predictions})

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
# @permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            user = User.objects.get(id=user_id)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.role = data.get('role', user.role)
            user.save()
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@csrf_exempt
# @permission_classes([IsAdminUser])
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
# @permission_classes([IsAuthenticated])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'username': user.username
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
# @permission_classes([IsAuthenticated])
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
# @permission_classes([IsAuthenticated])
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




@api_view(['POST'])
def contact_admin(request):
    email = request.data.get('email')
    email_message = request.data.get('message')
    names = request.data.get('names')
    submitted_subject = request.data.get('subject')
    

    if not email or not email_message or not names or not submitted_subject:
        return Response({'error': 'All inputs must have data.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        send_mail(
            subject=submitted_subject,
            message=email_message,
            from_email='princemugabe567@gmail.com',
            recipient_list=[email],
        )
        return Response({'message': 'Reply sent successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
from .serializers import ContactUsSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
@api_view(['POST'])
def contact_us(request):
    serializer = ContactUsSerializer(data=request.data)
    if serializer.is_valid():
        names = serializer.validated_data['name']
        email = serializer.validated_data['email']
        subject = serializer.validated_data['subject']
        description = serializer.validated_data['message']
        
        # Check for empty fields
        if not names.strip():
            return Response({"error": "Name field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not subject.strip():
            return Response({"error": "Subject field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not description.strip():
            return Response({"error": "Description field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Sending email
        send_mail(
            subject=f"Contact Us: {subject}",
            message=f"Name: {names}\nEmail: {email}\n\nDescription:\n{description}",
            from_email=email,
            recipient_list=['mandelatwah@gmail.com'],
            fail_silently=False,
        )
        return Response({"message": "Email sent successfully."}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    try:
        user = User.objects.get(email=email)
        
        # Update the user's password
        user.password = make_password(new_password)
        user.save()

        # Send email notification about the password change
        subject = 'Your Password Has Been Changed'
        message = f'Hello {user.username},\n\nYour password has been successfully changed.\n\nIf you did not request this change, please contact support immediately.'
        from_email = 'Policy-Link-Rwanda'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        print("\n\nPassword changed successfully\n\n")

        return Response({'message': 'Password reset successfully. Please check your email for confirmation.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        print('\n\nInvalid email, user does not exist\n\n')
        return Response({'error': 'Invalid username or email.'}, status=status.HTTP_400_BAD_REQUEST)
