import logging
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
from patientApp.models import Client
from patientApp.serializers import ClientSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from patientApp.serializers import ClientSerializer
from patientApp.models import Client
import base64
import base64
import numpy as np
import torch
from PIL import Image
from io import BytesIO
from facenet_pytorch import InceptionResnetV1, MTCNN
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework import status
import os
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
# View to return total available predictions
from django.http import JsonResponse
from .models import Prediction
from django.http import JsonResponse
from .models import Prediction
# View to return institution predictions by status
from django.http import JsonResponse
from django.db.models import Count
from .models import Prediction
from django.http import JsonResponse
from django.db.models import Count
from .models import Prediction


model_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'models')


def total_available_predictions(request):
    total_available = Prediction.objects.all().count()
    total_frauded = Prediction.objects.filter(available=False).count()
    total_valid = Prediction.objects.filter(available=True).count()
    return JsonResponse({'total_available_predictions': total_available, 'total_frauded': total_frauded, 'total_valid': total_valid})



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



@api_view(['GET'])
def display_predictions(request):
    all_predictions = Prediction.objects.all().select_related('insurance')
    serializer = PredictionSerializer(all_predictions, many=True)
    return Response({
        'predictions': serializer.data
    }, status=status.HTTP_200_OK)



import base64
import cv2
import logging
import numpy as np
import face_recognition
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from patientApp.models import Client
from patientApp.serializers import ClientSerializer
from insuranceApp.models import Insurance

# Pre-trained face detector
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def is_high_quality(image):
    height, width = image.shape[:2]
    min_resolution = (200, 200)  # Minimum resolution for a high-quality image
    return width >= min_resolution[0] and height >= min_resolution[1]

