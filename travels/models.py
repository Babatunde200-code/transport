from django.db import models
from accounts.models import CustomUser

# travels/models.py

class TravelPlan(models.Model):
    travel = models.ForeignKey('travels.TravelPlan', on_delete=models.CASCADE, related_name='booking_travel_set')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(TravelPlan, related_name='bookings', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
