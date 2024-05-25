from rest_framework import serializers
from .models import User
from insurancePredictionApp.models import Prediction
from insuranceApp.models import Insurance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = '__all__'
