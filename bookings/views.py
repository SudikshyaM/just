from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Booking
from .serializers import BookingSerializer
from package.models import Package, Hotel, Activity
from users.auth import admin_only
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user

        # Ensure the package exists
        package_id = data.get('package')
        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({'error': 'Package does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the first hotel from the package's associated hotels (if there are multiple hotels, you may need to adjust this logic)
        # hotels = package.hotels.all()
        # print(hotels)
        # if not hotels:
        #     return Response({'error': 'No hotels associated with this package'}, status=status.HTTP_400_BAD_REQUEST)
        
        # hotel=hotels.first()
        # print(hotel.id)
        # Create the booking
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user, package=package)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class SellerDashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         seller = request.user

#         # Retrieve hotels and activities owned by the seller
#         seller_hotels = Hotel.objects.filter(owner=seller)
#         # seller_activities = Activity.objects.filter(owner=seller)

#         # Retrieve packages that include these hotels or activities
#         packages_with_seller_hotels = Package.objects.filter(hotels__in=seller_hotels)
#         # packages_with_seller_activities = Package.objects.filter(activities__in=seller_activities)

#         # Combine packages and ensure uniqueness
#         related_packages = packages_with_seller_hotels | packages_with_seller_activities

#         # Retrieve bookings for these packages
#         bookings = Booking.objects.filter(package__in=related_packages).select_related('user', 'package')

#         # Serialize data
#         data = []
#         for booking in bookings:
#             data.append({
#                 'package_name': booking.package.name,
#                 'user_full_name': booking.full_name,
#                 'user_phone_number': booking.phone_number,
#                 'booking_date': booking.booking_date,
#                 'hotel_names': [hotel.name for hotel in booking.package.hotels.filter(owner=seller)],
#                 'activity_names': [activity.name for activity in booking.package.activities.filter(owner=seller)],
#             })

#         return Response(data, status=status.HTTP_200_OK)
    

@login_required
@admin_only
def booking(request):
    items=Booking.objects.all()
    for item in items:
        package = item.package
        hotels = package.hotels.all() 
        activities = package.activities.all() 
    context={
        'items':items,
        'hotels':hotels,
        'activities':activities,
    }
    return render(request,'bookings/bookings.html',context)

class SellerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seller = request.user.id

        # Check if the seller is a hotel owner
        seller_hotels = Hotel.objects.filter(owner=seller)
        is_hotel_owner = seller_hotels.exists()

        # Check if the seller is an activity lister
        seller_activities = Activity.objects.filter(owner=seller)
        is_activity_lister = seller_activities.exists()

        # Restrict sellers to one role (hotel owner or activity lister)
        if is_hotel_owner and is_activity_lister:
            return Response(
                {"detail": "Sellers can only own hotels or list activities, not both."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prefetch relevant data based on the seller's role
        if is_hotel_owner:
            # Fetch bookings related to hotels owned by the seller
            related_packages = Package.objects.filter(hotels__in=seller_hotels).distinct()
            bookings = Booking.objects.filter(package__in=related_packages).select_related('user', 'package')

            data = [
                {
                    'package_name': booking.package.name,
                    'user_full_name': booking.full_name,
                    'user_phone_number': booking.phone_number,
                    'booking_date': booking.booking_date,
                    'hotel_names': [hotel.name for hotel in booking.package.hotels.filter(owner=seller)],
                    'activity_names': [],  # Empty as the seller is not an activity lister
                }
                for booking in bookings
            ]
        
        elif is_activity_lister:
            # Fetch bookings related to activities listed by the seller
            related_packages = Package.objects.filter(activities__in=seller_activities).distinct()
            bookings = Booking.objects.filter(package__in=related_packages).select_related('user', 'package')

            data = [
                {
                    'package_name': booking.package.name,
                    'user_full_name': booking.full_name,
                    'user_phone_number': booking.phone_number,
                    'booking_date': booking.booking_date,
                    'hotel_names': [],  # Empty as the seller is not a hotel owner
                    'activity_names': [activity.name for activity in booking.package.activities.filter(owner=seller)],
                }
                for booking in bookings
            ]
        
        else:
            # If the seller owns neither hotels nor activities
            return Response(
                {"detail": "No data available. You must own hotels or list activities to see bookings."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(data, status=status.HTTP_200_OK)
