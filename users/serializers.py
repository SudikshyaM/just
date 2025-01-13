from rest_framework import serializers
from users.models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)

    class Meta:
        model = CustomUser
        fields = ['username','email', 'password','role']

    def create(self, validated_data):
        password=validated_data.pop('password',None)
        role = validated_data.get('role', 'user')
        user = CustomUser.objects.create_user(**validated_data, password=password) 
        if role == 'user':
            user.is_approved='approved'
            user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)