from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Insurance
import json
import pandas as pd

# Display insurances
def display_insurances(request):
    insurances = list(Insurance.objects.all().values('id', 'insurance_code', 'name', 'created_date'))
    return JsonResponse({'insurances': insurances})

# Get create insurance page
@csrf_exempt
def get_create_insurance_page(request):
    return JsonResponse({'message': 'Create new insurance page'})

# Save insurance
@csrf_exempt
def save_insurance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            name = data.get('name')

            if not code or not name:
                return JsonResponse({'error': 'code and name are required'}, status=400)

            # Check if the insurance code or name already exists
            if Insurance.objects.filter(insurance_code=code).exists():
                return JsonResponse({'error': 'Insurance with this code already exists'}, status=400)

            if Insurance.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Insurance with this name already exists'}, status=400)

            new_insurance = Insurance.objects.create(insurance_code=code, name=name)
            return JsonResponse({'message': 'Insurance created successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)  
    
# Edit insurance
def edit_insurance(request, insurance_id):
    insurance = Insurance.objects.filter(id=insurance_id).values('id', 'insurance_code', 'name').first()
    if insurance:
        return JsonResponse({'insurance': insurance})
    else:
        return JsonResponse({'error': 'Insurance not found'}, status=404)

# Update insurance
@csrf_exempt
def update(request, insurance_id):
    insurance = Insurance.objects.filter(id=insurance_id).first()
    if insurance:
        if request.method == 'POST':
            insurance.insurance_code = request.POST.get('code')
            insurance.name = request.POST.get('name')
            insurance.save()
            return JsonResponse({'message': 'Insurance updated successfully'})
        else:
            return JsonResponse({'error': 'POST method required'})
    else:
        return JsonResponse({'error': 'Insurance not found'}, status=404)

# Delete insurance
@csrf_exempt
def delete_insurance(request, insurance_id):
    insurance = Insurance.objects.filter(id=insurance_id).first()
    if insurance:
        insurance.delete()
        return JsonResponse({'message': 'Insurance deleted successfully'})
    else:
        return JsonResponse({'error': 'Insurance not found'}, status=404)

# Search insurance by code or name
def search_insurance(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', '')
        insurances = Insurance.objects.filter(insurance_code__icontains=search_query) | Insurance.objects.filter(name__icontains=search_query)
        count = insurances.count()
        insurances_list = list(insurances.values('id', 'insurance_code', 'name', 'created_date'))
        return JsonResponse({'count': count, 'insurances': insurances_list})
    else:
        return JsonResponse({'error': 'GET method required'})




import pandas as pd
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Insurance

def download_insurance_pdf(request):
    # Fetch insurance data
    insurances = Insurance.objects.all()
    data = [[insurance.insurance_code, insurance.name, insurance.created_date] for insurance in insurances]
    df = pd.DataFrame(data, columns=['Code', 'Name', 'Created Date'])

    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set up the PDF structure
    pdf.setTitle("Insurance Data")
    pdf.drawString(30, height - 40, "Insurance Data")

    # Create the table
    table_data = [['Code', 'Name', 'Created Date']] + data
    x_offset = 30
    y_offset = height - 60
    line_height = 20

    for row in table_data:
        y_offset -= line_height
        for item in row:
            pdf.drawString(x_offset, y_offset, str(item))
            x_offset += 150  # Adjust column width
        x_offset = 30  # Reset x offset for the next row

    pdf.showPage()
    pdf.save()

    # Get the value of the BytesIO buffer and write it to the response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="insurances.pdf"'
    return response



import pandas as pd
from django.http import HttpResponse
from .models import Insurance

def download_insurance_excel(request):
    # Fetch insurance data
    insurances = Insurance.objects.all()
    data = [[insurance.insurance_code, insurance.name, insurance.created_date] for insurance in insurances]
    df = pd.DataFrame(data, columns=['Code', 'Name', 'Created Date'])

    # Create an HttpResponse object with the appropriate Excel content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="insurances.xlsx"'

    # Use Pandas to write the data to the response as an Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Insurances')

    return response



from django.http import JsonResponse
from django.db.models import Count
from .models import Insurance
from datetime import datetime

# Increase of insurances in 2024 by each month
def increase_of_insurances(request):
    if request.method == 'GET':
        # Filter insurances created in 2024
        insurances_2024 = Insurance.objects.filter(created_date__year=2024)

        # Group insurances by month and count them
        insurances_by_month = insurances_2024.annotate(month=Count('created_date__month')).values('month').order_by('month')

        # Create a dictionary to store the monthly increase
        monthly_increase = {}

        # Calculate the increase for each month
        for item in insurances_by_month:
            month = item['month']
            month_name = datetime.strptime(str(month), "%m").strftime("%B")
            count = item['month']
            monthly_increase[month_name] = count

        return JsonResponse({'monthly_increase': monthly_increase})
    else:
        return JsonResponse({'error': 'GET method required'})
