from django.urls import path
from .views import *

urlpatterns = [
    path('hotels/', HotelListCreateView.as_view(), name='hotel-list-create'),
    path('activities/', ActivityListCreateView.as_view(), name='activity-list-create'),
    path('packages/', PackageListView.as_view(), name='package-list'),
    path('packages/<int:pk>/', PackageDetailView.as_view(), name='package-detail'),
    path('packages/create/', CreatePackageView.as_view(), name='create-package'),
    path('packages/<int:package_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('',index),
    path('addPackage/',post_package),
    path('updatepackage/<int:Package_id>',update_package),
    path('deletepackage/<int:Package_id>',delete_package),
    path('packages/<int:package_id>/reviews/', PackageReviewListCreateView.as_view(), name='package-review-list-create'),
    
    path('customize-package/<int:package_id>/', UserCustomizedPackageView.as_view(), name='customize-package'),
    path('packages/<int:package_id>/available-hotels/',AvailableHotelsForPackageView.as_view())
]
