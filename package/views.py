from rest_framework import generics, status,serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser,IsAuthenticatedOrReadOnly
from .models import Hotel, Activity, Package, Review
from .serializers import *
from django.contrib.auth.decorators import login_required
from .forms import *
from users.auth import admin_only
from django.shortcuts import render,redirect
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404


# Hotel Views
class HotelListCreateView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated]


# Activity Views
class ActivityListCreateView(generics.ListCreateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]


# Package Views
class PackageListView(generics.ListAPIView):
    queryset = Package.objects.filter(availability=True)
    serializer_class = PackageSerializer
    filter_backends = [SearchFilter,OrderingFilter,DjangoFilterBackend]


class PackageDetailView(generics.RetrieveAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


class CreatePackageView(generics.CreateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAdminUser]


# Review Views
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        package_id = self.kwargs['package_id']
        return Review.objects.filter(package_id=package_id)

    def perform_create(self, serializer):
        package = Package.objects.get(id=self.kwargs['package_id'])
        serializer.save(package=package, user=self.request.user)

@login_required
@admin_only
def index(request):
    #fetch data from the table
    packages=Package.objects.all()
    context={
        'packages':packages
    }
    return render(request,'packages/package.html',context)

@login_required
@admin_only
def post_package(request):
    if request.method=="POST":
        form=PackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Package added successfully.')
            return redirect('/package/addPackage')
        else:
            messages.add_message(request,messages.ERROR,'failed to add Package.')
            return render(request,'/packages/addPackage.html',{'form':form})
    context={
        'form':PackageForm
    }
    return render(request,'packages/addPackage.html',context)

@login_required
@admin_only
def update_package(request,Package_id):
    instance=Package.objects.get(id=Package_id)

    if request.method=="POST":
        form=PackageForm(request.POST, request.FILES,instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Package updated successfully.')
            return redirect('/package/')
        else:
            messages.add_message(request,messages.ERROR,'failed to update Package.')
            return render(request,'/packages/updatePackage.html',{'form':form})
    context={
        'form':PackageForm(instance=instance)
    }
    return render(request,'packages/updatePackage.html',context)

@login_required
@admin_only
def delete_package(request,Package_id):
    package=Package.objects.get(id=Package_id)
    package.delete()
    messages.add_message(request,messages.SUCCESS,'Packages deleted.')
    return redirect('/package')


class PackageReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow read-only for non-authenticated users

    def get_queryset(self):
        package = self.kwargs['package_id']
        return Review.objects.filter(package_id=package)

    def perform_create(self, serializer):
        # package = self.kwargs['package_id']
        package = Package.objects.get(id=self.kwargs['package_id'])
        # Automatically assign the logged-in user to the review and the package
        serializer.save(user=self.request.user, package_id=package)

# class PackageCustomizationView(generics.UpdateAPIView):
#     queryset = Package.objects.all()
#     serializer_class = PackageCustomizationSerializer
#     permission_classes = [IsAuthenticated]  # Make sure user is authenticated to update

#     def update(self, request, *args, **kwargs):
#         # Allow partial updates (only fields that are provided in the request will be updated)
#         return super().update(request, *args, **kwargs)
    
class AvailableHotelsForPackageView(generics.ListAPIView):
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve the package id from the URL and fetch the package
        package_id = self.kwargs['package_id']
        package = Package.objects.get(id=package_id)

        # Return hotels available for this package's location
        return Hotel.objects.filter(location=package.location)
    

class UserCustomizedPackageView(generics.RetrieveUpdateAPIView):
    queryset = UserCustomizedPackage.objects.all()
    serializer_class = UserCustomizedPackageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'package_id'  
    def get_object(self):
        package_id = self.kwargs.get('package_id')
        user = self.request.user

        try:
            # Get the package by ID
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            raise Http404("Package not found")

        # Check if UserCustomizedPackage exists for this user and package
        obj, created = UserCustomizedPackage.objects.get_or_create(
            user=user, package=package,
            defaults={"total_price": package.base_price}
        )

        return obj

    def perform_update(self, serializer):
        # Get the selected hotel ids and activity ids from the request data
        selected_hotel_ids = self.request.data.get('hotels', [])
        selected_activity_ids = self.request.data.get('activities', [])

        # Save the instance first to ensure it has an ID
        serializer.save()

        # Get the package associated with the customized package
        package = serializer.instance.package

        # Filter the available hotels based on the selected IDs (hotel is related to the package)
        available_hotels = Hotel.objects.filter(id__in=selected_hotel_ids)

        # Filter the selected activities based on the package
        available_activities = Activity.objects.filter(id__in=selected_activity_ids)

        # Validate selected activities and hotels
        selected_activities = available_activities.filter(id__in=selected_activity_ids)

        if not available_hotels or not selected_activities:
            return Response({"error": "Invalid hotels or activities selected."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the many-to-many relationships
        serializer.instance.hotels.set(available_hotels)
        serializer.instance.activities.set(selected_activities)

        # Recalculate the total price based on hotels and activities
        hotel_price = sum(hotel.price for hotel in available_hotels)
        activity_price = sum(activity.price for activity in selected_activities)
        serializer.instance.total_price = package.base_price + hotel_price + activity_price

        # Save the final updates
        serializer.instance.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
