from rest_framework import serializers
from .models import TravelPlan
from .models import Booking

class TravelPlanSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.username", read_only=True)

    class Meta:
        model = TravelPlan
        fields = [
            "id",
            "driver_name",
            "origin",
            "destination",
            "date",
            "time",
            "available_seats",
            "price",
            "car_picture",
        ]



class BookingSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(source="passenger.username", read_only=True)
    travel_plan_details = TravelPlanSerializer(source="travel_plan", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "passenger_name", "travel_plan", "travel_plan_details", "seats_booked", "created_at"]
        extra_kwargs = {"travel_plan": {"write_only": True}}
