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



# Display clients as RESTful response
def display_clients(request):
    clients = Client.objects.all()
    serialized_clients = serializers.serialize('json', clients)
    return JsonResponse({'clients': json.loads(serialized_clients)})


# Create a new client page
def get_create_client_page(request):
    insurances = Insurance.objects.all()
    return JsonResponse({'insurances': list(insurances.values())})


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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_high_quality(image):
    height, width = image.shape[:2]
    min_resolution = (200, 200)  # Minimum resolution for a high-quality image
    return width >= min_resolution[0] and height >= min_resolution[1]

def save_insurance_member(request):
    if request.method == 'POST':
        try:
            # Extract form data
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            phone = request.POST.get('phone')
            gender = request.POST.get('gender')
            marital_status = request.POST.get('marital_status')
            insurance_id = request.POST.get('insurance')
            address = request.POST.get('address')
            picture_data = request.POST.get('picture')

            if picture_data:
                # Convert base64 image data to bytes
                picture_bytes = base64.b64decode(picture_data.split(',')[1])

                # Read the submitted image
                submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

                # Check if the image has high enough quality
                if not is_high_quality(submitted_image):
                    messages.error(request, 'Image quality is too low. Please submit a higher quality image')
                    return redirect('create_client')

                # Detect faces in the image using face_recognition library
                face_locations = face_recognition.face_locations(submitted_image)
                if not face_locations:
                    messages.error(request, 'No faces detected in the image. Please submit a picture containing a face.')
                    return redirect('create_client')

                # Generate client code
                phone_suffix = phone[-3:]
                last_name_prefix = last_name[:2].upper()
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
                client_code = f"{phone_suffix}{last_name_prefix}{random_suffix}"

                # Save the picture contents into the database
                client = Client.objects.create(
                    client_code=client_code,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    gender=gender,
                    insurance_id=insurance_id,
                    marital_status=marital_status,
                    address=address,
                    picture=picture_bytes  # Save the picture contents directly
                )

                # Save the picture to the specified folder with client_code as filename
                picture_name = f"{client_code}.jpg"
                picture_path = os.path.join('submitted_pictures', picture_name)

                # Save the picture using FileSystemStorage
                fs = FileSystemStorage(location=os.path.join(BASE_DIR, 'templates', 'static', 'submitted_pictures'))
                filename = fs.save(picture_name, ContentFile(picture_bytes))

                # Get the URL of the saved picture (optional if needed)
                picture_url = fs.url(filename)

                messages.success(request, 'Client saved successfully')
                return JsonResponse({'message': 'Client saved successfully'})
            else:
                print("No image data received.")
                
                return JsonResponse({'Error': 'No image received'})
        except Exception as e:
            print("Error during image processing:", e)
            print(traceback.format_exc())  # Print the stack trace for debugging
            
            return JsonResponse({'Error': 'Error during image processing: {e}'})
    else:
        messages.error(request, 'Failed to submit Information')
        return JsonResponse({'Error': 'failed to submit information'})


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


def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()

    # Create or update the client dataset after deleting a client
    create_or_update_client_dataset()

    # Train or update the model
    # train_or_update_model()

    return JsonResponse({'message': 'Client Deleted successfully'})


def edit_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    insurances = Insurance.objects.all()
    #return render(request, 'client/edit_client.html', {'client': client, 'insurances': insurances})
    return JsonResponse({'insurances': list(insurances.values()), 'client':client})


from django.shortcuts import get_object_or_404, redirect
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import base64
import os
import traceback
import cv2
import numpy as np

