from rest_framework import serializers
from .models import Hotel, Activity, Package, Review,UserCustomizedPackage


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    hotels = HotelSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = '__all__'


# class ReviewSerializer(serializers.ModelSerializer):
#     package = serializers.StringRelatedField(read_only=True) 
#     # email = serializers.EmailField(source='user.email', read_only=True)

#     class Meta:
#         model = Review
#         fields = '__all__'
#         read_only_fields = ['user']

class ReviewSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = Review
        fields ='__all__'  # Only rating and comment will be submitted by the user
        read_only_fields = ['user','package']
        extra_kwargs = {'rating': {'required': True}, 'comment': {'required': True}}
    

class UserCustomizedPackageSerializer(serializers.ModelSerializer):
    hotels = HotelSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = UserCustomizedPackage
        fields = ['user', 'package', 'hotels', 'activities', 'total_price']