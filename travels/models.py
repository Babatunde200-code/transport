from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class TravelPlan(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="travel_plans")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    car_picture = models.ImageField(upload_to="cars/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin} → {self.destination} on {self.date}"

class Booking(models.Model):
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    travel_plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE, related_name="bookings")
    seats_booked = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.username} booked {self.seats_booked} seat(s) on {self.travel_plan}"

    def save(self, *args, **kwargs):
        # Ensure seat availability
        if self.travel_plan.available_seats < self.seats_booked:
            raise ValueError("Not enough seats available")
        # Reduce seats
        self.travel_plan.available_seats -= self.seats_booked
        self.travel_plan.save()
        super().save(*args, **kwargs)
