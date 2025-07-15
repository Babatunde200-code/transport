from django.db import models
from django.conf import settings
from travels.models import TravelPlan

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    travel = models.ForeignKey(TravelPlan, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reviewer', 'travel']  # Prevent duplicate reviews

    def __str__(self):
        return f"{self.reviewer.email} - {self.travel} - {self.rating}"
