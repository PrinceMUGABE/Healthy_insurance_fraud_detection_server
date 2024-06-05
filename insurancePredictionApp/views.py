from django.conf import settings
from django.contrib import messages
from .models import Prediction
from insuranceApp.models import Insurance
from sklearn.feature_extraction.text import TfidfVectorizer
from django.shortcuts import render, redirect
from patientApp.models import Client
from django.shortcuts import render, redirect
from django.contrib import messages
import base64

import cv2
import numpy as np
from PIL import Image
import imagehash
import os
import base64
import cv2
import numpy as np
from django.http import HttpResponse
from PIL import Image
import imagehash
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import face_recognition

from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Prediction
from .serializers import PredictionSerializer
from django.db.models import Q
from insuranceApp.serializers import InsuranceSerializer


import os

model_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'models')




# View to return total available predictions
from django.http import JsonResponse
from .models import Prediction

from django.http import JsonResponse
from .models import Prediction

def total_available_predictions(request):
    total_available = Prediction.objects.all().count()
    total_frauded = Prediction.objects.filter(available=False).count()
    total_valid = Prediction.objects.filter(available=True).count()
    return JsonResponse({'total_available_predictions': total_available, 'total_frauded': total_frauded, 'total_valid': total_valid})




# View to return institution predictions by status
from django.http import JsonResponse
from django.db.models import Count
from .models import Prediction

from django.http import JsonResponse
from django.db.models import Count
from .models import Prediction

def institution_predictions(request):
    institution_data = Prediction.objects.values('insurance__name', 'available').annotate(prediction_count=Count('id'))

    institution_counts = {}
    for data in institution_data:
        insurance_name = data['insurance__name']
        available = data['available']
        prediction_count = data['prediction_count']

        if insurance_name not in institution_counts:
            institution_counts[insurance_name] = {'True': 0, 'False': 0}

        if available:
            institution_counts[insurance_name]['True'] = prediction_count
        else:
            institution_counts[insurance_name]['False'] = prediction_count

    return JsonResponse(institution_counts)





# Initialize TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render
from .models import Prediction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Prediction
from .serializers import PredictionSerializer
from django.core.paginator import Paginator

