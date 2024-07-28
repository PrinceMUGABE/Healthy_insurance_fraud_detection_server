# clientApp/serializers.py
from rest_framework import serializers
from .models import Client
from insuranceApp.serializers import InsuranceSerializerData

class ClientSerializer(serializers.ModelSerializer):
    insurance = InsuranceSerializerData()  # Serialize the related insurance object

    class Meta:
        model = Client
        fields = ['id', 'client_code', 'first_name', 'last_name', 'phone', 'gender' , 'insurance',  'marital_status', 'address', 'picture', 'created_date']