def get_image_from_base64(picture_data):
    try:
        # Remove the "data:image/jpeg;base64," part if it exists
        if ',' in picture_data:
            picture_data = picture_data.split(',', 1)[1]
        picture_bytes = base64.b64decode(picture_data)
        submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

        if submitted_image is None:
            message = 'Image data is not valid.'
            logging.error(message)
            return JsonResponse({'error': message}, status=400)

        if not is_high_quality(submitted_image):
            message = 'Image quality is too low. Please submit a higher quality image.'
            logging.error(message)
            return JsonResponse({'error': message}, status=400)

        # Face detection using Haar Cascade Classifier
        faces = face_detector.detectMultiScale(submitted_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            message = 'No faces detected in the image. Please submit a picture with a face.'
            logging.error(message)
            return JsonResponse({'error': message}, status=400)
        elif len(faces) > 1:
            message = 'Multiple faces detected. Please submit a picture with only one person.'
            logging.error(message)
            return JsonResponse({'error': message}, status=400)

        return submitted_image

    except Exception as e:
        logging.error(f"Failed to decode base64 image: {e}")
        return JsonResponse({'error': 'Failed to decode base64 image'}, status=400)

def compare_images_content(submitted_picture, existing_picture):
    try:
        # Convert submitted picture to RGB
        submitted_picture_rgb = cv2.cvtColor(submitted_picture, cv2.COLOR_BGR2RGB)

        # Detect faces in the submitted picture
        submitted_face_locations = face_recognition.face_locations(submitted_picture_rgb)
        if not submitted_face_locations:
            logging.error("No faces found in the submitted picture.")
            return 0.0

        # Encode faces in the submitted picture
        submitted_encodings = face_recognition.face_encodings(submitted_picture_rgb, submitted_face_locations)
        if not submitted_encodings:
            logging.error("Failed to encode faces in the submitted picture.")
            return 0.0

        # Convert existing picture to RGB
        existing_picture_rgb = cv2.cvtColor(existing_picture, cv2.COLOR_BGR2RGB)
        existing_face_locations = face_recognition.face_locations(existing_picture_rgb)
        if not existing_face_locations:
            logging.error("No faces found in existing picture.")
            return 0.0

        # Encode faces in the existing picture
        existing_encodings = face_recognition.face_encodings(existing_picture_rgb, existing_face_locations)
        if not existing_encodings:
            logging.error("Failed to encode faces in existing picture.")
            return 0.0

        # Compare face encodings
        for existing_encoding in existing_encodings:
            results = face_recognition.compare_faces(submitted_encodings, existing_encoding)
            if True in results:
                return 1.0  # High similarity

        return 0.0  # Low similarity

    except Exception as e:
        logging.error(f"Error comparing images: {e}")
        return 0.0

@api_view(['POST'])
def save_prediction(request):
    try:
        data = request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        gender = data.get('gender')
        marital_status = data.get('marital_status')
        insurance_code = data.get('insurance')
        address = data.get('address')
        picture_data = data.get('picture')

        # Fetch the client based on the phone number
        insurance = Insurance.objects.get(insurance_code=insurance_code)
        clients = Client.objects.filter(phone=phone)
        if not clients.exists():
            data = Client.objects.filter(first_name=first_name, last_name=last_name, address=address, insurance=insurance)
          
            # Remove the "data:image/jpeg;base64," part if it exists
            if ',' in picture_data:
                picture_data = picture_data.split(',', 1)[1]
            picture_bytes = base64.b64decode(picture_data)
            submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

            submitted_image = get_image_from_base64(picture_data)
            if isinstance(submitted_image, JsonResponse):
                return submitted_image  # Return error response from get_image_from_base64

            prediction = Prediction(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                gender=gender,
                marital_status=marital_status,
                insurance=insurance,
                address=address,
                picture=client.picture,
                available=False
            )
            prediction.save()

        client = clients.first()

        # Serialize the client data
        serialized_client = ClientSerializer(client).data

        # Compare the submitted data with the existing client data
        comparison_results = {
            'first_name': first_name == client.first_name or first_name == client.last_name,
            'last_name': last_name == client.last_name or last_name == client.first_name,
            'phone': phone == client.phone,
            'gender': gender == client.gender,
            'marital_status': marital_status == client.marital_status,
            'insurance': insurance_code == client.insurance.insurance_code if client.insurance else False,
            'address': address.lower() == client.address.lower() if client.address else False,
        }

        # Convert submitted picture to a readable format
        submitted_picture = get_image_from_base64(picture_data)
        if isinstance(submitted_picture, JsonResponse):
            return submitted_picture  # Return error response from get_image_from_base64

        # Convert stored picture to a readable format
        stored_picture = cv2.imdecode(np.frombuffer(client.picture, np.uint8), cv2.IMREAD_COLOR)
        if stored_picture is None:
            logging.error("Failed to decode stored picture.")
            return Response({'error': 'Failed to decode stored picture'}, status=status.HTTP_400_BAD_REQUEST)

        # Compare picture contents
        picture_match = compare_images_content(submitted_picture, stored_picture)
        comparison_results['picture'] = picture_match

        # Separate matched and mismatched data
        matched_data = {k: v for k, v in comparison_results.items() if v}
        mismatched_data = {k: v for k, v in comparison_results.items() if not v}

        # Determine availability
        available = all(comparison_results.values())
        
        if available:
            # Save the prediction data to the database
            prediction = Prediction(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                gender=gender,
                marital_status=marital_status,
                insurance=client.insurance,  # Use the existing insurance object
                address=address,
                picture=client.picture,
                available=True
            )
            prediction.save()
        else:
            # Save the prediction data to the database
            prediction = Prediction(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                gender=gender,
                marital_status=marital_status,
                insurance=client.insurance,  # Use the existing insurance object
                address=address,
                picture=client.picture,
                available=False
            )
            prediction.save()

        return Response({
            'matched_data': matched_data,
            'mismatched_data': mismatched_data,
            'serialized_client': serialized_client,
        }, status=status.HTTP_200_OK)

        

    except Exception as e:
        logging.error(f"Error during image processing: {e}")
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
