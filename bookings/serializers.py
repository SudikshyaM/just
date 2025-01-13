from rest_framework import serializers
from .models import Booking
from package.models import Hotel

class BookingSerializer(serializers.ModelSerializer):
    # hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    class Meta:
        model = Booking
        fields = ['id', 'user', 'package', 'full_name', 'phone_number', 'additional_notes', 'status', 'booking_date']
        read_only_fields = ['id', 'user', 'status']

