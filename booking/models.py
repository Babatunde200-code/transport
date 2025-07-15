from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_requests')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)  # newly added field
    travel_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
