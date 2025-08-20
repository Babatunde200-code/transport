from django.db import models
from django.conf import settings
from django.utils import timezone


class TravelPlan(models.Model):
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="travel_plans"
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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="travel_bookings",
        null=True,  # temporarily allow null for migrations
        blank=True
    )
    travel_plan = models.ForeignKey(
        TravelPlan,
        on_delete=models.CASCADE,
        related_name="travel_bookings",
        null=True,  # temporarily allow null for migrations
        blank=True
    )
    seats_booked = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("cancelled", "Cancelled")],
        default="pending"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        passenger_str = self.passenger if self.passenger else "Unknown"
        return f"Booking by {passenger_str} for {self.travel_plan}"
