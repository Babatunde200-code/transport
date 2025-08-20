from rest_framework import serializers
from .models import TravelPlan, Booking


class TravelPlanSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TravelPlan
        fields = [
            "id", "driver", "origin", "destination", 
            "departure_date", "departure_time", 
            "available_seats", "price", "created_at"
        ]


class BookingSerializer(serializers.ModelSerializer):
    passenger = serializers.StringRelatedField(read_only=True)
    travel_plan = TravelPlanSerializer(read_only=True)
    travel_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=TravelPlan.objects.all(), source="travel_plan", write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            "id", "passenger", "travel_plan", "travel_plan_id",
            "seats_booked", "status", "created_at"
        ]
