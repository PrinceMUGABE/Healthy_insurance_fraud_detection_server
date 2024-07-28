from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee
from insuranceApp.models import Insurance
import random
import string
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Employee

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Employee
from django.db.models import Q
import datetime
from collections import Counter

from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from collections import Counter
from .models import Employee
from datetime import datetime

from django.core import serializers
from django.http import JsonResponse
from django.db.models import Q
from collections import Counter
from .models import Employee

def display_employees(request):
    query = request.GET.get('q')
    if query:
        employee_list = Employee.objects.filter(
            Q(employee_code__icontains=query) |
            Q(email__icontains=query) |
            Q(insurance__name__icontains=query)
        ).select_related('insurance')  # Ensure insurance data is fetched in the query
    else:
        employee_list = Employee.objects.all().select_related('insurance')

    # Serialize queryset
    serialized_data = serializers.serialize('json', employee_list, use_natural_foreign_keys=True)

    return JsonResponse({'employees': serialized_data})




from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Insurance

@api_view(['GET'])
def get_create_employee_page(request):
    try:
        insurances = Insurance.objects.all().values('id', 'insurance_code', 'name')
        insurances_list = list(insurances)
        return Response({'insurances': insurances_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from insuranceApp.models import Insurance
from userAccountApp.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail

@api_view(['POST'])
# @permission_classes([IsAdminUser])
def save_employee(request):
    try:
        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        insurance_id = data.get('insurance')

        # Generate employee code
        random_numbers = ''.join(random.choices(string.digits, k=3))
        random_chars = ''.join(random.choices(string.ascii_letters, k=2))
        employee_code = f"{phone[:2]}{random_numbers}{random_chars}"

        # Get insurance instance
        insurance = None
        if insurance_id:
            insurance = Insurance.objects.get(pk=insurance_id)

        # Create and save the employee instance
        employee = Employee.objects.create(
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            insurance=insurance
        )

        # Generate unique username
        while True:
            random_numbers = ''.join(random.choices(string.digits, k=3))
            random_chars = ''.join(random.choices(string.ascii_letters, k=5))
            username = f"{random_chars}{random_numbers}"
            if not User.objects.filter(username=username).exists():
                break

        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Save user credentials to User model
        hashed_password = make_password(password)
        user = User.objects.create(
            username=username,
            email=email,
            password=hashed_password,
            role='employee'
        )

        # Send email with credentials
        subject = 'Your Account Credentials'
        message = f'Hello {first_name},\n\nThank you for registering with us. Here are your account credentials:\n\nUsername: {username}\nPassword: {password}\n\nPlease keep this information secure.'
        from_email = 'no-reply@gmail.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Employee saved successfully'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Insurance
from userAccountApp.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from insuranceApp.models import Insurance
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def get_employee(request, id):
    try:
        employee = Employee.objects.get(pk=id)
        insurances = Insurance.objects.all()
        
        employee_data = {
            "id": employee.pk,
            "employee_code": employee.employee_code,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "phone": employee.phone,
            "address": employee.address,
            "insurance": employee.insurance.pk if employee.insurance else None
        }
        
       
        insurances_data = [
            {
                "id": insurance.pk,
                "insurance_code": insurance.insurance_code,
                "name": insurance.name
            } for insurance in insurances
        ]
        
        return JsonResponse({"employee": employee_data, "insurances": insurances_data})
    except Employee.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)


@api_view(['PUT'])
# @permission_classes([IsAdminUser])
def update_employee(request, employee_id):
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        data = request.data
        employee.first_name = data.get('first_name')
        employee.last_name = data.get('last_name')
        employee.email = data.get('email')
        employee.phone = data.get('phone')
        employee.address = data.get('address')

        insurance_id = data.get('insurance')
        insurance = None
        if insurance_id:
            insurance = Insurance.objects.get(pk=insurance_id)
        employee.insurance = insurance

        employee.save()
        employee_data = {
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'phone': employee.phone,
            'address': employee.address,
            'insurance': employee.insurance.id if employee.insurance else None
        }
        return Response({'message': 'Employee updated successfully', 'employee': employee_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['DELETE'])
# @permission_classes([IsAdminUser])
def delete_employee(request, employee_id):
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        employee.delete()
        return Response({'message': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.utils.timezone import localtime
from .models import Employee

def download_employees_pdf(request):
    # Retrieve employees from the database
    employees = Employee.objects.all()

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employees.pdf"'

    # Create PDF document
    pdf = SimpleDocTemplate(response, pagesize=letter)
    data = []

    # Define table headers
    table_headers = ["ID", "Code", "Phone", "Email", "Insurance", "Created Date"]

    # Add headers to data
    data.append(table_headers)

    # Add employee data to table
    for employee in employees:
        employee_data = [
            employee.id,
            employee.employee_code,
            employee.phone,
            employee.email,
            employee.insurance.name if employee.insurance else "N/A",
            localtime(employee.created_date).strftime('%Y-%m-%d %H:%M:%S')
        ]
        data.append(employee_data)

    # Create table and style
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    # Add table to the PDF document
    elements = []
    elements.append(table)
    pdf.build(elements)

    return response



from openpyxl import Workbook
from django.http import HttpResponse
from django.utils.timezone import localtime
from .models import Employee

def download_employees_excel(request):
    # Retrieve employees from the database
    employees = Employee.objects.all()

    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active

    # Define column headers
    headers = ["ID", "Code", "Phone", "Email", "Insurance", "Created Date"]

    # Write headers to the first row
    ws.append(headers)

    # Write employee data to the Excel sheet
    for employee in employees:
        employee_data = [
            employee.id,
            employee.employee_code,
            employee.phone,
            employee.email,
            employee.insurance.name if employee.insurance else "N/A",
            localtime(employee.created_date).strftime('%Y-%m-%d %H:%M:%S')
        ]
        ws.append(employee_data)

    # Save the workbook to a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
    wb.save(response)

    return response