def update(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if request.method == 'POST':
        try:
            # Extract form data
            client.client_code = request.POST.get('code')
            client.first_name = request.POST.get('firstname')
            client.last_name = request.POST.get('lastname')
            client.phone = request.POST.get('phone')
            client.gender = request.POST.get('gender')
            client.marital_status = request.POST.get('marital_status')
            client.insurance_id = request.POST.get('insurance')
            client.address = request.POST.get('address')
            picture_data = request.POST.get('picture')

            if picture_data:
                # Convert base64 image data to bytes
                picture_bytes = base64.b64decode(picture_data.split(',')[1])

                # Read the submitted image
                submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

                # Check if the image has high enough quality
                if not is_high_quality(submitted_image):
                    print('Image quality is too low. Please submit a higher quality image')
                    messages.error(request, 'Image quality is too low. Please submit a higher quality image')
                    #return redirect('edit_client', client_id=client_id)
                    return JsonResponse({'error': 'Image quality is too low. Please submit a higher quality image'},client_id=client_id)

                # Save the new picture contents into the database
                client.picture = picture_bytes

                # Save the picture to the specified folder with client_code as filename
                picture_name = f"{client.client_code}.jpg"
                picture_path = os.path.join(BASE_DIR, 'templates', 'static', 'submitted_pictures', picture_name)

                # Check if the file already exists and delete it if it does
                if os.path.exists(picture_path):
                    os.remove(picture_path)

                # Save the picture using FileSystemStorage
                fs = FileSystemStorage(location=os.path.join(BASE_DIR, 'templates', 'static', 'submitted_pictures'))
                filename = fs.save(picture_name, ContentFile(picture_bytes))

                # Get the URL of the saved picture (optional if needed)
                picture_url = fs.url(filename)

            # Save the updated client object
            client.save()
            print('Client updated successfully')
            messages.success(request, 'Client updated successfully')
            return JsonResponse({'message': 'Client updated successfully'})
        except Exception as e:
            print("Error during image processing:", e)
            print(traceback.format_exc())  # Print the stack trace for debugging
            messages.error(request, f'Error during image processing: {e}')
            #return redirect('edit_client', client_id=client_id)
            return JsonResponse({'error': 'Error during image processing'},client_id=client_id)
    else:
        # Handle GET request if needed
        # You might want to render a form template here
        pass











































































def view_client_details(request, client_id):
    client = Client.objects.get(pk=client_id)
    save_client_picture(client_id, client.picture)
    serialized_client = serializers.serialize('json', [client, ])
    return JsonResponse({'client': json.loads(serialized_client)})






def save_client_picture(client_id, picture_data):
    picture_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'retrieved_pictures')
    picture_path = os.path.join(picture_folder, f"{client_id}.jpg")  # Assuming the pictures are JPEG format

    # Create the directory if it doesn't exist
    if not os.path.exists(picture_folder):
        os.makedirs(picture_folder)

        # Decode base64 image data
    image_data = base64.b64decode(picture_data)

    with open(picture_path, 'wb') as f:
        f.write(image_data)
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer


