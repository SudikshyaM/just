from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from users.models import CustomUser
# from users.auth import admin_only
from package.models import * 
from bookings.models import Booking
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import LoginForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework import status
from .serializers import AdminLoginSerializer,UserSerializer
from bookings.serializers import BookingSerializer
from package.serializers import PackageSerializer

class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = CustomUser.objects.get(email=email,role='admin') 
            except CustomUser.DoesNotExist:
                return Response({'error': 'Invalid email credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
            if user.check_password(password):  
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message':"login successful",
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                })
            else:
                # Incorrect password case
                return Response({'error': 'Invalid password credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


def login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('/adminspage/dashboard')
            else:
                messages.error(request, 'Please provide valid credentials')
    else:
        form = LoginForm() 

    return render(request, 'admins/login.html', {'form': form})

def logout_user(request):
    logout(request)
    context={
        'form':LoginForm
    }
    return render(request,'admins/login.html',context)

permission_classes=[IsAdminUser]
def dashboard(request):
    package_count = Package.objects.count()
    user_count = CustomUser.objects.count()
    superuser_count = CustomUser.objects.filter(is_superuser=True).count()
    review_count = Review.objects.count()
    booking_count = Booking.objects.count()
    deactivated_user_count = CustomUser.objects.filter(is_active=False).count()
    unavailable_count = Package.objects.count_unavailable()


    context = {
        'package_count': package_count,
        'user_count': user_count,
        'review_count': review_count,
        'superuser_count': superuser_count,
        'booking_count': booking_count,
        'deactivated_user_count': deactivated_user_count,
        'unavailable_count':unavailable_count,
    }
    
    return render(request, 'admins/dashboard.html', context)

@login_required
def get_superuser_info(request):
    user = request.user
    if user.is_superuser:
        name = user.username  
        email = user.email
        context= {
            'name': name,
            'email': email
        }
        return render(request,'admins/layout.html',context)
    else:
        return None  
    
def packages(request):
    pass

def test_view(request):
    review_count = Review.objects.count()
    return render(request, 'admins/test.html', {'review_count': review_count})



