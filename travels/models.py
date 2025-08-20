from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class TravelPlan(models.Model):
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="travel_plans"
    )
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    available_seats = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin} → {self.destination} by {self.driver}"


class Booking(models.Model):
    passenger = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="travel_bookings"
    )
    travel_plan = models.ForeignKey(
        TravelPlan, on_delete=models.CASCADE, related_name="travel_bookings"
    )
    seats_booked = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("cancelled", "Cancelled")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.passenger} for {self.travel_plan}"
