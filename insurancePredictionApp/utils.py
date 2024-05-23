import base64
import os
import cv2
import numpy as np
import joblib
import pickle
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Define the path to the preprocessing config file
preprocessing_config_file = os.path.join(settings.BASE_DIR, 'templates', 'static', 'models', 'preprocessing_config.pkl')


def preprocess_picture(picture_data):
    # Convert the base64 image data to bytes
    nparr = np.frombuffer(base64.b64decode(picture_data), np.uint8)
    # Decode the image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Check if the image is empty
    if image is None:
        return False
    # Detect faces in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        return True
    else:
        return False


def preprocess_input_data(input_data):
    # Load TF-IDF vectorizer from the saved configuration
    with open(preprocessing_config_file, 'rb') as f:
        config = pickle.load(f)
    tfidf_vectorizer = config['tfidf_vectorizer']

    # Preprocess text data (first_name, last_name, address)
    text_data = " ".join([input_data['first_name'], input_data['last_name'], input_data['address']])
    # Transform text data using the loaded TF-IDF vectorizer
    text_data_tfidf = tfidf_vectorizer.transform([text_data]).toarray()  # Convert to dense array

    # Encode categorical variables (gender and marital_status)
    gender_encoded = {'male': 0, 'female': 1, 'other': 2}.get(input_data['gender'], 2)  # Default to 'other' if not recognized
    marital_status_encoded = {'single': 0, 'married': 1, 'divorced': 2, 'widowed': 3, 'separated': 4}.get(input_data['marital_status'], 0)  # Default to 'single' if not recognized

    # Combine features into a single array-like object
    features = [
        *text_data_tfidf.flatten(),  # Flatten and add TF-IDF features
        gender_encoded,
        marital_status_encoded
    ]

    # Ensure the length of the feature vector matches the expected length
    if len(features) != 4:
        raise ValueError(f"Expected 4 features, but found {len(features)} features.")

    return features


def load_model(model_file_name):
    model_folder = os.path.join(settings.BASE_DIR, 'templates', 'static', 'models')
    model_file_path = os.path.join(model_folder, model_file_name)
    return joblib.load(model_file_path)


def make_prediction(prediction_data):
    # Load the trained model
    loaded_model = load_model('trained_model.joblib')
    # Preprocess input data
    features = preprocess_input_data(prediction_data)
    # Make prediction
    prediction_result = loaded_model.predict([features])
    return prediction_result

