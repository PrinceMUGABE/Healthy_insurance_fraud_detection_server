from rest_framework import serializers
from .models import Insurance

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model =Insurance
        fields = '__all__'



class InsuranceSerializerData(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['insurance_code', 'name', 'owner', 'created_date']
