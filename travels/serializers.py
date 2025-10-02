from rest_framework import serializers


class TravelPlanSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)   # MongoDB ObjectId
    driver_id = serializers.CharField(read_only=True)

    from_location = serializers.CharField()
    to_location = serializers.CharField()
    date = serializers.CharField()  # store as string or ISO datetime
    price = serializers.FloatField()
    seats = serializers.IntegerField()
    available_seats = serializers.IntegerField()
    booked_seats = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )


class BookingSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    passenger_id = serializers.CharField(read_only=True)
    travel_plan_id = serializers.CharField(read_only=True)

    seat_number = serializers.IntegerField()
    booked_at = serializers.DateTimeField(read_only=True)

class RideSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    origin = serializers.CharField()
    destination = serializers.CharField()
    departure_time = serializers.CharField()
    price = serializers.FloatField()
    available_seats = serializers.IntegerField()

class BookingSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField()
    ride_id = serializers.CharField()
    seat_count = serializers.IntegerField()
    total_price = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
