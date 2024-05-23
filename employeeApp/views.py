from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee
from insuranceApp.models import Insurance
import random
import string


# Create your views here.
def display_employees(request):
    employees = Employee.objects.all().values('id', 'employee_code', 'phone',  'email', 'insurance'
                                              , 'created_date')
    return render(request, 'employee/manageEmployees.html', {'employees':employees})


def get_create_employee_page(request):
    # Retrieve all saved insurances
    insurances = Insurance.objects.all()
    return render(request, 'employee/create_new_employee.html', {'insurances': insurances})


def save_employee(request):

    if request.method == 'POST':
        # Get form data from POST request
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        insurance_id = request.POST.get('insurance')

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

        # Redirect to the employees list page
        return redirect('employees')

    else:
        insurances = Insurance.objects.all()
        return render(request, 'employee/create_new_employee.html', {'insurances': insurances})


def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    insurances = Insurance.objects.all()
    return render(request, 'employee/edit_employee.html', {'employee': employee, 'insurances': insurances})


def update(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.employee_code = request.POST.get('code')
        employee.first_name = request.POST.get('firstname')
        employee.last_name = request.POST.get('lastname')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone')
        employee.address = request.POST.get('address')

        insurance_id = request.POST.get('insurance')
        insurance = None
        if insurance_id:
            insurance = Insurance.objects.get(pk=insurance_id)
        employee.insurance = insurance

        employee.save()

        return redirect('employees')

    else:
        insurances = Insurance.objects.all()
        return render(request, 'employee/edit_employee.html', {'employee': employee, 'insurances': insurances})


def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return redirect('employees')