@api_view(['GET'])
def display_predictions(request):
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

    serializer = PredictionSerializer(predictions_page, many=True)

    return Response({
        'predictions': serializer.data,
        'page': predictions_page.number,
        'num_pages': paginator.num_pages,
        'has_next': predictions_page.has_next(),
        'has_previous': predictions_page.has_previous(),
    }, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Insurance
from insuranceApp.serializers import InsuranceSerializer

@api_view(['GET'])
def get_create_prediction_page(request):
    insurances = Insurance.objects.all()
    serializer = InsuranceSerializer(insurances, many=True)
    return Response({'insurances': serializer.data}, status=status.HTTP_200_OK)





import base64
import os
import random
import string
import traceback
import cv2
import face_recognition
import numpy as np
from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from patientApp.models import Client  # Import your Client model
from .models import Prediction

# Assuming BASE_DIR is defined somewhere in your settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_high_quality(image):
    height, width = image.shape[:2]
    min_resolution = (200, 200)  # Minimum resolution for a high-quality image
    return width >= min_resolution[0] and height >= min_resolution[1]

def retrieve_submitted_pictures():
    submitted_pictures_folder = os.path.join(BASE_DIR, 'templates', 'static', 'submitted_pictures')
    picture_files = [filename for filename in os.listdir(submitted_pictures_folder) if filename.endswith('.jpg')]
    return picture_files

def compare_images_content(submitted_picture, existing_pictures):
    # Convert submitted picture to RGB
    submitted_picture_rgb = cv2.cvtColor(submitted_picture, cv2.COLOR_BGR2RGB)

    # Encode faces in the submitted picture
    submitted_encodings = face_recognition.face_encodings(submitted_picture_rgb)

    if not submitted_encodings:
        print("No faces found in the submitted picture.")
        return False

    # Load face encodings for existing pictures
    existing_encodings = []
    for existing_picture in existing_pictures:
        # Check if the existing picture has high enough quality
        if not is_high_quality(existing_picture):
            print(f"Skipping low-quality existing picture: {existing_picture}")
            continue

        existing_picture_rgb = cv2.cvtColor(existing_picture, cv2.COLOR_BGR2RGB)
        existing_encoding = face_recognition.face_encodings(existing_picture_rgb)

        if existing_encoding:
            existing_encodings.append(existing_encoding[0])
        else:
            print(f"No faces found in existing picture: {existing_picture}")

    if not existing_encodings:
        print("No faces found in any high-quality existing pictures.")
        return False

    # Compare face encodings
    for encoding in existing_encodings:
        results = face_recognition.compare_faces(submitted_encodings, encoding)
        if True in results:
            return True

    return False


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import base64
import cv2
import numpy as np
import random
import string
import os
import traceback
from .models import Prediction
from patientApp.models import Client

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

@api_view(['POST'])
def save_prediction(request):
    try:
        data = request.data
        first_name = data.get('firstname')
        last_name = data.get('lastname')
        phone = data.get('phone')
        gender = data.get('gender')
        marital_status = data.get('marital_status')
        insurance_id = data.get('insurance')
        address = data.get('address')
        picture_data = data.get('picture')

        gender_map = {
            'Male': 'M',
            'Female': 'F',
            'Other': 'O'
        }

        marital_status_map = {
            'Single': 'S',
            'Married': 'M',
            'Divorced': 'D',
            'Widowed': 'W',
            'Other': 'O'
        }

        gender_code = gender_map.get(gender)
        marital_status_code = marital_status_map.get(marital_status)

        if picture_data:
            picture_bytes = base64.b64decode(picture_data.split(',')[1])
            submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

            if submitted_image is None:
                prediction = Prediction(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    gender=gender_code,
                    marital_status=marital_status_code,
                    insurance_id=insurance_id,
                    address=address,
                    available=False
                )
                prediction.save()
                return Response({'error': 'Submitted image could not be read.'}, status=status.HTTP_400_BAD_REQUEST)

            if not is_high_quality(submitted_image):
                prediction = Prediction(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    gender=gender_code,
                    marital_status=marital_status_code,
                    insurance_id=insurance_id,
                    address=address,
                    available=False
                )
                prediction.save()
                return Response({'error': 'Image quality is too low. Please submit a higher quality image.'}, status=status.HTTP_400_BAD_REQUEST)

            face_locations = face_recognition.face_locations(submitted_image)
            if not face_locations:
                prediction = Prediction(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    gender=gender_code,
                    marital_status=marital_status_code,
                    insurance_id=insurance_id,
                    address=address,
                    available=False
                )
                prediction.save()
                return Response({'error': 'No faces detected in the image. Please submit a picture containing a face.'}, status=status.HTTP_400_BAD_REQUEST)

            phone_suffix = phone[-3:]
            last_name_prefix = last_name[:2].upper()
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            client_code = f"{phone_suffix}{last_name_prefix}{random_suffix}"
            picture_name = f"{client_code}.jpg"

            retrieved_pictures_folder = os.path.join(BASE_DIR, 'templates', 'static', 'retrieved_pictures')
            if not os.path.exists(retrieved_pictures_folder):
                os.makedirs(retrieved_pictures_folder)
            picture_path = os.path.join(retrieved_pictures_folder, picture_name)

            fs = FileSystemStorage(location=retrieved_pictures_folder)
            filename = fs.save(picture_name, ContentFile(picture_bytes))

            prediction_success = False
            submitted_pictures = retrieve_submitted_pictures()

            for submitted_picture_path in submitted_pictures:
                if submitted_picture_path.endswith('.jpg'):
                    stored_image_path = os.path.join(BASE_DIR, 'templates', 'static', 'submitted_pictures', submitted_picture_path)
                    stored_image_contents = cv2.imread(stored_image_path)

                    if stored_image_contents is not None:
                        is_similar = compare_images_content(submitted_image, [stored_image_contents])

                        if is_similar:
                            client_code = submitted_picture_path[:5]
                            client_query = Client.objects.filter(client_code__startswith=client_code)

                            if client_query.exists():
                                client = client_query.first()

                                if (client.first_name == first_name and
                                        client.last_name == last_name and
                                        client.phone == phone and
                                        client.gender == gender_code and
                                        client.marital_status == marital_status_code and
                                        str(client.insurance.id) == insurance_id):
                                    prediction_success = True
                                    break

            prediction = Prediction(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                gender=gender_code,
                marital_status=marital_status_code,
                insurance_id=insurance_id,
                address=address,
                picture=filename,
                available=prediction_success
            )
            prediction.save()

            if not prediction_success:
                return Response({'error': 'No matching picture found'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Prediction matched successfully.'}, status=status.HTTP_201_CREATED)

        else:
            prediction = Prediction(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                gender=gender_code,
                marital_status=marital_status_code,
                insurance_id=insurance_id,
                address=address,
                available=False
            )
            prediction.save()
            return Response({'error': 'No image data received.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        prediction = Prediction(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            gender=gender_code,
            marital_status=marital_status_code,
            insurance_id=insurance_id,
            address=address,
            available=False
        )
        prediction.save()
        return Response({'error': f'Error during image processing: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PredictionSerializer
from django.db.models import Q





from django.http import JsonResponse
from django.db.models import Q
from .models import Prediction

def search_predictions(request):
    search_query = request.GET.get('search', '')
    predictions = Prediction.objects.filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(phone__icontains=search_query) |
        Q(insurance__name__icontains=search_query) |
        Q(available__icontains=search_query) |
        Q(created_date__icontains=search_query)
    )
    predictions_data = [
        {
            'id': prediction.id,
            'first_name': prediction.first_name,
            'last_name': prediction.last_name,
            'phone': prediction.phone,
            'insurance': prediction.insurance.name,
            'available': prediction.available,
            'created_date': prediction.created_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        for prediction in predictions
    ]
    return JsonResponse(predictions_data, safe=False)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Prediction

@csrf_exempt
def delete_prediction(request, prediction_id):
    try:
        # Retrieve the prediction object to be deleted
        prediction = Prediction.objects.get(pk=prediction_id)
        
        # Delete the prediction from the database
        prediction.delete()
        
        # Return a success response
        return JsonResponse({'message': 'Prediction deleted successfully'}, status=200)
    
    except Prediction.DoesNotExist:
        # If the prediction does not exist, return a 404 error
        return JsonResponse({'error': 'Prediction not found'}, status=404)
    
    except Exception as e:
        # If any other error occurs, return an error response
        return JsonResponse({'error': str(e)}, status=500)




from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from openpyxl import Workbook
from django.utils.timezone import localtime
from .models import Prediction

def download_predictions_pdf(request):
    # Retrieve predictions from the database
    predictions = Prediction.objects.all()

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="predictions.pdf"'

    # Create PDF document
    pdf = SimpleDocTemplate(response, pagesize=letter)
    data = []

    # Define table headers
    table_headers = ["First Name", "Last Name", "Phone", "Gender", "Marital Status", "Insurance", "Status", "Address", "Created Date"]

    # Add headers to data
    data.append(table_headers)

    # Add prediction data to table
    for prediction in predictions:
        prediction_data = [
            prediction.first_name,
            prediction.last_name,
            prediction.phone,
            prediction.get_gender_display(),
            prediction.get_marital_status_display(),
            prediction.insurance.name,
            prediction.available,
            prediction.address,
            localtime(prediction.created_date).strftime('%Y-%m-%d %H:%M:%S')
        ]
        data.append(prediction_data)

    # Create table and style
    table = Table(data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Add table to the PDF document
    elements = []
    elements.append(table)
    pdf.build(elements)

    return response


def download_predictions_excel(request):
    # Retrieve predictions from the database
    predictions = Prediction.objects.all()

    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active

    # Define column headers
    headers = ["First Name", "Last Name", "Phone", "Gender", "Marital Status", "Insurance", "Status", "Address", "Created Date"]

    # Write headers to the first row
    ws.append(headers)

    # Write prediction data to the Excel sheet
    for prediction in predictions:
        prediction_data = [
            prediction.first_name,
            prediction.last_name,
            prediction.phone,
            prediction.get_gender_display(),
            prediction.get_marital_status_display(),
            prediction.insurance.name,
            "Available" if prediction.available else "Not Available",
            prediction.address,
            localtime(prediction.created_date).strftime('%Y-%m-%d %H:%M:%S')
        ]
        ws.append(prediction_data)

    # Save the workbook to a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="predictions.xlsx"'
    wb.save(response)

    return response






from django.http import JsonResponse
from .models import Prediction

def total_available_predictions(request):
    # Query the database for predictions where 'available' is True and count them
    total_available = Prediction.objects.all().count()
    total_frauded = Prediction.objects.filter(available=False).count()
    total_valid = Prediction.objects.filter(available=True).count()

    # Return the count as a JSON response
    return JsonResponse({'total_available_predictions': total_available, '\nTotal frauded Insurance': total_frauded, '\nTotal valid Insurance': total_valid})




from django.http import JsonResponse
from django.db.models import Count
from .models import Prediction
from datetime import datetime, timedelta

def increase_of_predictions_2024(request):
    # Filter predictions created in 2024
    predictions_2024 = Prediction.objects.filter(created_date__year=2024)

    # Group predictions by month and count them
    predictions_by_month_2024 = predictions_2024.annotate(month=Count('created_date__month')).values('month').order_by('month')

    # Create a dictionary to store the monthly increase
    monthly_increase_2024 = {}

    # Calculate the increase for each month
    for item in predictions_by_month_2024:
        month = item['month']
        month_name = datetime.strptime(str(month), "%m").strftime("%B")
        count = item['month']
        monthly_increase_2024[month_name] = count

    return JsonResponse({'monthly_increase_2024': monthly_increase_2024})

def increase_of_predictions_last_5_years(request):
    # Get current year
    current_year = datetime.now().year

    # Calculate the starting year for the last 5 years
    start_year = current_year - 5

    # Filter predictions created in the last 5 years
    predictions_last_5_years = Prediction.objects.filter(created_date__year__range=[start_year, current_year])

    # Group predictions by year and count them
    predictions_by_year_last_5_years = predictions_last_5_years.annotate(year=Count('created_date__year')).values('year').order_by('year')

    # Create a dictionary to store the yearly increase
    yearly_increase_last_5_years = {}

    # Calculate the increase for each year
    for item in predictions_by_year_last_5_years:
        year = item['year']
        count = item['year']
        yearly_increase_last_5_years[year] = count

    return JsonResponse({'yearly_increase_last_5_years': yearly_increase_last_5_years})





from django.http import JsonResponse
from django.db.models import Count
from .models import Prediction
import datetime

def predictions_in_2024(request):
    # Get the current year
    current_year = datetime.datetime.now().year

    # Filter predictions for the year 2024
    predictions_2024 = Prediction.objects.filter(created_date__year=2024)

    # Group predictions by month and count them
    predictions_by_month = predictions_2024.annotate(month=Count('created_date__month')).values('month')

    # Prepare data for JSON response
    data = {}
    for prediction in predictions_by_month:
        month = prediction['month']
        data[month] = prediction['month']

    return JsonResponse(data)




from django.views.generic import ListView
from django.db.models import Q
from .models import Prediction

class PredictionListView(ListView):
    model = Prediction
    template_name = 'prediction/managePredictions.html'
    context_object_name = 'predictions'
    paginate_by = 5

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Prediction.objects.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(insurance__name__icontains=search_query) |
                Q(available__icontains=search_query) |
                Q(created_date__icontains=search_query)
            )
        return Prediction.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context
