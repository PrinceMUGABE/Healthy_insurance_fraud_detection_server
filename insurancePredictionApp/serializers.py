from rest_framework import serializers
from .models import Prediction
from insuranceApp.models import Insurance

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['insurance_code', 'name', 'owner', 'created_date']

# class PredictionSerializer(serializers.ModelSerializer):
#     insurance = InsuranceSerializer()
#     picture = serializers.SerializerMethodField()

#     class Meta:
#         model = Prediction
#         fields = '__all__'

#     def get_picture(self, obj):
#         return obj.picture.tobytes().decode('utf-8') if obj.picture else None
    
    
class PredictionSerializer(serializers.ModelSerializer):
    insurance = InsuranceSerializer() # Serialize the related insurance object

    class Meta:
        model = Prediction
        fields = ['id', 'first_name', 'last_name', 'phone', 'gender' , 'insurance',  'marital_status', 'address', 'picture', 'available', 'created_date']
