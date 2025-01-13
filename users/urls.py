from django.urls import path
from .views import *
urlpatterns = [
    path('register/',signup,name="register"),
    path('login/',login,name="login"),
    
]

