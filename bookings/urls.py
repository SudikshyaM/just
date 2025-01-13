from django.urls import path
from .views import *


urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('list/', ListBookingsView.as_view(), name='list-bookings'),
    path('dashboard/seller/', SellerDashboardView.as_view(), name='seller-dashboard'),
    path('',booking),
]
