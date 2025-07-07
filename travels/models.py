from django.db import models
from django.conf import settings

class Travel(models.Model):
    TRANSPORT_CHOICES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('van', 'Van'),
    ]

    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='travels')
    origin_country = models.CharField(max_length=50)
    origin_city = models.CharField(max_length=50)
    destination_country = models.CharField(max_length=50)
    destination_city = models.CharField(max_length=50)
    departure_date = models.DateField()
    transport_type = models.CharField(max_length=10, choices=TRANSPORT_CHOICES)
    available_seats = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver.email} - {self.origin_city} to {self.destination_city}"
