from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import CustomUser


# Hotel Model
class Hotel(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='hotels',
        limit_choices_to={'role': 'hotel_owner'},
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} - {self.location}"


# Activity Model
class Activity(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='activities',
        limit_choices_to={'role': 'activity_lister'},
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return f"Activity: {self.name} at {self.location}"


# Package Manager
class PackageManager(models.Manager):
    def count_unavailable(self):
        return self.filter(availability=False).count()


# Package Model
class Package(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploads/packages', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True,editable=False)
    base_price = models.FloatField(default=0.0, help_text="Minimum service charge")
    location = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in days")
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Many-to-Many relationships
    hotels = models.ManyToManyField(
        Hotel,
        related_name='packages',
        blank=True
    )
    activities = models.ManyToManyField(
        Activity,
        related_name='packages',
        blank=True
    )

    objects = PackageManager()

    def calculate_price(self):
        # Sum the default prices of hotels and activities
        hotel_price = sum(hotel.price for hotel in self.hotels.all())
        activity_price = sum(activity.price for activity in self.activities.all())
        return self.base_price + hotel_price + activity_price
    
    def save(self, *args, **kwargs):
        if not self.pk:  # For new instances, calculate an initial price
            self.price = self.base_price
        super().save(*args, **kwargs)
       

    def __str__(self):
        return f"Package: {self.name}, Location: {self.location}"
    

class UserCustomizedPackage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customized_packages')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='user_customized_packages')
    hotels = models.JSONField(default=list)  # Storing hotel IDs as a list
    activities = models.JSONField(default=list)  # Storing activity IDs as a list
    total_price = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        # Calculate total price for the customized package without double counting
        base_price = self.package.base_price

        # Fetch the hotels and activities based on their IDs
        hotel_objects = Hotel.objects.filter(id__in=self.hotels)
        activity_objects = Activity.objects.filter(id__in=self.activities)

        # Calculate the price of selected hotels and activities
        hotel_price = sum(hotel.price for hotel in hotel_objects)
        activity_price = sum(activity.price for activity in activity_objects)

        # Update the total price
        self.total_price = base_price + hotel_price + activity_price

        # Call the superclass save method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Customized Package for {self.user.email} - ${self.total_price}"



# Review Model
class Review(models.Model):
    package = models.ForeignKey(Package, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.user.email} for {self.package.name}"
