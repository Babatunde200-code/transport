from rest_framework import serializers
from .models import TravelPlan
from travels.models import Booking

# travels/serializers.py

class TravelPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelPlan
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

