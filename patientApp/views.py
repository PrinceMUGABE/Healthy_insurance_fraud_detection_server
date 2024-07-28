import traceback
import numpy as np
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from insuranceApp.models import Insurance
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from django.http import JsonResponse
from django.core import serializers
import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

import base64
import os
import random
import string
import traceback
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import Client  # Import your Client model
import numpy as np
import cv2
import face_recognition
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
import cv2
import numpy as np
import random
import string
import os
import traceback
from .models import Client
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
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
import base64
import cv2
import numpy as np
from django.http import JsonResponse
from rest_framework.decorators import api_view
import traceback
from django.core.paginator import Paginator
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Client
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.http import JsonResponse
from patientApp.models import Client

from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.http import JsonResponse
from patientApp.models import Client
import base64

from .serializers import ClientSerializer

@api_view(['GET'])
def display_clients(request):
    clients = Client.objects.all().order_by('id')
    paginator = Paginator(clients, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    serializer = ClientSerializer(page_obj, many=True)

    return Response({
        'clients': serializer.data,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_high_quality(image):
    height, width = image.shape[:2]
    min_resolution = (200, 200)  # Minimum resolution for a high-quality image
    return width >= min_resolution[0] and height >= min_resolution[1]



# Pre-trained face detector
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


@csrf_exempt
@api_view(['POST'])
def save_insurance_member(request):
    try:
        if request.content_type == 'application/json':
            data = request.data
        else:
            data = request.POST

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        gender = data.get('gender')
        marital_status = data.get('marital_status')
        insurance_code = data.get('insurance')  # Changed from insurance_id to insurance_code
        address = data.get('address')
        picture_data = data.get('picture')
        
        print(f'\n\nInsurance submitted: {insurance_code}\n\n')

        if not all([first_name, last_name, phone, gender, marital_status, insurance_code, address, picture_data]):
            message = 'All fields are required.'
            print(message)
            return JsonResponse({'error': message}, status=400)

        try:
            insurance = Insurance.objects.get(insurance_code=insurance_code)
            print(f'\n\n Insurance found in Insurance App: {insurance}\n\n')
        except Insurance.DoesNotExist:
            message = f'Insurance with code {insurance_code} does not exist.'
            print(message)
            return JsonResponse({'error': message}, status=400)

        if picture_data:
            # Remove the "data:image/jpeg;base64," part if it exists
            if ',' in picture_data:
                picture_data = picture_data.split(',', 1)[1]
            picture_bytes = base64.b64decode(picture_data)
            submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

            if not is_high_quality(submitted_image):
                message = 'Image quality is too low. Please submit a higher quality image.'
                print(message)
                return JsonResponse({'error': message}, status=400)

            # Face detection using Haar Cascade Classifier
            faces = face_detector.detectMultiScale(submitted_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 0:
                message = 'No faces detected in the image. Please submit a picture with a face.'
                print(message)
                return JsonResponse({'error': message}, status=400)
            elif len(faces) > 1:
                message = 'Multiple faces detected. Please submit a picture with only one person.'
                print(message)
                return JsonResponse({'error': message}, status=400)
            
            # Example logic to generate client code
            phone_suffix = phone[-3:]
            last_name_prefix = last_name[:2].upper()
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            client_code = f"{phone_suffix}{last_name_prefix}{random_suffix}"

            # Save client data to database
            client = Client.objects.create(
                client_code=client_code,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                gender=gender,
                insurance=insurance,  # Note the correct assignment
                marital_status=marital_status,
                address=address,
                picture=picture_bytes
            )

            message = 'Client saved successfully'
            print(message)
            return JsonResponse({'message': message}, status=201)
        else:
            message = 'No image data received.'
            print(message)
            return JsonResponse({'error': message}, status=400)
    except Exception as e:
        error_message = 'Error during image processing'
        print(f"{error_message}: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': error_message}, status=500)



def extract_face_encodings(image):
    # Load the pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    try:
        # Convert the image data to a numpy array
        nparr = np.frombuffer(image, np.uint8)

        # Decode the image array
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_np is None:
            raise ValueError("Failed to decode image")

        # Convert the image to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        face_encodings = []
        for (x, y, w, h) in faces:
            # Extract the face region from the image
            face_roi = gray[y:y + h, x:x + w]

            # Resize the face region to a fixed size
            face_roi = cv2.resize(face_roi, (128, 128))

            # Calculate the face encoding using a pre-trained face recognition model
            # Here, we're using a dummy encoding for demonstration purposes
            face_encoding = np.random.rand(128)

            face_encodings.append(face_encoding)

        return face_encodings
    except Exception as e:
        print("Error:", e)
        return []

@api_view(['DELETE'])
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()

    return JsonResponse({'message': 'Client Deleted successfully'}, status=status.HTTP_200_OK)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Client, Insurance

def get_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    client_data = {
        'id': client.id,
        'client_code': client.client_code,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'phone': client.phone,
        'gender': client.gender,
        'marital_status': client.marital_status,
        'insurance': {
            'insurance_code': client.insurance.insurance_code,
            'name': client.insurance.name
        } if client.insurance else None,
        'address': client.address,
        'picture': base64.b64encode(client.picture).decode('utf-8') if client.picture else None,
        'created_date': client.created_date
    }
    return JsonResponse(client_data)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import base64
import cv2
import numpy as np
import os
import traceback
from .models import Client
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

@api_view(['PUT'])
def update_client(request, client_id):
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ClientSerializer(client, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_list_or_404
from django.utils.timezone import now
from django.db.models import Count
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import csv

# Function to show the total number of clients
def total_clients(request):
    client_count = Client.objects.count()
    return JsonResponse({'total_clients': client_count})

# Function to show the increase of clients in 2024
def clients_in_2024(request):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    count_2024 = Client.objects.filter(created_date__range=(start_date, end_date)).count()
    return JsonResponse({'clients_in_2024': count_2024})

# Function to show the increase of clients in May
def clients_in_may(request):
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2024, 5, 31)
    count_may = Client.objects.filter(created_date__range=(start_date, end_date)).count()
    return JsonResponse({'clients_in_may': count_may})

# Function to download all clients in PDF
def download_clients_pdf(request):
    clients = Client.objects.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for client in clients:
        pdf.cell(200, 10, txt=str(client), ln=True)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="clients.pdf"'
    response.write(pdf.output(dest='S').encode('latin1'))
    return response

# Function to download all clients in Excel
def download_clients_excel(request):
    clients = Client.objects.all().values()
    df = pd.DataFrame(clients)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="clients.xls"'
    df.to_excel(response, index=False)
    return response

# Function to show new clients of today
def new_clients_today(request):
    today = now().date()
    clients = Client.objects.filter(created_date__date=today)
    serialized_clients = serializers.serialize('json', clients)
    return JsonResponse({'new_clients_today': json.loads(serialized_clients)})

# Function to search clients
def search_clients(request):
    query_params = request.GET
    clients = Client.objects.all()

    if 'firstname' in query_params:
        clients = clients.filter(first_name__icontains=query_params['firstname'])
    if 'lastname' in query_params:
        clients = clients.filter(last_name__icontains=query_params['lastname'])
    if 'phone' in query_params:
        clients = clients.filter(phone__icontains=query_params['phone'])
    if 'client_code' in query_params:
        clients = clients.filter(client_code__icontains=query_params['client_code'])
    if 'gender' in query_params:
        clients = clients.filter(gender=query_params['gender'])
    if 'marital_status' in query_params:
        clients = clients.filter(marital_status=query_params['marital_status'])
    if 'insurance' in query_params:
        clients = clients.filter(insurance__id=query_params['insurance'])
    if 'address' in query_params:
        clients = clients.filter(address__icontains=query_params['address'])
    if 'created_date' in query_params:
        clients = clients.filter(created_date__date=query_params['created_date'])

    serialized_clients = serializers.serialize('json', clients)
    return JsonResponse({'clients': json.loads(serialized_clients)})
