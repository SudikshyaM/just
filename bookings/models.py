from django.db import models
from django.conf import settings  # Import settings to use AUTH_USER_MODEL
from package.models import Package,Hotel  # Ensure Package model is correctly imported

class Booking(models.Model):
    STATUS = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ]
     
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'user'})
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, default='')
    phone_number = models.CharField(max_length=20, default='')
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50,choices=STATUS, default='Pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings',null=True)


    def __str__(self):
        return f"{self.user.username} - {self.package.name} - {self.status}"
