from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .models import Insurance
import json
import pandas as pd
from django.contrib import messages

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Insurance
from django.db.models import Q

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Insurance
from .serializers import InsuranceSerializer
from django.core.paginator import Paginator


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


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def display_insurances(request):
    try:
        search_query = request.GET.get('q', '')
        insurances = Insurance.objects.filter(
            Q(insurance_code__icontains=search_query) | 
            Q(name__icontains=search_query)
        )

        paginator = Paginator(insurances, 5)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        serializer = InsuranceSerializer(page_obj, many=True)

        return Response({
            'insurances': serializer.data,
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def get_create_insurance_page(request):
    return Response({'message': 'Insurance creation page'}, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Insurance
from .serializers import InsuranceSerializer

@api_view(['POST'])
# @permission_classes([IsAdminUser])
def save_insurance(request):
    try:
        data = request.data
        code = data.get('code')
        name = data.get('name')
        owner = data.get('owner')

        if not code or not name or not owner:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if Insurance.objects.filter(insurance_code=code).exists():
            return Response({'error': 'Insurance with this code already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if Insurance.objects.filter(name=name).exists():
            return Response({'error': 'Insurance with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        new_insurance = Insurance.objects.create(insurance_code=code, name=name, owner=owner)
        serializer = InsuranceSerializer(new_insurance)
        return Response({'message': 'Insurance saved successfully', 'insurance': serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Failed to save insurance: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
   
   
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Insurance
from .serializers import InsuranceSerializer

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def edit_insurance(request, insurance_id):
    try:
        insurance = Insurance.objects.filter(id=insurance_id).values('id', 'insurance_code', 'name', 'owner').first()
        if insurance:
            serializer = InsuranceSerializer(insurance)
            return Response({'insurance': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Insurance
from .serializers import InsuranceSerializer

import logging

logger = logging.getLogger(__name__)

@api_view(['PUT'])
# @permission_classes([IsAdminUser])
def update(request, insurance_id):
    try:
        insurance = Insurance.objects.filter(id=insurance_id).first()
        if insurance:
            data = request.data
            insurance.insurance_code = data.get('insurance_code')
            insurance.name = data.get('name')
            insurance.owner = data.get('owner')
            insurance.save()
            serializer = InsuranceSerializer(insurance)
            return Response({'message': 'Insurance updated successfully', 'insurance': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating insurance: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Insurance

@api_view(['DELETE'])
def delete_insurance(request, insurance_id):
    try:
        insurance = Insurance.objects.filter(id=insurance_id).first()
        if insurance:
            insurance.delete()
            return Response({'message': 'Insurance deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Insurance not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

from django.http import HttpResponse
from .models import Insurance
import pandas as pd

def download_insurance_excel(request):
    # Fetch insurance data
    insurances = Insurance.objects.all()
    data = [
        [insurance.insurance_code, insurance.name, insurance.created_date.replace(tzinfo=None)] 
        for insurance in insurances
    ]
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
