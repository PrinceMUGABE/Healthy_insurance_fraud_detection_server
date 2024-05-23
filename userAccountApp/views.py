from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from insurancePredictionApp.models import Prediction


def get_signup_page(request):
    return render(request, "user/signup.html")
#
#


def create_user(request):
    if request.method == 'POST':
        # Get user data from the request
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        # Check if all required fields are provided
        if not all([username, email, role, password]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required'})

        # Hash the password before saving
        hashed_password = make_password(password)

        try:
            # Save the user to the database
            user = User.objects.create(username=username, email=email, role=role, password=hashed_password)
            # Send email confirmation
            subject = 'User Registration Confirmation'
            message = 'Thank you for registering with us!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            return JsonResponse({'status': 'success', 'message': 'User created successfully'})
        except IntegrityError as e:
            # Handle the case of duplicate email
            return JsonResponse({'status': 'error', 'message': str(e)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Unsupported request method'})


from django.contrib.auth.hashers import check_password

from django.contrib.auth.hashers import check_password

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print('\nUsername persisted:', username)
        print('\n\nPassword persisted: ', password)

        try:
            user = User.objects.get(username=username)
            print('\nUsername is found\n')
            if check_password(password, user.password):
                print('\nPassword is correct\n')
                # Check user role and redirect accordingly
                # Check user role and redirect accordingly
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'doctor':

                    return redirect('doctor_dashboard')
                elif user.role == 'investigator':
                    return redirect('investigator_dashboard')
                elif user.role == 'employee':
                    return redirect('employee_dashboard')
                else:
                    print('Invalid password\n')
                    messages.error(request, 'Invalid password.')
                    return render(request, "user/login.html")
        except User.DoesNotExist:
                print('Username not found\n')
                messages.error(request, 'Invalid username.')
                return render(request, "user/login.html")

    return render(request, "user/login.html")

def admin_dashboard(request):
    return render(request, 'user/adminDashboard.html')

def doctor_dashboard(request):
    # Retrieve all predictions
    predictions = Prediction.objects.all()
    return render(request, 'user/doctorDashboard.html', {'predictions': predictions})

def investigator_dashboard(request):
    return render(request, 'user/investigatorDashboard.html')


def employee_dashboard(request):
    return render(request, 'user/employeeDashboard.html')


def list_users(request):
    users = User.objects.all().values('id', 'username', 'email', 'role')  # Query only necessary fields
    return render(request, 'user/manageUsers.html', {'users': users})


def update_user_data(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        try:

            # user = User.object.get(id=id)
            user.username = username
            user.email = email
            user.role = role

            user.save()

            return redirect('user/users')
        except User.DoesNotExist:
            return redirect('user/users')


def logout_user(request):
    logout(request)
    # Redirect to a page after logout, for example, login page
    return redirect('signin')


from django.utils import timezone

def today_users(request):
    # Calculate today's date
    today = timezone.now().date()

    # Filter users created today
    users = User.objects.filter(created_date__date=today).values('username', 'email')

    # Render the template with today's users
    return render(request, 'user/manageUsers.html', {'today_users': list(users)})