import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
def prepare_dataset(dataset, save_config=True, config_file='preprocessing_config.pkl'):
    # Drop duplicates and rows with missing values
    dataset = dataset.drop_duplicates()
    dataset = dataset.dropna()

    # Initialize TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # TF-IDF Vectorization for first name
    first_name_tfidf = tfidf_vectorizer.fit_transform(dataset['first_name'])
    first_name_df = pd.DataFrame(first_name_tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

    # TF-IDF Vectorization for last name
    last_name_tfidf = tfidf_vectorizer.fit_transform(dataset['last_name'])
    last_name_df = pd.DataFrame(last_name_tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

    # TF-IDF Vectorization for address
    address_tfidf = tfidf_vectorizer.fit_transform(dataset['address'])
    address_df = pd.DataFrame(address_tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

    # Combine numerical features
    X = pd.concat([first_name_df, last_name_df, address_df], axis=1)

    # Encode categorical variables (gender and marital_status)
    dataset['gender'] = dataset['gender'].map({'male': 0, 'female': 1, 'other': 2})
    dataset['marital_status'] = dataset['marital_status'].map(
        {'single': 0, 'married': 1, 'divorced': 2, 'widowed': 3, 'separated': 4})

    # Include insurance_id as a categorical variable
    X = pd.concat([X, pd.get_dummies(dataset['insurance_id'])], axis=1)

    # Include picture data as a feature (assuming it's already preprocessed as needed)
    picture_features = dataset['picture'].apply(lambda x: preprocess_picture(x))
    picture_df = pd.DataFrame(picture_features, columns=['picture_feature'])
    X = pd.concat([X, picture_df], axis=1)

    # Define target variable (availability) and client code
    y = dataset['availability']
    client_code = dataset['client_code']

    # Define the path where preprocessing_config.pkl should be saved
    config_path = os.path.join('templates', 'static', 'models', config_file)

    print("\n\nNumber of features in X: \n\n", X.shape[1])

    # Save configurations
    if save_config:
        config = {
            'tfidf_vectorizer': tfidf_vectorizer
            # Add more configurations here if needed
        }
        with open(config_path, 'wb') as f:
            pickle.dump(config, f)

    return X, y, client_code

import cv2
import numpy as np
import base64

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def preprocess_picture(picture_data):
    # Debugging: Print the length of the picture data
    print("Length of picture data:", len(picture_data))

    # Convert the base64 image data to bytes
    nparr = np.frombuffer(base64.b64decode(picture_data), np.uint8)

    # Debugging: Print the length of the decoded bytes
    print("Length of decoded bytes:", len(nparr))

    # Decode the image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Debugging: Check if the image is empty
    if image is None:
        print("Image is empty!")
        return False  # Return False if the image is empty

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # If a face is detected, return True
        return True
    else:
        # If no face is detected, return False
        return False
def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model
def create_or_update_client_dataset():
    # Retrieve all clients from the database
    clients = Client.objects.all()

    # If no clients are found, return early
    if not clients:
        return

    # Serialize clients data
    client_data_list = []
    for client in clients:
        client_data = {
            'client_code': client.client_code,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'phone': client.phone,
            'gender': client.gender,
            'marital_status': client.marital_status,
            'insurance_id': client.insurance_id,
            'address': client.address,
            'picture': client.picture,
            'availability': 1  # Default availability value
        }
        client_data_list.append(client_data)

    # Convert the data to a DataFrame
    dataset = pd.DataFrame(client_data_list)

    # Define the folder where the dataset file will be saved
    dataset_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'datasets')
    os.makedirs(dataset_folder, exist_ok=True)

    # Define the file path for the dataset file
    dataset_file_path = os.path.join(dataset_folder, 'client_dataset.csv')

    # Save the dataset to a CSV file
    save_dataset(dataset, 'client_dataset.csv')
def load_dataset(dataset_file):
    dataset_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'datasets')
    dataset_file_path = os.path.join(dataset_folder, dataset_file)
    return pd.read_csv(dataset_file_path)
def save_dataset(dataset, dataset_file):
    dataset_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'datasets')
    dataset_file_path = os.path.join(dataset_folder, dataset_file)
    dataset.to_csv(dataset_file_path, index=False)

def train_or_update_model():
    # Load dataset
    dataset_file = 'client_dataset.csv'  # Specify the dataset file name
    dataset = load_dataset(dataset_file)

    # Prepare dataset for training
    X, y, client_code = prepare_dataset(dataset)

    # Debugging: Print the shapes of input arrays
    print("Shape of X:", X.shape)
    print("Shape of y:", y.shape)

    # If dataset is too small, log a warning and return
    if len(dataset) < 5:  # Adjust the threshold as needed
        print("Dataset has too few samples to split. Please collect more data.")
        return

    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Debugging: Print the shapes of training and testing sets
    print("Shape of X_train:", X_train.shape)
    print("Shape of X_test:", X_test.shape)
    print("Shape of y_train:", y_train.shape)
    print("Shape of y_test:", y_test.shape)

    # Train model
    model = train_model(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

    # Save model
    model_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'models')
    model_file_path = os.path.join(model_folder, 'trained_model.joblib')
    joblib.dump(model, model_file_path)









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
