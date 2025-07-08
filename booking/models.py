from django.db import models
from django.conf import settings
from travels.models import Travel

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    driver_status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    driver_status = models.CharField(max_length=10, choices=driver_status_choices, default='pending')
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE, related_name='bookings')
    seats_booked = models.PositiveIntegerField()
    booking_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.email} - {self.travel} - {self.seats_booked} seats"
